from __future__ import annotations

import json
from typing import Any

import pandas as pd


def build_reason_catalog() -> pd.DataFrame:
    rows = [
        {
            "reason_code": "DUPLICATION_HIGH",
            "definition": "同一 need_state 下重复 SKU 偏多，且该 SKU 的机会成本更高。",
            "trigger_rule": "decision=delist 且 duplicate_count>=2 且存在替代者。",
            "evidence_fields": "duplicate_count,replacement_sku_id,keep_cost",
        },
        {
            "reason_code": "VELOCITY_LOW",
            "definition": "动销位于 cluster 低分位，继续保留会拖累坪效。",
            "trigger_rule": "decision=delist 且 velocity_pct<=0.35。",
            "evidence_fields": "weekly_units,velocity_pct",
        },
        {
            "reason_code": "MARGIN_LOW",
            "definition": "单位毛利或毛利率处于低分位。",
            "trigger_rule": "margin_pct<=0.35。",
            "evidence_fields": "unit_margin,margin_rate,margin_pct",
        },
        {
            "reason_code": "SPACE_INEFFICIENT",
            "definition": "每厘米货架毛利偏低，空间利用效率差。",
            "trigger_rule": "space_efficiency_pct<=0.35。",
            "evidence_fields": "gp_per_cm,space_efficiency_pct,shelf_width_cm",
        },
        {
            "reason_code": "HALO_HIGH",
            "definition": "该 SKU 能明显带动湿巾/护臀霜联动毛利。",
            "trigger_rule": "halo_pct>=0.70 或 halo_gp>0。",
            "evidence_fields": "halo_gp,halo_support,halo_lift,halo_pct",
        },
        {
            "reason_code": "COVERAGE_GAP_FIX",
            "definition": "用于填补核心 need_state 覆盖缺口。",
            "trigger_rule": "coverage_fix_flag=1。",
            "evidence_fields": "coverage_group_id,baseline_coverage,recommended_coverage",
        },
        {
            "reason_code": "KVI_PROTECT",
            "definition": "KVI 需要保留，避免价格形象和流量受损。",
            "trigger_rule": "is_kvi=1 且 recommended_listed=1。",
            "evidence_fields": "is_kvi,baseline_kvi_price_index,recommended_kvi_price_index",
        },
        {
            "reason_code": "OSA_RISK_HIGH",
            "definition": "缺货风险偏高，需要通过保留/加面数或补货动作保护。",
            "trigger_rule": "recommended_osa_risk>=0.90。",
            "evidence_fields": "baseline_osa_risk,recommended_osa_risk,recommended_facings",
        },
        {
            "reason_code": "PROMO_DEPENDENT",
            "definition": "过度依赖促销，非促销期动销支撑不足。",
            "trigger_rule": "promo_dependency_score>=0.45。",
            "evidence_fields": "promo_share,promo_dependency_score,non_promo_units",
        },
        {
            "reason_code": "BRAND_CAP_TRIGGER",
            "definition": "品牌占比接近或触发上限，需要结构平衡。",
            "trigger_rule": "brand_cap_pressure_flag=1。",
            "evidence_fields": "brand,baseline_brand_share,recommended_brand_share,brand_cap",
        },
        {
            "reason_code": "FORMAT_SHIFT",
            "definition": "客群对腰贴/拉拉裤的偏好发生迁移。",
            "trigger_rule": "abs(format_trend)>=0.05。",
            "evidence_fields": "format,format_trend",
        },
        {
            "reason_code": "PACK_TIER_OPT",
            "definition": "大包/中包/小包结构需要顺着需求变化做优化。",
            "trigger_rule": "abs(pack_tier_gap)>=0.05。",
            "evidence_fields": "pack_tier,pack_tier_gap",
        },
        {
            "reason_code": "PREMIUM_DEPTH_FOCUS",
            "definition": "高净值集群主动压缩低价/私牌，把空间让给高端与拉拉裤。",
            "trigger_rule": "cluster_id=C1 且命中高端倾斜规则。",
            "evidence_fields": "cluster_name,price_tier,is_private_label,format",
        },
        {
            "reason_code": "STOCKUP_PACK_RULE",
            "definition": "囤货型大仓优先量贩装，并强保护 KVI。",
            "trigger_rule": "cluster_id=C2 且命中量贩装或 KVI 保护规则。",
            "evidence_fields": "cluster_name,pack_tier,is_kvi,baseline_facings,recommended_facings",
        },
        {
            "reason_code": "EMERGENCY_ASSORTMENT_FOCUS",
            "definition": "紧急补缺店只保留头部品牌与便携规格，强压长尾。",
            "trigger_rule": "cluster_id=C3 且命中头部品牌/禁大箱规则。",
            "evidence_fields": "cluster_name,brand_rank_in_cluster,pack_tier",
        },
        {
            "reason_code": "VALUE_DEFENSE_MATRIX",
            "definition": "价值防守集群提高经济型与私牌权重，并避免低价功能重复。",
            "trigger_rule": "cluster_id=C4 且命中低价防守规则。",
            "evidence_fields": "cluster_name,price_tier,is_private_label,duplicate_count",
        },
    ]
    return pd.DataFrame(rows)


def loads_json_cell(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None or value == "":
        return [] if value == "" else {}
    return json.loads(value)


def _evidence_fields_for(code: str) -> list[str]:
    catalog = build_reason_catalog().set_index("reason_code")
    return [field.strip() for field in catalog.loc[code, "evidence_fields"].split(",")]


def _collect_evidence(row: pd.Series, code: str) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for field in _evidence_fields_for(code):
        value = row.get(field)
        if isinstance(value, float):
            evidence[field] = round(value, 6)
        else:
            evidence[field] = value
    return evidence


def derive_reason_bundle(row: pd.Series) -> dict[str, Any]:
    codes: list[str] = []
    decision = row["decision"]

    if decision == "delist" and row["duplicate_count"] >= 2 and row["replacement_sku_id"]:
        codes.append("DUPLICATION_HIGH")
    if decision == "delist" and row["velocity_pct"] <= 0.35:
        codes.append("VELOCITY_LOW")
    if row["margin_pct"] <= 0.35:
        codes.append("MARGIN_LOW")
    if row["space_efficiency_pct"] <= 0.35:
        codes.append("SPACE_INEFFICIENT")
    if decision in {"retain", "add"} and (row["halo_pct"] >= 0.70 or row["halo_gp"] > 0):
        codes.append("HALO_HIGH")
    if decision in {"retain", "add"} and row["coverage_fix_flag"] == 1:
        codes.append("COVERAGE_GAP_FIX")
    if row["is_kvi"] == 1 and row["recommended_listed"] == 1:
        codes.append("KVI_PROTECT")
    if decision in {"retain", "add"} and row["recommended_osa_risk"] >= 0.90:
        codes.append("OSA_RISK_HIGH")
    if decision == "delist" and row["promo_dependency_score"] >= 0.45:
        codes.append("PROMO_DEPENDENT")
    if row["brand_cap_pressure_flag"] == 1:
        codes.append("BRAND_CAP_TRIGGER")
    if (
        (decision in {"retain", "add"} and row["format_trend"] >= 0.05)
        or (decision == "delist" and row["format_trend"] <= -0.05)
    ):
        codes.append("FORMAT_SHIFT")
    if (
        (decision in {"retain", "add"} and row["pack_tier_gap"] >= 0.05)
        or (decision == "delist" and row["pack_tier_gap"] <= -0.05)
    ):
        codes.append("PACK_TIER_OPT")
    if row["cluster_id"] == "C1" and (
        (decision == "delist" and (row["price_tier"] == "good" or row["is_private_label"] == 1))
        or (decision in {"retain", "add"} and (row["price_tier"] == "best" or row["format"] == "拉拉裤"))
    ):
        codes.append("PREMIUM_DEPTH_FOCUS")
    if row["cluster_id"] == "C2" and (
        row["pack_tier"] == "bulk_pack" or (row["is_kvi"] == 1 and row["recommended_listed"] == 1)
    ):
        codes.append("STOCKUP_PACK_RULE")
    if row["cluster_id"] == "C3" and (
        row["brand_rank_in_cluster"] <= 3 or row["pack_tier"] == "bulk_pack"
    ):
        codes.append("EMERGENCY_ASSORTMENT_FOCUS")
    if row["cluster_id"] == "C4" and (
        row["price_tier"] == "good" or row["is_private_label"] == 1 or row["duplicate_count"] >= 2
    ):
        codes.append("VALUE_DEFENSE_MATRIX")

    if not codes:
        if decision == "delist":
            codes = ["SPACE_INEFFICIENT"]
        elif decision == "add":
            codes = ["COVERAGE_GAP_FIX"] if row["is_core"] == 1 else ["HALO_HIGH"]
        else:
            codes = ["KVI_PROTECT"] if row["is_kvi"] == 1 else ["HALO_HIGH"]

    details = [{"reason_code": code, "evidence": _collect_evidence(row, code)} for code in codes]
    lead_code = codes[0]
    if decision == "delist":
        summary = (
            f"下架 {row['sku_id']}：同需求下它的机会成本更高，优先把空间让给 {row['replacement_sku_id'] or '更强替代者'}。"
        )
    elif decision == "add":
        summary = (
            f"上新 {row['sku_id']}：补覆盖并争取增量毛利，推荐上 {int(row['recommended_facings'])} 面。"
        )
    else:
        if row["recommended_facings"] > row["baseline_facings"]:
            summary = (
                f"保留 {row['sku_id']} 并加面到 {int(row['recommended_facings'])} 面：动销或联动价值更高，需要降低缺货。"
            )
        elif row["recommended_facings"] < row["baseline_facings"]:
            summary = (
                f"保留 {row['sku_id']} 但减面到 {int(row['recommended_facings'])} 面：保留覆盖，同时回收低效空间。"
            )
        else:
            summary = f"保留 {row['sku_id']}：它仍是当前组合里的有效组成部分。"

    operation_instruction = (
        f"{'下架' if decision == 'delist' else '上新' if decision == 'add' else '调整'} {row['sku_id']}："
        f"从 {int(row['baseline_facings'])} 面调整到 {int(row['recommended_facings'])} 面。"
    )
    risk_summary = (
        "注意观察 2 周销量与缺货"
        if row["recommended_osa_risk"] >= 0.90
        else "主要风险是增量不及预期"
        if decision == "add"
        else "主要风险较低"
    )
    rollback_hint = (
        f"如连续 2 周周销低于基线 90%，回滚到 {int(row['baseline_facings'])} 面。"
    )
    counterfactual = {
        "replacement_sku_id": row["replacement_sku_id"],
        "replacement_total_gp": round(float(row["replacement_total_gp"]), 6),
        "opportunity_cost_gp": round(float(row["opportunity_cost_gp"]), 6),
        "constraint_violation_flag": int(row["constraint_violation_flag"]),
        "keep_cost": round(float(row["keep_cost"]), 6),
        "message": (
            "如果保留它，将挤占更高 GP 的替代者，且可能超出货架容量。"
            if int(row["constraint_violation_flag"]) == 1
            else "如果保留它，不一定立刻违反硬约束，但会放弃更高 GP 的替代者。"
        ),
    }
    contribution = {
        "delta_total_gp": round(float(row["delta_total_gp"]), 6),
        "delta_direct_gp": round(float(row["delta_direct_gp"]), 6),
        "delta_halo_gp": round(float(row["delta_halo_gp"]), 6),
        "delta_dup_penalty": round(float(row["delta_dup_penalty"]), 6),
        "delta_kvi_penalty": round(float(row["delta_kvi_penalty"]), 6),
        "delta_ops_penalty": round(float(row["delta_ops_penalty"]), 6),
    }
    return {
        "reason_codes": codes,
        "reason_details": details,
        "one_line_summary": summary,
        "operation_instruction": operation_instruction,
        "risk_summary": risk_summary,
        "rollback_hint": rollback_hint,
        "counterfactual": counterfactual,
        "contribution": contribution,
        "lead_reason_code": lead_code,
    }


def explain_decision_table(decision_table: pd.DataFrame, reason_catalog: pd.DataFrame | None = None) -> pd.DataFrame:
    del reason_catalog
    explained = decision_table.copy()
    bundles = explained.apply(derive_reason_bundle, axis=1)
    explained["reason_codes"] = bundles.map(lambda bundle: json.dumps(bundle["reason_codes"], ensure_ascii=False))
    explained["reason_details"] = bundles.map(lambda bundle: json.dumps(bundle["reason_details"], ensure_ascii=False))
    explained["one_line_summary"] = bundles.map(lambda bundle: bundle["one_line_summary"])
    explained["operation_instruction"] = bundles.map(lambda bundle: bundle["operation_instruction"])
    explained["risk_summary"] = bundles.map(lambda bundle: bundle["risk_summary"])
    explained["rollback_hint"] = bundles.map(lambda bundle: bundle["rollback_hint"])
    explained["counterfactual"] = bundles.map(lambda bundle: json.dumps(bundle["counterfactual"], ensure_ascii=False))
    explained["contribution_json"] = bundles.map(lambda bundle: json.dumps(bundle["contribution"], ensure_ascii=False))
    explained["lead_reason_code"] = bundles.map(lambda bundle: bundle["lead_reason_code"])
    return explained


def build_explain_trace(decision_table: pd.DataFrame) -> dict[str, Any]:
    trace = []
    for row in decision_table.itertuples():
        trace.append(
            {
                "cluster_id": row.cluster_id,
                "sku_id": row.sku_id,
                "decision": row.decision,
                "data_refs": [
                    {"table": "transactions", "fields": ["qty", "price", "promo_flag"]},
                    {"table": "products", "fields": ["unit_cost", "shelf_width_cm", "is_kvi", "is_core"]},
                    {"table": "stores", "fields": ["store_format", "income_proxy", "baseline_gp"]},
                    {"table": "inventory_daily", "fields": ["on_hand", "oos_flag"]},
                    {"table": "baseline_assortment", "fields": ["is_listed", "facings"]},
                    {
                        "table": "derived.sku_metrics_by_cluster",
                        "fields": [
                            "weekly_units",
                            "weekly_gp",
                            "gp_per_cm",
                            "oos_rate",
                            "price_index",
                            "pred_units",
                            "pred_direct_gp",
                        ],
                    },
                    {
                        "table": "derived.halo_rules",
                        "fields": ["support", "confidence", "lift", "halo_profit"],
                    },
                ],
                "formulas": [
                    "pred_units = historical weekly units * format/pack trend adjustment * OOS adjustment * promo dependency adjustment",
                    "delta_total_gp = delta_direct_gp + delta_halo_gp - delta_dup_penalty - delta_kvi_penalty - delta_ops_penalty",
                    "keep_cost = opportunity_cost_gp + constraint_violation_flag",
                ],
                "reason_codes": loads_json_cell(row.reason_codes),
                "counterfactual": loads_json_cell(row.counterfactual),
                "compare_panel": {
                    "baseline": {
                        "direct_gp": row.baseline_direct_gp,
                        "halo_gp": row.baseline_halo_gp,
                        "total_gp": row.baseline_total_gp,
                        "shelf_cm": row.baseline_shelf_cm,
                        "coverage": row.baseline_coverage,
                        "kvi_price_index": row.baseline_kvi_price_index,
                        "osa_risk": row.baseline_osa_risk,
                    },
                    "recommended": {
                        "direct_gp": row.recommended_direct_gp,
                        "halo_gp": row.recommended_halo_gp,
                        "total_gp": row.recommended_total_gp,
                        "shelf_cm": row.recommended_shelf_cm,
                        "coverage": row.recommended_coverage,
                        "kvi_price_index": row.recommended_kvi_price_index,
                        "osa_risk": row.recommended_osa_risk,
                    },
                },
            }
        )
    return {"trace": trace}
