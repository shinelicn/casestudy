from __future__ import annotations

from itertools import permutations
from typing import Dict

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SEMANTIC_CLUSTERS = [
    {
        "cluster_id": "C1",
        "cluster_name": "聚类 1：高净值家庭“品质与探索”中心",
        "cluster_english": "Premium & Discovery Cluster",
        "rule_focus": "压缩低价与私牌，优先高端/拉拉裤，并保护高阶尺码连续性。",
    },
    {
        "cluster_id": "C2",
        "cluster_name": "聚类 2：市郊“重度囤货”驱动大仓",
        "cluster_english": "Suburban Stock-up Drivers",
        "rule_focus": "优先量贩装并强化 KVI 保护，小包装默认退出。",
    },
    {
        "cluster_id": "C3",
        "cluster_name": "聚类 3：城市高频“紧急补缺”店",
        "cluster_english": "Urban Emergency / Fill-in",
        "rule_focus": "只留头部品牌，死守 NB/S，彻底禁入大箱装。",
    },
    {
        "cluster_id": "C4",
        "cluster_name": "聚类 4：价值敏感型“基础防守”堡垒",
        "cluster_english": "Value-Conscious Defenders",
        "rule_focus": "提高经济型与私牌占比，并重罚同 CDT 叶子下的重复低价 SKU。",
    },
]


def build_store_features(
    transactions: pd.DataFrame,
    stores: pd.DataFrame,
    inventory_daily: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    tx = transactions.merge(products[["sku_id", "category", "format", "price_tier"]], on="sku_id", how="left")
    diaper_tx = tx[tx["category"] == "diaper"].copy()
    diaper_tx["sales"] = diaper_tx["qty"] * diaper_tx["price"]

    basket_mix = (
        tx.groupby(["store_id", "basket_id"], as_index=False)
        .agg(
            diaper_lines=("category", lambda x: int((x == "diaper").any())),
            accessory_lines=("category", lambda x: int((x != "diaper").any())),
        )
    )
    basket_mix["cross_sell_hit"] = basket_mix["diaper_lines"] * basket_mix["accessory_lines"]

    feature_rows = []
    for store_id, group in diaper_tx.groupby("store_id"):
        total_units = group["qty"].sum()
        total_sales = group["sales"].sum()
        day_count = max(group["date"].nunique(), 1)
        mix = basket_mix[basket_mix["store_id"] == store_id]
        cross_sell_rate = mix["cross_sell_hit"].sum() / max(mix["diaper_lines"].sum(), 1)
        feature_rows.append(
            {
                "store_id": store_id,
                "weekly_units": total_units / max(day_count / 7.0, 1.0),
                "avg_basket": group.groupby("basket_id")["sales"].sum().mean(),
                "visits_per_day": group["basket_id"].nunique() / day_count,
                "pullup_share": group.loc[group["format"] == "拉拉裤", "qty"].sum() / max(total_units, 1),
                "premium_share": group.loc[group["price_tier"] == "best", "qty"].sum() / max(total_units, 1),
                "promo_share": group.loc[group["promo_flag"] == 1, "qty"].sum() / max(total_units, 1),
                "avg_selling_price": total_sales / max(total_units, 1),
                "cross_sell_rate": cross_sell_rate,
            }
        )
    features = stores.merge(pd.DataFrame(feature_rows), on="store_id", how="left")
    inv = inventory_daily.groupby("store_id", as_index=False).agg(oos_rate=("oos_flag", "mean"))
    features = features.merge(inv, on="store_id", how="left")
    features["format_hyper"] = (features["store_format"] == "Hyper").astype(int)
    features["format_super"] = (features["store_format"] == "Super").astype(int)
    features["format_cvs"] = (features["store_format"] == "CVS").astype(int)
    features = features.fillna(0.0)
    return features


def _normalize_centroids(centroids: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    normalized = centroids.copy()
    for col in cols:
        series = normalized[col]
        span = float(series.max() - series.min())
        if span <= 1e-9:
            normalized[col] = 0.5
        else:
            normalized[col] = (series - series.min()) / span
    return normalized


def _semantic_score(profile_id: str, row: pd.Series) -> float:
    if profile_id == "C1":
        return float(
            1.7 * row["income_proxy"]
            + 1.6 * row["avg_basket"]
            + 1.5 * row["premium_share"]
            + 1.3 * row["avg_selling_price"]
            + 1.2 * row["cross_sell_rate"]
            + 0.8 * row["pullup_share"]
            - 0.9 * row["promo_share"]
        )
    if profile_id == "C2":
        return float(
            1.8 * row["format_hyper"]
            + 1.5 * row["weekly_units"]
            + 1.2 * row["avg_basket"]
            + 1.0 * row["promo_share"]
            + 0.5 * row["cross_sell_rate"]
        )
    if profile_id == "C3":
        return float(
            1.8 * row["format_cvs"]
            + 1.2 * row["visits_per_day"]
            + 0.8 * row["oos_rate"]
            - 1.3 * row["avg_basket"]
            - 0.8 * row["avg_selling_price"]
        )
    return float(
        1.7 * (1.0 - row["income_proxy"])
        + 1.4 * row["promo_share"]
        + 1.1 * (1.0 - row["premium_share"])
        + 1.0 * (1.0 - row["avg_selling_price"])
        + 0.7 * (1.0 - row["cross_sell_rate"])
    )


def _assign_semantic_map(centroids: pd.DataFrame) -> dict[int, dict[str, str]]:
    score_cols = [
        "income_proxy",
        "weekly_units",
        "avg_basket",
        "visits_per_day",
        "pullup_share",
        "premium_share",
        "promo_share",
        "avg_selling_price",
        "cross_sell_rate",
        "oos_rate",
        "format_hyper",
        "format_cvs",
    ]
    normalized = _normalize_centroids(centroids, score_cols)
    raw_labels = normalized["raw_cluster"].tolist()
    profile_ids = [item["cluster_id"] for item in SEMANTIC_CLUSTERS]
    score_lookup = {
        raw_label: {profile_id: _semantic_score(profile_id, normalized[normalized["raw_cluster"] == raw_label].iloc[0]) for profile_id in profile_ids}
        for raw_label in raw_labels
    }

    best_total = None
    best_map: dict[int, dict[str, str]] = {}
    for perm in permutations(raw_labels, len(profile_ids)):
        total = 0.0
        candidate: dict[int, dict[str, str]] = {}
        for idx, raw_label in enumerate(perm):
            semantic = SEMANTIC_CLUSTERS[idx]
            total += score_lookup[raw_label][semantic["cluster_id"]]
            candidate[int(raw_label)] = semantic
        if best_total is None or total > best_total:
            best_total = total
            best_map = candidate
    return best_map


def assign_clusters(store_features: pd.DataFrame, stores: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    del stores
    n_clusters = 4
    numeric_cols = [
        "income_proxy",
        "baseline_gp",
        "weekly_units",
        "avg_basket",
        "visits_per_day",
        "pullup_share",
        "premium_share",
        "promo_share",
        "avg_selling_price",
        "cross_sell_rate",
        "oos_rate",
        "format_hyper",
        "format_super",
        "format_cvs",
    ]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(store_features[numeric_cols])
    model = KMeans(n_clusters=n_clusters, n_init=20, random_state=7)
    labels = model.fit_predict(scaled)

    clustered = store_features.copy()
    clustered["raw_cluster"] = labels
    centroids = clustered.groupby("raw_cluster", as_index=False)[numeric_cols].mean()
    semantic_map = _assign_semantic_map(centroids)
    clustered["cluster_id"] = clustered["raw_cluster"].map(lambda x: semantic_map[int(x)]["cluster_id"])
    clustered["cluster_name"] = clustered["raw_cluster"].map(lambda x: semantic_map[int(x)]["cluster_name"])
    clustered["cluster_english"] = clustered["raw_cluster"].map(lambda x: semantic_map[int(x)]["cluster_english"])
    clustered["cluster_rule_focus"] = clustered["raw_cluster"].map(lambda x: semantic_map[int(x)]["rule_focus"])
    return clustered.drop(columns=["raw_cluster"]).sort_values(["cluster_id", "store_id"]).reset_index(drop=True)


def _preference_table(
    cluster_tx: pd.DataFrame,
    field: str,
    title: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (cluster_id, cluster_name), group in cluster_tx.groupby(["cluster_id", "cluster_name"]):
        total = group["qty"].sum()
        shares = (
            group.groupby(field, as_index=False)["qty"]
            .sum()
            .assign(share=lambda df: df["qty"] / max(total, 1))
            .sort_values(["share", field], ascending=[False, True])
            .head(5)
        )
        for row in shares.itertuples():
            rows.append(
                {
                    "cluster_id": cluster_id,
                    "cluster_name": cluster_name,
                    "dimension": title,
                    "value": getattr(row, field),
                    "share": round(float(row.share), 4),
                }
            )
    return pd.DataFrame(rows)


def profile_clusters(
    clustered_stores: pd.DataFrame,
    transactions: pd.DataFrame,
    products: pd.DataFrame,
) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    tx = transactions.merge(
        clustered_stores[["store_id", "cluster_id", "cluster_name", "cluster_english"]],
        on="store_id",
        how="left",
    )
    tx = tx.merge(products[["sku_id", "category", "size", "format", "brand", "price_tier"]], on="sku_id", how="left")
    diaper_tx = tx[tx["category"] == "diaper"].copy()
    diaper_tx["sales"] = diaper_tx["qty"] * diaper_tx["price"]
    profile_rows = []
    for cluster_id, store_slice in clustered_stores.groupby("cluster_id"):
        cluster_name = store_slice["cluster_name"].iloc[0]
        cluster_english = store_slice["cluster_english"].iloc[0]
        rule_focus = store_slice["cluster_rule_focus"].iloc[0]
        group = diaper_tx[diaper_tx["cluster_id"] == cluster_id]
        format_share = group.loc[group["format"] == "拉拉裤", "qty"].sum() / max(group["qty"].sum(), 1)
        premium_share = group.loc[group["price_tier"] == "best", "qty"].sum() / max(group["qty"].sum(), 1)
        dominant_size = (
            group.groupby("size")["qty"].sum().sort_values(ascending=False).index[0]
            if not group.empty
            else "NA"
        )
        profile_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "cluster_english": cluster_english,
                "store_count": int(store_slice["store_id"].nunique()),
                "dominant_store_format": store_slice["store_format"].mode().iat[0],
                "avg_income_proxy": round(float(store_slice["income_proxy"].mean()), 2),
                "avg_weekly_units_per_store": round(float(group["qty"].sum() / max(group["date"].nunique() / 7.0, 1.0) / max(len(store_slice), 1)), 2),
                "pullup_share": round(float(format_share), 4),
                "premium_share": round(float(premium_share), 4),
                "cross_sell_rate": round(float(store_slice["cross_sell_rate"].mean()), 4),
                "dominant_size": dominant_size,
                "rule_focus": rule_focus,
            }
        )
    cluster_profile = pd.DataFrame(profile_rows).sort_values("cluster_id").reset_index(drop=True)
    preference_tables = {
        "size 偏好": _preference_table(diaper_tx, "size", "size"),
        "format 偏好": _preference_table(diaper_tx, "format", "format"),
        "brand 偏好": _preference_table(diaper_tx, "brand", "brand"),
        "price_tier 偏好": _preference_table(diaper_tx, "price_tier", "price_tier"),
    }
    return cluster_profile, preference_tables
