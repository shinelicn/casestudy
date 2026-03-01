from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_pilot(
    clustered_stores: pd.DataFrame,
    decision_table: pd.DataFrame,
    seed: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    cluster_uplift = decision_table.groupby("cluster_id", as_index=False)["delta_total_gp"].sum().rename(columns={"delta_total_gp": "cluster_delta_gp"})
    stores = clustered_stores.merge(cluster_uplift, on="cluster_id", how="left")
    stores["cluster_delta_gp"] = stores["cluster_delta_gp"].fillna(0.0)
    stores = stores.sort_values(["trade_area_id", "store_id"]).reset_index(drop=True)
    stores["group"] = stores.groupby("trade_area_id").cumcount().map(lambda idx: "treatment" if idx % 2 == 0 else "control")
    stores["pre_gp"] = stores["baseline_gp"]
    stores["expected_uplift"] = np.where(stores["group"] == "treatment", stores["cluster_delta_gp"] * 0.55, stores["cluster_delta_gp"] * 0.08)
    noise = rng.normal(0.0, 120.0, len(stores))
    stores["post_gp"] = stores["pre_gp"] + stores["expected_uplift"] + noise
    stores["uplift_gp"] = stores["post_gp"] - stores["pre_gp"]
    summary = (
        stores.groupby("group", as_index=False)
        .agg(
            store_count=("store_id", "nunique"),
            pre_gp=("pre_gp", "mean"),
            post_gp=("post_gp", "mean"),
            uplift_gp=("uplift_gp", "mean"),
        )
        .sort_values("group")
        .reset_index(drop=True)
    )
    return stores, summary
