from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from modules.cdt import attach_need_states, build_need_state_dict
from modules.clustering import assign_clusters, build_store_features, profile_clusters
from modules.data_gen import generate_demo_data
from modules.experiment import simulate_pilot
from modules.explain import build_explain_trace, build_reason_catalog, explain_decision_table
from modules.exports import build_export_bundle, write_export_bundle
from modules.forecast import build_sku_metrics_by_cluster
from modules.guardrails import build_guardrail_tables, validate_all_clusters
from modules.halo import build_halo_rules, summarize_halo_scores
from modules.optimize import OptimizeParams, run_optimization, summarize_clusters


def build_demo_artifacts(
    seed: int = 7,
    n_clusters: int = 4,
    shelf_capacity_cm: float = 180.0,
    min_facings_core: int = 2,
    max_facings_per_sku: int = 4,
    brand_cap: float = 0.42,
) -> dict[str, Any]:
    raw_tables = generate_demo_data(seed=seed)
    products = attach_need_states(raw_tables["products"])
    raw_tables["products"] = products
    need_state_dict = build_need_state_dict(products)
    store_features = build_store_features(
        transactions=raw_tables["transactions"],
        stores=raw_tables["stores"],
        inventory_daily=raw_tables["inventory_daily"],
        products=products,
    )
    clustered_stores = assign_clusters(store_features, raw_tables["stores"], n_clusters=4)
    cluster_profile, preference_tables = profile_clusters(
        clustered_stores=clustered_stores,
        transactions=raw_tables["transactions"],
        products=products,
    )
    halo_rules = build_halo_rules(
        transactions=raw_tables["transactions"],
        products=products,
        clustered_stores=clustered_stores,
    )
    halo_scores = summarize_halo_scores(halo_rules)
    sku_metrics = build_sku_metrics_by_cluster(
        transactions=raw_tables["transactions"],
        products=products,
        clustered_stores=clustered_stores,
        inventory_daily=raw_tables["inventory_daily"],
        baseline_assortment=raw_tables["baseline_assortment"],
        halo_scores=halo_scores,
    )
    params = OptimizeParams(
        shelf_capacity_cm=shelf_capacity_cm,
        min_facings_core=min_facings_core,
        max_facings_per_sku=max_facings_per_sku,
        brand_cap=brand_cap,
    )
    decision_base = run_optimization(
        sku_metrics_by_cluster=sku_metrics,
        need_state_dict=need_state_dict,
        params=params,
    )
    reason_catalog = build_reason_catalog()
    decision_table = explain_decision_table(decision_base, reason_catalog)
    guardrails = build_guardrail_tables(
        decision_table=decision_table,
        need_state_dict=need_state_dict,
        params=params,
    )
    constraint_report = validate_all_clusters(
        decision_table=decision_table,
        need_state_dict=need_state_dict,
        params=params,
    )
    cluster_summary = summarize_clusters(decision_table, params)
    pilot_store_results, pilot_summary = simulate_pilot(
        clustered_stores=clustered_stores,
        decision_table=decision_table,
        seed=seed,
    )
    explain_trace = build_explain_trace(decision_table)
    export_bundle = build_export_bundle(
        decision_table=decision_table,
        clustered_stores=clustered_stores,
        guardrails=guardrails,
        explain_trace=explain_trace,
        pilot_summary=pilot_summary,
        params=params,
    )
    return {
        "raw_tables": raw_tables,
        "need_state_dict": need_state_dict,
        "store_features": store_features,
        "clustered_stores": clustered_stores,
        "cluster_profile": cluster_profile,
        "preference_tables": preference_tables,
        "halo_rules": halo_rules,
        "sku_metrics_by_cluster": sku_metrics,
        "decision_table": decision_table,
        "guardrails": guardrails,
        "constraint_report": constraint_report,
        "cluster_summary": cluster_summary,
        "pilot_store_results": pilot_store_results,
        "pilot_summary": pilot_summary,
        "store_task_sheet": export_bundle["store_task_sheet"],
        "planogram_proxy": export_bundle["planogram_proxy"],
        "one_pager_md": export_bundle["one_pager_md"],
        "playbook_md": export_bundle["playbook_md"],
        "explain_trace": explain_trace,
        "reason_catalog": reason_catalog,
        "params": params,
        "export_bundle": export_bundle,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Explainable diaper assortment optimization demo")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--clusters", type=int, default=4)
    parser.add_argument("--shelf-capacity", type=float, default=180.0, dest="shelf_capacity_cm")
    parser.add_argument("--min-facings-core", type=int, default=2)
    parser.add_argument("--max-facings-per-sku", type=int, default=4)
    parser.add_argument("--brand-cap", type=float, default=0.42)
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    args = parser.parse_args()

    payload = build_demo_artifacts(
        seed=args.seed,
        n_clusters=4,
        shelf_capacity_cm=args.shelf_capacity_cm,
        min_facings_core=args.min_facings_core,
        max_facings_per_sku=args.max_facings_per_sku,
        brand_cap=args.brand_cap,
    )
    write_export_bundle(payload["export_bundle"], args.out_dir)
    print(f"Outputs written to {args.out_dir.resolve()}")


if __name__ == "__main__":
    main()
