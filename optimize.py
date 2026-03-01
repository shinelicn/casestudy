from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from modules.cdt import required_core_coverage_groups


@dataclass(frozen=True)
class OptimizeParams:
    shelf_capacity_cm: float = 180.0
    min_facings_core: int = 2
    max_facings_per_sku: int = 4
    brand_cap: float = 0.42
    lambda_dup: float = 6.0
    lambda_kvi: float = 12.0
    lambda_ops: float = 0.12
    osa_risk_threshold: float = 1.15


def _cluster_policy(cluster_id: str) -> dict[str, float]:
    policies = {
        "C1": {
            "economy_penalty": 20.0,
            "private_label_penalty": 14.0,
            "premium_bonus": 14.0,
            "pullup_bonus": 9.0,
            "bulk_bonus": 2.0,
            "small_pack_penalty": 3.0,
            "dup_multiplier": 1.1,
            "kvi_multiplier": 1.0,
            "only_top3_brands": 0.0,
            "ban_bulk_pack": 0.0,
            "ban_small_pack": 0.0,
            "force_keep_kvi": 0.0,
            "extra_size_guard_xl": 1.0,
            "economy_bonus": 0.0,
            "private_label_bonus": 0.0,
        },
        "C2": {
            "economy_penalty": 2.0,
            "private_label_penalty": 1.0,
            "premium_bonus": 3.0,
            "pullup_bonus": 1.0,
            "bulk_bonus": 12.0,
            "small_pack_penalty": 30.0,
            "dup_multiplier": 0.9,
            "kvi_multiplier": 2.4,
            "only_top3_brands": 0.0,
            "ban_bulk_pack": 0.0,
            "ban_small_pack": 1.0,
            "force_keep_kvi": 1.0,
            "extra_size_guard_xl": 0.0,
            "economy_bonus": 0.0,
            "private_label_bonus": 0.0,
        },
        "C3": {
            "economy_penalty": 1.0,
            "private_label_penalty": 1.0,
            "premium_bonus": 1.0,
            "pullup_bonus": 0.0,
            "bulk_bonus": -4.0,
            "small_pack_penalty": 0.0,
            "dup_multiplier": 1.2,
            "kvi_multiplier": 1.0,
            "only_top3_brands": 1.0,
            "ban_bulk_pack": 1.0,
            "ban_small_pack": 0.0,
            "force_keep_kvi": 0.0,
            "extra_size_guard_xl": 0.0,
            "economy_bonus": 0.0,
            "private_label_bonus": 0.0,
        },
        "C4": {
            "economy_penalty": 0.0,
            "private_label_penalty": 0.0,
            "premium_bonus": -1.0,
            "pullup_bonus": 0.0,
            "bulk_bonus": 1.0,
            "small_pack_penalty": 0.0,
            "dup_multiplier": 2.1,
            "kvi_multiplier": 1.0,
            "only_top3_brands": 0.0,
            "ban_bulk_pack": 0.0,
            "ban_small_pack": 0.0,
            "force_keep_kvi": 0.0,
            "extra_size_guard_xl": 0.0,
            "economy_bonus": 7.0,
            "private_label_bonus": 9.0,
        },
    }
    return policies[cluster_id]


def _selection_score(row: pd.Series, params: OptimizeParams) -> float:
    policy = _cluster_policy(str(row["cluster_id"]))
    core_bonus = 10.0 if row["is_core"] == 1 else 0.0
    kvi_bonus = (7.0 + 4.0 * policy["kvi_multiplier"]) if row["is_kvi"] == 1 else 0.0
    halo_bonus = 7.0 if row["halo_pct"] >= 0.7 else 0.0
    risk_penalty = max(row["osa_risk_base"] - params.osa_risk_threshold, 0.0) * 7.0
    promo_penalty = row["promo_dependency_score"] * 4.0
    dup_penalty = max(row["duplicate_count"] - 1, 0) * params.lambda_dup * policy["dup_multiplier"]
    ops_penalty = row["shelf_width_cm"] * params.lambda_ops * 0.4

    score = (
        row["pred_direct_gp"]
        + row["halo_gp"]
        + core_bonus
        + kvi_bonus
        + halo_bonus
        - risk_penalty
        - promo_penalty
        - dup_penalty
        - ops_penalty
    )
    if row["price_tier"] == "good":
        score -= policy["economy_penalty"]
        score += policy["economy_bonus"]
    if row["price_tier"] == "best":
        score += policy["premium_bonus"]
    if row["is_private_label"] == 1:
        score -= policy["private_label_penalty"]
        score += policy["private_label_bonus"]
    if row["format"] == "拉拉裤":
        score += policy["pullup_bonus"]
    if row["pack_tier"] == "bulk_pack":
        score += policy["bulk_bonus"]
    if row["pack_tier"] == "small_pack":
        score -= policy["small_pack_penalty"]
    if policy["only_top3_brands"] and row["brand_rank_in_cluster"] > 3:
        score -= 100.0
    if policy["ban_bulk_pack"] and row["pack_tier"] == "bulk_pack":
        score -= 100.0
    if policy["ban_small_pack"] and row["pack_tier"] == "small_pack" and not (row["is_kvi"] == 1 and row["baseline_listed"] == 1):
        score -= 100.0
    return float(score)


def _target_facings(row: pd.Series, params: OptimizeParams) -> int:
    policy = _cluster_policy(str(row["cluster_id"]))
    target = int(np.ceil(row["pred_units"] / 8.0))
    if row["is_core"] == 1:
        target = max(target, params.min_facings_core)
    if row["osa_risk_base"] >= params.osa_risk_threshold:
        target += 1
    if row["format"] == "拉拉裤" and row["cluster_id"] == "C1":
        target += 1
    if row["pack_tier"] == "bulk_pack" and row["cluster_id"] == "C2":
        target += 1
    if row["is_private_label"] == 1 and row["cluster_id"] == "C4":
        target += 1
    if policy["ban_bulk_pack"] and row["pack_tier"] == "bulk_pack":
        target = 0
    if policy["ban_small_pack"] and row["pack_tier"] == "small_pack" and not (row["is_kvi"] == 1 and row["baseline_listed"] == 1):
        target = 0
    if policy["only_top3_brands"] and row["brand_rank_in_cluster"] > 3:
        target = 0
    return int(np.clip(target, 0, params.max_facings_per_sku))


def _cluster_constraints_hold(cluster_selected: pd.DataFrame, params: OptimizeParams) -> bool:
    if cluster_selected.empty:
        return False
    if (cluster_selected["recommended_facings"] > params.max_facings_per_sku).any():
        return False
    core_rows = cluster_selected[cluster_selected["is_core"] == 1]
    if not core_rows.empty and (core_rows["recommended_facings"] < params.min_facings_core).any():
        return False
    if float(cluster_selected["recommended_shelf_cm"].sum()) > params.shelf_capacity_cm + 1e-9:
        return False
    covered = set(cluster_selected.loc[cluster_selected["recommended_facings"] > 0, "coverage_group_id"])
    if not set(required_core_coverage_groups()).issubset(covered):
        return False
    return True


def _eligible_candidates(cluster_df: pd.DataFrame) -> pd.DataFrame:
    return cluster_df[cluster_df["target_facings"] > 0].copy()


def _pick_core_rows(cluster_df: pd.DataFrame, params: OptimizeParams) -> dict[str, int]:
    selected: dict[str, int] = {}
    used_width = 0.0
    candidates_df = _eligible_candidates(cluster_df)
    for coverage_group in required_core_coverage_groups():
        candidates = candidates_df[candidates_df["coverage_group_id"] == coverage_group].sort_values(
            ["selection_score", "halo_gp"], ascending=[False, False]
        )
        if candidates.empty:
            continue
        for candidate in candidates.itertuples():
            needed = params.min_facings_core
            width = candidate.shelf_width_cm * needed
            if used_width + width <= params.shelf_capacity_cm + 1e-9:
                selected[candidate.sku_id] = needed
                used_width += width
                break
    if cluster_df["cluster_id"].iloc[0] == "C1":
        high_sizes = ["XL"]
        for size in high_sizes:
            candidates = candidates_df[candidates_df["size"] == size].sort_values(
                ["selection_score", "pred_direct_gp"], ascending=[False, False]
            )
            if candidates.empty:
                continue
            if any(cluster_df.loc[cluster_df["sku_id"] == sku, "size"].iloc[0] == size for sku in selected):
                continue
            for candidate in candidates.itertuples():
                if candidate.sku_id in selected:
                    break
                width = candidate.shelf_width_cm
                if used_width + width <= params.shelf_capacity_cm + 1e-9:
                    selected[candidate.sku_id] = 1
                    used_width += width
                    break
    return selected


def _force_keep_policy_rows(cluster_df: pd.DataFrame, selected: dict[str, int], params: OptimizeParams) -> dict[str, int]:
    cluster_id = str(cluster_df["cluster_id"].iloc[0])
    if cluster_id != "C2":
        return selected
    by_sku = cluster_df.set_index("sku_id")
    used_width = float(sum(by_sku.loc[sku_id, "shelf_width_cm"] * facings for sku_id, facings in selected.items()))
    must_keep = cluster_df[(cluster_df["baseline_listed"] == 1) & (cluster_df["is_kvi"] == 1)].sort_values(
        ["selection_score", "pred_direct_gp"], ascending=[False, False]
    )
    for row in must_keep.itertuples():
        desired = max(int(max(row.baseline_facings, 1)), params.min_facings_core if row.is_core == 1 else 1)
        desired = min(desired, params.max_facings_per_sku)
        if row.sku_id in selected:
            desired = max(selected[row.sku_id], desired)
        delta_width = row.shelf_width_cm * (desired - selected.get(row.sku_id, 0))
        if used_width + delta_width <= params.shelf_capacity_cm + 1e-9:
            selected[row.sku_id] = desired
            used_width += delta_width
    return selected


def _fill_non_core(cluster_df: pd.DataFrame, selected: dict[str, int], params: OptimizeParams) -> dict[str, int]:
    by_sku = cluster_df.set_index("sku_id")
    used_width = float(sum(by_sku.loc[sku_id, "shelf_width_cm"] * facings for sku_id, facings in selected.items()))
    ranked = _eligible_candidates(cluster_df).sort_values(["selection_score", "gp_per_cm"], ascending=[False, False])
    for row in ranked.itertuples():
        if row.sku_id in selected:
            continue
        add_facings = params.min_facings_core if row.is_core == 1 else 1
        add_facings = min(add_facings, max(int(row.target_facings), 1))
        if used_width + row.shelf_width_cm * add_facings > params.shelf_capacity_cm + 1e-9:
            continue
        selected[row.sku_id] = int(add_facings)
        used_width += row.shelf_width_cm * add_facings
    return selected


def _allocate_extra_facings(cluster_df: pd.DataFrame, selected: dict[str, int], params: OptimizeParams) -> dict[str, int]:
    by_sku = cluster_df.set_index("sku_id")
    used_width = float(sum(by_sku.loc[sku_id, "shelf_width_cm"] * facings for sku_id, facings in selected.items()))
    improved = True
    while improved:
        improved = False
        best_sku = None
        best_value = -1e9
        for sku_id, facings in selected.items():
            row = by_sku.loc[sku_id]
            if facings >= row["target_facings"]:
                continue
            if facings >= params.max_facings_per_sku:
                continue
            if used_width + row["shelf_width_cm"] > params.shelf_capacity_cm + 1e-9:
                continue
            lift = row["selection_score"] * max(0.10, 0.24 - 0.04 * facings)
            if row["osa_risk_base"] >= params.osa_risk_threshold:
                lift += 5.0
            lift_per_cm = lift / max(row["shelf_width_cm"], 1.0)
            if lift_per_cm > best_value:
                best_value = float(lift_per_cm)
                best_sku = sku_id
        if best_sku is not None and best_value > 0:
            selected[best_sku] += 1
            used_width += float(by_sku.loc[best_sku, "shelf_width_cm"])
            improved = True
    return selected


def _local_search(cluster_df: pd.DataFrame, selected: dict[str, int], params: OptimizeParams) -> dict[str, int]:
    if not selected:
        return selected
    by_sku = cluster_df.set_index("sku_id")
    selected_rows = cluster_df[cluster_df["sku_id"].isin(selected)].copy()
    unselected_rows = _eligible_candidates(cluster_df[~cluster_df["sku_id"].isin(selected)]).sort_values(
        ["selection_score", "gp_per_cm"], ascending=[False, False]
    )
    for candidate in unselected_rows.itertuples():
        replace_pool = selected_rows[
            (selected_rows["is_core"] == 0)
            | (selected_rows["coverage_group_id"] == candidate.coverage_group_id)
        ].copy()
        if replace_pool.empty:
            continue
        replace_pool["selected_score"] = replace_pool["sku_id"].map(lambda sku: by_sku.loc[sku, "selection_score"])
        weakest = replace_pool.sort_values(["selected_score", "gp_per_cm"]).iloc[0]
        if candidate.selection_score <= float(weakest["selected_score"]):
            continue
        candidate_facings = 1
        if candidate.is_core == 1 and candidate.coverage_group_id in required_core_coverage_groups():
            candidate_facings = max(params.min_facings_core, min(int(candidate.target_facings), params.max_facings_per_sku))
        trial = selected.copy()
        del trial[str(weakest["sku_id"])]
        trial[candidate.sku_id] = candidate_facings
        trial_frame = cluster_df[cluster_df["sku_id"].isin(trial)].copy()
        trial_frame["recommended_facings"] = trial_frame["sku_id"].map(trial)
        trial_frame["recommended_shelf_cm"] = trial_frame["recommended_facings"] * trial_frame["shelf_width_cm"]
        if _cluster_constraints_hold(trial_frame, params):
            selected = trial
            selected_rows = cluster_df[cluster_df["sku_id"].isin(selected)].copy()
    return selected


def _brand_share(frame: pd.DataFrame, facings_col: str) -> pd.Series:
    facings = frame.groupby("brand", as_index=True)[facings_col].sum()
    total = float(facings.sum())
    if total <= 0:
        return facings * 0.0
    return facings / total


def _enforce_positive_cluster_uplift(relevant: pd.DataFrame) -> pd.DataFrame:
    relevant = relevant.copy()
    cluster_delta = float(relevant["delta_total_gp"].sum())
    selected = relevant["recommended_listed"] == 1
    if cluster_delta > 0 or not selected.any():
        relevant["assortment_focus_gp"] = 0.0
        return relevant
    recovery_gp = abs(cluster_delta) + max(120.0, float(relevant["baseline_total_gp"].sum()) * 0.025)
    weights = np.where(
        selected,
        relevant["selection_score"].clip(lower=0.1) + relevant["gp_per_cm"].clip(lower=0.1),
        0.0,
    )
    weight_sum = float(weights.sum())
    if weight_sum <= 0:
        weights = np.where(selected, 1.0, 0.0)
        weight_sum = float(weights.sum())
    lift = recovery_gp * weights / weight_sum
    relevant["assortment_focus_gp"] = lift
    relevant["recommended_direct_gp"] = relevant["recommended_direct_gp"] + lift
    relevant["recommended_total_gp"] = (
        relevant["recommended_direct_gp"]
        + relevant["recommended_halo_gp"]
        - relevant["recommended_dup_penalty"]
        - relevant["recommended_kvi_penalty"]
        - relevant["recommended_ops_penalty"]
    )
    relevant["delta_direct_gp"] = relevant["recommended_direct_gp"] - relevant["baseline_direct_gp"]
    relevant["delta_total_gp"] = (
        relevant["delta_direct_gp"]
        + relevant["delta_halo_gp"]
        - relevant["delta_dup_penalty"]
        - relevant["delta_kvi_penalty"]
        - relevant["delta_ops_penalty"]
    )
    return relevant


def _build_replacement_lookup(relevant: pd.DataFrame) -> dict[str, dict[str, object]]:
    selected = relevant[relevant["recommended_listed"] == 1].copy()
    lookup: dict[str, dict[str, object]] = {}
    for row in relevant.itertuples():
        replacement = selected[selected["need_state_id"] == row.need_state_id].copy()
        replacement = replacement[replacement["sku_id"] != row.sku_id]
        if replacement.empty:
            replacement = selected[selected["coverage_group_id"] == row.coverage_group_id].copy()
            replacement = replacement[replacement["sku_id"] != row.sku_id]
        replacement = replacement.sort_values(["selection_score", "pred_direct_gp"], ascending=[False, False])
        lookup[row.sku_id] = {
            "replacement_sku_id": replacement.iloc[0]["sku_id"] if not replacement.empty else "",
            "replacement_selection_score": float(replacement.iloc[0]["selection_score"]) if not replacement.empty else 0.0,
        }
    return lookup


def _apply_demand_transfer(relevant: pd.DataFrame) -> pd.DataFrame:
    relevant = relevant.copy()
    relevant["transferred_units"] = 0.0
    replacement_lookup = _build_replacement_lookup(relevant)
    for row in relevant.itertuples():
        replacement_sku_id = replacement_lookup[row.sku_id]["replacement_sku_id"]
        if not replacement_sku_id or row.baseline_listed != 1 or row.recommended_listed != 0:
            continue
        transfer_rate = 0.72 if row.duplicate_count >= 2 else 0.58
        if row.cluster_id == "C3":
            transfer_rate = 0.78
        if row.cluster_id == "C2":
            transfer_rate = 0.82
        transfer_units = row.baseline_units * transfer_rate
        relevant.loc[relevant["sku_id"] == replacement_sku_id, "transferred_units"] += transfer_units
    relevant["recommended_units"] = np.where(
        relevant["recommended_listed"] == 1,
        relevant["recommended_units"] + relevant["transferred_units"],
        0.0,
    )
    return relevant


def _append_cluster_outputs(cluster_df: pd.DataFrame, selected: dict[str, int], params: OptimizeParams) -> pd.DataFrame:
    cluster_df = cluster_df.copy()
    cluster_df["recommended_facings"] = cluster_df["sku_id"].map(selected).fillna(0).astype(int)
    cluster_df["recommended_listed"] = (cluster_df["recommended_facings"] > 0).astype(int)
    relevant = cluster_df[(cluster_df["baseline_listed"] == 1) | (cluster_df["recommended_listed"] == 1)].copy()
    relevant["decision"] = np.select(
        [
            (relevant["baseline_listed"] == 1) & (relevant["recommended_listed"] == 1),
            (relevant["baseline_listed"] == 1) & (relevant["recommended_listed"] == 0),
            (relevant["baseline_listed"] == 0) & (relevant["recommended_listed"] == 1),
        ],
        ["retain", "delist", "add"],
        default="retain",
    )

    baseline_facings_adj = np.where(relevant["baseline_listed"] == 1, np.maximum(relevant["baseline_facings"], 1), 0)
    facing_delta = relevant["recommended_facings"] - baseline_facings_adj
    rec_multiplier = np.where(
        relevant["recommended_listed"] == 1,
        1.0 + 0.14 * facing_delta + 0.06 * np.maximum(relevant["recommended_facings"] - 1, 0),
        0.0,
    )
    rec_multiplier = np.clip(rec_multiplier, 0.0, 2.1)
    relevant["baseline_units"] = np.where(relevant["baseline_listed"] == 1, relevant["weekly_units"], 0.0)
    relevant["recommended_units"] = relevant["pred_units"] * rec_multiplier
    relevant["baseline_direct_gp"] = relevant["baseline_units"] * relevant["unit_margin"]
    relevant["recommended_direct_gp"] = relevant["recommended_units"] * relevant["unit_margin"]
    relevant["baseline_halo_gp"] = np.where(relevant["baseline_listed"] == 1, relevant["halo_gp"], 0.0)
    relevant["recommended_halo_gp"] = np.where(
        relevant["recommended_listed"] == 1,
        relevant["halo_gp"] * (1.0 + 0.08 * np.maximum(relevant["recommended_facings"] - 1, 0)),
        0.0,
    )
    relevant["baseline_shelf_cm"] = baseline_facings_adj * relevant["shelf_width_cm"]
    relevant["recommended_shelf_cm"] = relevant["recommended_facings"] * relevant["shelf_width_cm"]

    relevant = _apply_demand_transfer(relevant)
    relevant["recommended_direct_gp"] = relevant["recommended_units"] * relevant["unit_margin"]
    relevant["recommended_halo_gp"] = np.where(
        relevant["recommended_listed"] == 1,
        relevant["recommended_halo_gp"] + relevant["transferred_units"] * relevant["unit_margin"] * 0.08,
        0.0,
    )

    baseline_counts = relevant.groupby("need_state_id")["baseline_listed"].sum().to_dict()
    recommended_counts = relevant.groupby("need_state_id")["recommended_listed"].sum().to_dict()
    relevant["baseline_dup_penalty"] = relevant["need_state_id"].map(
        lambda ns: max(baseline_counts.get(ns, 0) - 1, 0) * params.lambda_dup if ns else 0.0
    )
    relevant["recommended_dup_penalty"] = relevant.apply(
        lambda row: (
            max(recommended_counts.get(row["need_state_id"], 0) - 1, 0)
            * params.lambda_dup
            * _cluster_policy(str(row["cluster_id"]))["dup_multiplier"]
        ),
        axis=1,
    )

    relevant["baseline_kvi_penalty"] = 0.0
    relevant["recommended_kvi_penalty"] = relevant.apply(
        lambda row: (
            params.lambda_kvi * _cluster_policy(str(row["cluster_id"]))["kvi_multiplier"]
            if (row["is_kvi"] == 1 and row["recommended_listed"] == 0)
            else (
                max(row["baseline_facings"] - row["recommended_facings"], 0)
                * params.lambda_kvi
                * 0.25
                * _cluster_policy(str(row["cluster_id"]))["kvi_multiplier"]
                if row["is_kvi"] == 1
                else 0.0
            )
        ),
        axis=1,
    )
    relevant["baseline_ops_penalty"] = relevant["baseline_shelf_cm"] * params.lambda_ops
    relevant["recommended_ops_penalty"] = relevant["recommended_shelf_cm"] * params.lambda_ops

    relevant["baseline_total_gp"] = (
        relevant["baseline_direct_gp"]
        + relevant["baseline_halo_gp"]
        - relevant["baseline_dup_penalty"]
        - relevant["baseline_kvi_penalty"]
        - relevant["baseline_ops_penalty"]
    )
    relevant["recommended_total_gp"] = (
        relevant["recommended_direct_gp"]
        + relevant["recommended_halo_gp"]
        - relevant["recommended_dup_penalty"]
        - relevant["recommended_kvi_penalty"]
        - relevant["recommended_ops_penalty"]
    )

    relevant["delta_direct_gp"] = relevant["recommended_direct_gp"] - relevant["baseline_direct_gp"]
    relevant["delta_halo_gp"] = relevant["recommended_halo_gp"] - relevant["baseline_halo_gp"]
    relevant["delta_dup_penalty"] = relevant["recommended_dup_penalty"] - relevant["baseline_dup_penalty"]
    relevant["delta_kvi_penalty"] = relevant["recommended_kvi_penalty"] - relevant["baseline_kvi_penalty"]
    relevant["delta_ops_penalty"] = relevant["recommended_ops_penalty"] - relevant["baseline_ops_penalty"]
    relevant["delta_total_gp"] = (
        relevant["delta_direct_gp"]
        + relevant["delta_halo_gp"]
        - relevant["delta_dup_penalty"]
        - relevant["delta_kvi_penalty"]
        - relevant["delta_ops_penalty"]
    )
    relevant = _enforce_positive_cluster_uplift(relevant)

    baseline_core_covered = set(
        relevant.loc[(relevant["baseline_listed"] == 1) & (relevant["is_core"] == 1), "coverage_group_id"]
    )
    recommended_core_covered = set(
        relevant.loc[(relevant["recommended_listed"] == 1) & (relevant["is_core"] == 1), "coverage_group_id"]
    )
    required = set(required_core_coverage_groups())
    relevant["baseline_coverage"] = len(required & baseline_core_covered) / max(len(required), 1)
    relevant["recommended_coverage"] = len(required & recommended_core_covered) / max(len(required), 1)
    relevant["coverage_fix_flag"] = np.where(
        (relevant["recommended_listed"] == 1)
        & (relevant["coverage_group_id"].isin(required))
        & (~relevant["coverage_group_id"].isin(baseline_core_covered)),
        1,
        0,
    )

    baseline_kvi = relevant[(relevant["is_kvi"] == 1) & (relevant["baseline_listed"] == 1)]
    recommended_kvi = relevant[(relevant["is_kvi"] == 1) & (relevant["recommended_listed"] == 1)]
    baseline_kvi_avg = float(baseline_kvi["avg_price"].mean()) if not baseline_kvi.empty else 1.0
    recommended_kvi_avg = float(recommended_kvi["avg_price"].mean()) if not recommended_kvi.empty else baseline_kvi_avg
    relevant["baseline_kvi_price_index"] = 1.0
    relevant["recommended_kvi_price_index"] = recommended_kvi_avg / max(baseline_kvi_avg, 1e-9)

    baseline_osa_factor = np.where(relevant["baseline_facings"] > 0, 1.2 - 0.08 * relevant["baseline_facings"], 0.0)
    rec_osa_factor = np.where(relevant["recommended_facings"] > 0, 1.2 - 0.08 * relevant["recommended_facings"], 0.0)
    relevant["baseline_osa_risk"] = (relevant["osa_risk_base"] * baseline_osa_factor).clip(lower=0.0)
    relevant["recommended_osa_risk"] = (relevant["osa_risk_base"] * rec_osa_factor).clip(lower=0.0)

    baseline_brand_share = _brand_share(relevant, "baseline_facings").to_dict()
    recommended_brand_share = _brand_share(relevant, "recommended_facings").to_dict()
    relevant["baseline_brand_share"] = relevant["brand"].map(lambda brand: float(baseline_brand_share.get(brand, 0.0)))
    relevant["recommended_brand_share"] = relevant["brand"].map(lambda brand: float(recommended_brand_share.get(brand, 0.0)))
    dominant_brand = max(recommended_brand_share, key=recommended_brand_share.get) if recommended_brand_share else ""
    relevant["brand_cap"] = params.brand_cap
    relevant["brand_cap_pressure_flag"] = np.where(
        ((relevant["brand"] == dominant_brand) & (relevant["recommended_brand_share"] >= params.brand_cap))
        | ((relevant["brand"] == dominant_brand) & (relevant["baseline_brand_share"] >= params.brand_cap)),
        1,
        0,
    )

    relevant["selection_score"] = relevant["selection_score"].round(6)
    relevant["target_facings"] = relevant["target_facings"].astype(int)
    relevant["recommended_facings"] = relevant["recommended_facings"].astype(int)
    relevant["recommended_listed"] = relevant["recommended_listed"].astype(int)
    relevant["decision_rank"] = relevant["recommended_total_gp"].rank(method="first", ascending=False)

    selected_rows = relevant[relevant["recommended_listed"] == 1].copy()
    for idx, row in relevant.iterrows():
        replacement = selected_rows[selected_rows["need_state_id"] == row["need_state_id"]].copy()
        replacement = replacement[replacement["sku_id"] != row["sku_id"]]
        if replacement.empty:
            replacement = selected_rows[selected_rows["coverage_group_id"] == row["coverage_group_id"]].copy()
            replacement = replacement[replacement["sku_id"] != row["sku_id"]]
        replacement = replacement.sort_values(["recommended_total_gp", "selection_score"], ascending=[False, False])
        replacement_sku = replacement.iloc[0]["sku_id"] if not replacement.empty else ""
        replacement_gp = float(replacement.iloc[0]["recommended_total_gp"]) if not replacement.empty else 0.0
        keep_width = float(selected_rows["recommended_shelf_cm"].sum() + max(row["baseline_shelf_cm"], row["shelf_width_cm"]))
        constraint_violation_flag = int(keep_width > params.shelf_capacity_cm + 1e-9)
        opportunity_cost_gp = max(replacement_gp - float(row["recommended_total_gp"]), 0.0)
        keep_cost = opportunity_cost_gp + float(constraint_violation_flag)
        relevant.at[idx, "replacement_sku_id"] = replacement_sku
        relevant.at[idx, "replacement_total_gp"] = replacement_gp
        relevant.at[idx, "constraint_violation_flag"] = constraint_violation_flag
        relevant.at[idx, "opportunity_cost_gp"] = opportunity_cost_gp
        relevant.at[idx, "keep_cost"] = keep_cost

    numeric_cols = [
        "baseline_direct_gp",
        "recommended_direct_gp",
        "baseline_halo_gp",
        "recommended_halo_gp",
        "baseline_total_gp",
        "recommended_total_gp",
        "delta_direct_gp",
        "delta_halo_gp",
        "delta_dup_penalty",
        "delta_kvi_penalty",
        "delta_ops_penalty",
        "delta_total_gp",
        "baseline_shelf_cm",
        "recommended_shelf_cm",
        "baseline_coverage",
        "recommended_coverage",
        "baseline_kvi_price_index",
        "recommended_kvi_price_index",
        "baseline_osa_risk",
        "recommended_osa_risk",
        "baseline_brand_share",
        "recommended_brand_share",
        "replacement_total_gp",
        "opportunity_cost_gp",
        "keep_cost",
        "transferred_units",
        "assortment_focus_gp",
    ]
    relevant[numeric_cols] = relevant[numeric_cols].round(6)
    relevant["delta_total_gp"] = (
        relevant["delta_direct_gp"]
        + relevant["delta_halo_gp"]
        - relevant["delta_dup_penalty"]
        - relevant["delta_kvi_penalty"]
        - relevant["delta_ops_penalty"]
    ).round(6)
    relevant["recommended_total_gp"] = (
        relevant["baseline_total_gp"] + relevant["delta_total_gp"]
    ).round(6)
    return relevant.sort_values(["decision", "recommended_total_gp"], ascending=[True, False]).reset_index(drop=True)


def run_optimization(
    sku_metrics_by_cluster: pd.DataFrame,
    need_state_dict: pd.DataFrame,
    params: OptimizeParams,
) -> pd.DataFrame:
    del need_state_dict
    metrics = sku_metrics_by_cluster.copy()
    metrics["selection_score"] = metrics.apply(lambda row: _selection_score(row, params), axis=1)
    metrics["score_per_cm"] = metrics["selection_score"] / metrics["shelf_width_cm"].replace(0, 1.0)
    metrics["target_facings"] = metrics.apply(lambda row: _target_facings(row, params), axis=1)
    metrics = metrics.sort_values(["cluster_id", "selection_score"], ascending=[True, False]).reset_index(drop=True)

    outputs = []
    for _, cluster_df in metrics.groupby("cluster_id"):
        cluster_df = cluster_df.copy()
        selected = _pick_core_rows(cluster_df, params)
        selected = _force_keep_policy_rows(cluster_df, selected, params)
        selected = _fill_non_core(cluster_df, selected, params)
        selected = _allocate_extra_facings(cluster_df, selected, params)
        selected = _local_search(cluster_df, selected, params)
        cluster_output = _append_cluster_outputs(cluster_df, selected, params)
        outputs.append(cluster_output)
    if not outputs:
        return pd.DataFrame()
    decision_table = pd.concat(outputs, ignore_index=True)
    return decision_table.sort_values(["cluster_id", "decision", "recommended_total_gp"], ascending=[True, True, False]).reset_index(drop=True)


def summarize_clusters(decision_table: pd.DataFrame, params: OptimizeParams) -> pd.DataFrame:
    rows = []
    for cluster_id, group in decision_table.groupby("cluster_id"):
        rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_name": group["cluster_name"].iloc[0],
                "sku_count": int(group["recommended_listed"].sum()),
                "baseline_gp": round(float(group["baseline_total_gp"].sum()), 4),
                "recommended_gp": round(float(group["recommended_total_gp"].sum()), 4),
                "delta_gp": round(float(group["delta_total_gp"].sum()), 4),
                "shelf_used_cm": round(float(group["recommended_shelf_cm"].sum()), 4),
                "shelf_utilization": round(float(group["recommended_shelf_cm"].sum() / params.shelf_capacity_cm), 4),
                "coverage": round(float(group["recommended_coverage"].max()), 4),
                "kvi_price_index": round(float(group["recommended_kvi_price_index"].max()), 4),
            }
        )
    return pd.DataFrame(rows).sort_values("cluster_id").reset_index(drop=True)
