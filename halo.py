from __future__ import annotations

import pandas as pd


def build_halo_rules(
    transactions: pd.DataFrame,
    products: pd.DataFrame,
    clustered_stores: pd.DataFrame,
) -> pd.DataFrame:
    tx = transactions.merge(clustered_stores[["store_id", "cluster_id"]], on="store_id", how="left")
    tx = tx.merge(products[["sku_id", "category", "brand", "unit_cost"]], on="sku_id", how="left")
    tx["gp"] = tx["qty"] * (tx["price"] - tx["unit_cost"])
    basket_level = (
        tx.groupby(["cluster_id", "basket_id"], as_index=False)
        .agg(
            diaper_skus=("sku_id", lambda x: sorted(set(tx.loc[x.index][tx.loc[x.index, "category"] == "diaper"]["sku_id"]))),
            accessory_skus=("sku_id", lambda x: sorted(set(tx.loc[x.index][tx.loc[x.index, "category"] != "diaper"]["sku_id"]))),
        )
    )
    accessory_gp = (
        tx[tx["category"] != "diaper"]
        .groupby(["cluster_id", "sku_id"], as_index=False)["gp"]
        .mean()
        .rename(columns={"sku_id": "target_sku_id", "gp": "avg_target_gp"})
    )
    rows: list[dict[str, object]] = []
    for cluster_id, baskets in basket_level.groupby("cluster_id"):
        total_baskets = len(baskets)
        diaper_basket_count: dict[str, int] = {}
        accessory_basket_count: dict[str, int] = {}
        pair_count: dict[tuple[str, str], int] = {}
        for basket in baskets.itertuples():
            for source in basket.diaper_skus:
                diaper_basket_count[source] = diaper_basket_count.get(source, 0) + 1
            for target in basket.accessory_skus:
                accessory_basket_count[target] = accessory_basket_count.get(target, 0) + 1
            for source in basket.diaper_skus:
                for target in basket.accessory_skus:
                    pair = (source, target)
                    pair_count[pair] = pair_count.get(pair, 0) + 1

        for (source_sku_id, target_sku_id), count in pair_count.items():
            support = count / max(total_baskets, 1)
            confidence = count / max(diaper_basket_count[source_sku_id], 1)
            target_support = accessory_basket_count[target_sku_id] / max(total_baskets, 1)
            lift = confidence / max(target_support, 1e-9)
            rows.append(
                {
                    "cluster_id": cluster_id,
                    "source_sku_id": source_sku_id,
                    "target_sku_id": target_sku_id,
                    "support": round(float(support), 6),
                    "confidence": round(float(confidence), 6),
                    "lift": round(float(lift), 6),
                }
            )
    halo_rules = pd.DataFrame(rows)
    if halo_rules.empty:
        return halo_rules
    halo_rules = halo_rules.merge(accessory_gp, on=["cluster_id", "target_sku_id"], how="left")
    halo_rules["avg_target_gp"] = halo_rules["avg_target_gp"].fillna(0.0)
    halo_rules["halo_profit"] = (
        halo_rules["support"] * halo_rules["avg_target_gp"] * (halo_rules["lift"] - 1.0).clip(lower=0.0) * 8.0
    ).round(4)
    return halo_rules.sort_values(["cluster_id", "halo_profit"], ascending=[True, False]).reset_index(drop=True)


def summarize_halo_scores(halo_rules: pd.DataFrame) -> pd.DataFrame:
    if halo_rules.empty:
        return pd.DataFrame(columns=["cluster_id", "sku_id", "halo_gp", "halo_support", "halo_lift"])
    halo_scores = (
        halo_rules.groupby(["cluster_id", "source_sku_id"], as_index=False)
        .agg(
            halo_gp=("halo_profit", "sum"),
            halo_support=("support", "mean"),
            halo_lift=("lift", "mean"),
        )
        .rename(columns={"source_sku_id": "sku_id"})
    )
    return halo_scores
