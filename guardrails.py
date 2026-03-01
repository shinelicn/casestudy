from __future__ import annotations

import pandas as pd

from modules.cdt import required_core_coverage_groups
from modules.optimize import OptimizeParams


def validate_cluster_constraints(
    cluster_rows: pd.DataFrame,
    params: OptimizeParams,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    selected = cluster_rows[cluster_rows["recommended_facings"] > 0].copy()
    if selected.empty:
        errors.append("No selected SKU in cluster.")
        return False, errors
    if float(selected["recommended_shelf_cm"].sum()) > params.shelf_capacity_cm + 1e-9:
        errors.append("Shelf capacity exceeded.")
    if (selected["recommended_facings"] > params.max_facings_per_sku).any():
        errors.append("Max facings per SKU violated.")
    core_selected = selected[selected["is_core"] == 1]
    if not core_selected.empty and (core_selected["recommended_facings"] < params.min_facings_core).any():
        errors.append("Min facings for core SKU violated.")
    covered = set(core_selected["coverage_group_id"].tolist())
    missing = sorted(set(required_core_coverage_groups()) - covered)
    if missing:
        errors.append(f"Core coverage missing: {', '.join(missing)}")
    return len(errors) == 0, errors


def validate_all_clusters(
    decision_table: pd.DataFrame,
    need_state_dict: pd.DataFrame,
    params: OptimizeParams,
) -> list[str]:
    del need_state_dict
    issues: list[str] = []
    for cluster_id, group in decision_table.groupby("cluster_id"):
        ok, errors = validate_cluster_constraints(group, params)
        if not ok:
            for error in errors:
                issues.append(f"{cluster_id}: {error}")
    return issues


def build_guardrail_tables(
    decision_table: pd.DataFrame,
    need_state_dict: pd.DataFrame,
    params: OptimizeParams,
) -> dict[str, pd.DataFrame]:
    del need_state_dict
    required = set(required_core_coverage_groups())
    coverage_rows = []
    brand_rows = []
    kvi_rows = []
    for cluster_id, group in decision_table.groupby("cluster_id"):
        selected = group[group["recommended_facings"] > 0].copy()
        core_selected = selected[selected["is_core"] == 1]
        covered = set(core_selected["coverage_group_id"])
        missing = sorted(required - covered)
        coverage_rows.append(
            {
                "cluster_id": cluster_id,
                "required_core_states": len(required),
                "covered_core_states": len(required & covered),
                "coverage_ratio": round(len(required & covered) / max(len(required), 1), 4),
                "alert": "RED" if missing else "GREEN",
                "missing_states": ", ".join(missing) if missing else "OK",
            }
        )

        if not selected.empty:
            brand_mix = (selected.groupby("brand")["recommended_facings"].sum() / selected["recommended_facings"].sum()).sort_values(ascending=False)
            dominant_brand = brand_mix.index[0]
            dominant_share = float(brand_mix.iloc[0])
        else:
            dominant_brand = ""
            dominant_share = 0.0
        brand_rows.append(
            {
                "cluster_id": cluster_id,
                "dominant_brand": dominant_brand,
                "dominant_share": round(dominant_share, 4),
                "brand_cap": params.brand_cap,
                "alert": "AMBER" if dominant_share >= params.brand_cap else "GREEN",
            }
        )

        kvi_rows.append(
            {
                "cluster_id": cluster_id,
                "baseline_kvi_price_index": 1.0,
                "recommended_kvi_price_index": round(float(group["recommended_kvi_price_index"].max()), 4),
                "alert": "RED" if float(group["recommended_kvi_price_index"].max()) > 1.03 else "GREEN",
            }
        )

    osa = (
        decision_table[
            [
                "cluster_id",
                "sku_id",
                "decision",
                "recommended_facings",
                "baseline_osa_risk",
                "recommended_osa_risk",
                "replacement_sku_id",
            ]
        ]
        .sort_values("recommended_osa_risk", ascending=False)
        .reset_index(drop=True)
    )
    return {
        "coverage": pd.DataFrame(coverage_rows),
        "kvi_index": pd.DataFrame(kvi_rows),
        "osa_risk": osa,
        "brand_cap": pd.DataFrame(brand_rows),
    }
