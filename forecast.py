from __future__ import annotations

import numpy as np
import pandas as pd


def _cluster_baseline_assortment(
    baseline_assortment: pd.DataFrame,
    clustered_stores: pd.DataFrame,
) -> pd.DataFrame:
    merged = baseline_assortment.merge(clustered_stores[["store_id", "cluster_id"]], on="store_id", how="left")
    cluster_base = (
        merged.groupby(["cluster_id", "sku_id"], as_index=False)
        .agg(
            listed_share=("is_listed", "mean"),
            baseline_facings=("facings", "mean"),
        )
    )
    cluster_base["baseline_listed"] = (cluster_base["listed_share"] >= 0.5).astype(int)
    cluster_base["baseline_facings"] = np.where(
        cluster_base["baseline_listed"] == 1,
        np.maximum(cluster_base["baseline_facings"].round().astype(int), 1),
        0,
    )
    return cluster_base[["cluster_id", "sku_id", "baseline_listed", "baseline_facings"]]


def build_sku_metrics_by_cluster(
    transactions: pd.DataFrame,
    products: pd.DataFrame,
    clustered_stores: pd.DataFrame,
    inventory_daily: pd.DataFrame,
    baseline_assortment: pd.DataFrame,
    halo_scores: pd.DataFrame,
) -> pd.DataFrame:
    tx = transactions.merge(clustered_stores[["store_id", "cluster_id"]], on="store_id", how="left")
    cluster_meta = clustered_stores[
        ["cluster_id", "cluster_name", "cluster_english", "cluster_rule_focus"]
    ].drop_duplicates()
    tx = tx.merge(
        products[
            [
                "sku_id",
                "category",
                "brand",
                "size",
                "format",
                "pack_tier",
                "price_tier",
                "unit_cost",
                "shelf_width_cm",
                "is_kvi",
                "is_core",
                "is_private_label",
                "need_state_id",
                "coverage_group_id",
            ]
        ],
        on="sku_id",
        how="left",
    )
    tx["sales"] = tx["qty"] * tx["price"]
    tx["gp"] = tx["qty"] * (tx["price"] - tx["unit_cost"])
    diaper_tx = tx[tx["category"] == "diaper"].copy()
    weeks = max(diaper_tx["date"].nunique() / 7.0, 1.0)
    agg = (
        diaper_tx.groupby(
            [
                "cluster_id",
                "sku_id",
                "brand",
                "size",
                "format",
                "pack_tier",
                "price_tier",
                "shelf_width_cm",
                "is_kvi",
                "is_core",
                "is_private_label",
                "need_state_id",
                "coverage_group_id",
            ],
            as_index=False,
        )
        .agg(
            units=("qty", "sum"),
            sales=("sales", "sum"),
            gp=("gp", "sum"),
            promo_units=("qty", lambda x: x[diaper_tx.loc[x.index, "promo_flag"] == 1].sum()),
            non_promo_units=("qty", lambda x: x[diaper_tx.loc[x.index, "promo_flag"] == 0].sum()),
            basket_count=("basket_id", "nunique"),
        )
    )
    agg["weekly_units"] = agg["units"] / weeks
    agg["weekly_sales"] = agg["sales"] / weeks
    agg["weekly_gp"] = agg["gp"] / weeks
    agg["avg_price"] = agg["sales"] / agg["units"].replace(0, np.nan)
    agg["avg_price"] = agg["avg_price"].fillna(0.0)
    agg["unit_margin"] = agg["gp"] / agg["units"].replace(0, np.nan)
    agg["unit_margin"] = agg["unit_margin"].fillna(0.0)
    agg["margin_rate"] = agg["gp"] / agg["sales"].replace(0, np.nan)
    agg["margin_rate"] = agg["margin_rate"].fillna(0.0)
    agg["gp_per_cm"] = agg["weekly_gp"] / agg["shelf_width_cm"].replace(0, np.nan)
    agg["gp_per_cm"] = agg["gp_per_cm"].fillna(0.0)
    agg["promo_share"] = agg["promo_units"] / agg["units"].replace(0, np.nan)
    agg["promo_share"] = agg["promo_share"].fillna(0.0)
    agg["promo_dependency_score"] = agg["promo_units"] / (agg["promo_units"] + 1.5 * agg["non_promo_units"] + 1e-9)

    inv = inventory_daily.merge(clustered_stores[["store_id", "cluster_id"]], on="store_id", how="left")
    inv_cluster = inv.groupby(["cluster_id", "sku_id"], as_index=False).agg(
        avg_on_hand=("on_hand", "mean"),
        oos_rate=("oos_flag", "mean"),
    )
    agg = agg.merge(inv_cluster, on=["cluster_id", "sku_id"], how="left")
    agg["avg_on_hand"] = agg["avg_on_hand"].fillna(0.0)
    agg["oos_rate"] = agg["oos_rate"].fillna(0.0)
    agg["turnover"] = agg["units"] / agg["avg_on_hand"].replace(0, np.nan)
    agg["turnover"] = agg["turnover"].fillna(0.0)

    cluster_base = _cluster_baseline_assortment(baseline_assortment, clustered_stores)
    agg = agg.merge(cluster_base, on=["cluster_id", "sku_id"], how="left")
    agg["baseline_listed"] = agg["baseline_listed"].fillna(0).astype(int)
    agg["baseline_facings"] = agg["baseline_facings"].fillna(0).astype(int)

    agg = agg.merge(halo_scores, on=["cluster_id", "sku_id"], how="left")
    agg["halo_gp"] = agg["halo_gp"].fillna(0.0)
    agg["halo_support"] = agg["halo_support"].fillna(0.0)
    agg["halo_lift"] = agg["halo_lift"].fillna(0.0)

    ref_price = (
        agg.groupby(["cluster_id", "size", "format"], as_index=False)["avg_price"]
        .mean()
        .rename(columns={"avg_price": "cluster_ref_price"})
    )
    agg = agg.merge(ref_price, on=["cluster_id", "size", "format"], how="left")
    agg["price_index"] = agg["avg_price"] / agg["cluster_ref_price"].replace(0, np.nan)
    agg["price_index"] = agg["price_index"].fillna(1.0)

    diaper_tx["date"] = pd.to_datetime(diaper_tx["date"])
    split_date = diaper_tx["date"].min() + (diaper_tx["date"].max() - diaper_tx["date"].min()) / 2
    diaper_tx["period"] = np.where(diaper_tx["date"] <= split_date, "early", "late")

    format_share = (
        diaper_tx.groupby(["cluster_id", "period", "format"], as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "format_units"})
    )
    format_share["format_share"] = format_share["format_units"] / format_share.groupby(["cluster_id", "period"])["format_units"].transform("sum")
    format_pivot = (
        format_share.pivot_table(index=["cluster_id", "format"], columns="period", values="format_share", fill_value=0.0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    format_pivot["format_trend"] = format_pivot.get("late", 0.0) - format_pivot.get("early", 0.0)
    agg = agg.merge(format_pivot[["cluster_id", "format", "format_trend"]], on=["cluster_id", "format"], how="left")
    agg["format_trend"] = agg["format_trend"].fillna(0.0)

    pack_share = (
        diaper_tx.groupby(["cluster_id", "period", "pack_tier"], as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "pack_units"})
    )
    pack_share["pack_share"] = pack_share["pack_units"] / pack_share.groupby(["cluster_id", "period"])["pack_units"].transform("sum")
    pack_pivot = (
        pack_share.pivot_table(index=["cluster_id", "pack_tier"], columns="period", values="pack_share", fill_value=0.0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    pack_pivot["pack_tier_gap"] = pack_pivot.get("late", 0.0) - pack_pivot.get("early", 0.0)
    agg = agg.merge(pack_pivot[["cluster_id", "pack_tier", "pack_tier_gap"]], on=["cluster_id", "pack_tier"], how="left")
    agg["pack_tier_gap"] = agg["pack_tier_gap"].fillna(0.0)

    base_multiplier = 1.0 + 0.9 * agg["format_trend"] + 0.6 * agg["pack_tier_gap"]
    oos_drag = 1.0 - 0.35 * agg["oos_rate"]
    promo_drag = 1.0 - 0.25 * agg["promo_dependency_score"]
    agg["pred_units"] = agg["weekly_units"] * base_multiplier * oos_drag * promo_drag
    agg["pred_units"] = agg["pred_units"].clip(lower=0.2)
    agg["pred_direct_gp"] = agg["pred_units"] * agg["unit_margin"]
    agg["osa_risk_base"] = (
        agg["weekly_units"] / (agg["avg_on_hand"] + 1.0) * (1.0 + agg["oos_rate"])
    ).clip(lower=0.0)

    agg["velocity_pct"] = agg.groupby("cluster_id")["weekly_units"].rank(pct=True, method="average")
    agg["margin_pct"] = agg.groupby("cluster_id")["margin_rate"].rank(pct=True, method="average")
    agg["space_efficiency_pct"] = agg.groupby("cluster_id")["gp_per_cm"].rank(pct=True, method="average")
    agg["halo_pct"] = agg.groupby("cluster_id")["halo_gp"].rank(pct=True, method="average")
    agg["duplicate_count"] = agg.groupby(["cluster_id", "need_state_id"])["sku_id"].transform("count")
    brand_units = agg.groupby(["cluster_id", "brand"], as_index=False)["weekly_units"].sum()
    brand_units["brand_rank_in_cluster"] = brand_units.groupby("cluster_id")["weekly_units"].rank(
        method="dense", ascending=False
    )
    agg = agg.merge(
        brand_units[["cluster_id", "brand", "brand_rank_in_cluster"]],
        on=["cluster_id", "brand"],
        how="left",
    )
    agg = agg.merge(cluster_meta, on="cluster_id", how="left")

    keep_cols = [
        "cluster_id",
        "cluster_name",
        "cluster_english",
        "cluster_rule_focus",
        "sku_id",
        "brand",
        "size",
        "format",
        "pack_tier",
        "price_tier",
        "shelf_width_cm",
        "is_kvi",
        "is_core",
        "is_private_label",
        "need_state_id",
        "coverage_group_id",
        "weekly_units",
        "weekly_sales",
        "weekly_gp",
        "avg_price",
        "unit_margin",
        "margin_rate",
        "gp_per_cm",
        "avg_on_hand",
        "oos_rate",
        "turnover",
        "price_index",
        "promo_share",
        "promo_dependency_score",
        "promo_units",
        "non_promo_units",
        "halo_gp",
        "halo_support",
        "halo_lift",
        "format_trend",
        "pack_tier_gap",
        "pred_units",
        "pred_direct_gp",
        "osa_risk_base",
        "velocity_pct",
        "margin_pct",
        "space_efficiency_pct",
        "halo_pct",
        "duplicate_count",
        "brand_rank_in_cluster",
        "baseline_listed",
        "baseline_facings",
    ]
    return agg[keep_cols].sort_values(["cluster_id", "pred_direct_gp"], ascending=[True, False]).reset_index(drop=True)
