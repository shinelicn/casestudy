from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from modules.optimize import OptimizeParams


def build_store_task_sheet(decision_table: pd.DataFrame, clustered_stores: pd.DataFrame) -> pd.DataFrame:
    stores = clustered_stores[["store_id", "cluster_id", "store_format", "region"]].drop_duplicates()
    tasks = stores.merge(decision_table, on="cluster_id", how="left")
    tasks["task_type"] = tasks["decision"].map({"add": "上新", "delist": "下架", "retain": "改面数"})
    tasks["replenish_advice"] = tasks.apply(
        lambda row: "建议同步补货阈值上调" if row["recommended_osa_risk"] >= 0.90 and row["recommended_facings"] > 0 else "",
        axis=1,
    )
    keep_cols = [
        "store_id",
        "cluster_id",
        "store_format",
        "region",
        "sku_id",
        "task_type",
        "baseline_facings",
        "recommended_facings",
        "operation_instruction",
        "one_line_summary",
        "lead_reason_code",
        "risk_summary",
        "rollback_hint",
        "replenish_advice",
    ]
    return tasks[keep_cols].sort_values(["store_id", "task_type", "sku_id"]).reset_index(drop=True)


def build_planogram_proxy(decision_table: pd.DataFrame) -> pd.DataFrame:
    selected = decision_table[decision_table["recommended_facings"] > 0].copy()
    selected = selected.sort_values(
        ["cluster_id", "coverage_group_id", "recommended_total_gp", "sku_id"],
        ascending=[True, True, False, True],
    )
    rows = []
    for cluster_id, group in selected.groupby("cluster_id"):
        cursor = 0.0
        slot = 1
        for row in group.itertuples():
            width = float(row.recommended_shelf_cm)
            rows.append(
                {
                    "cluster_id": cluster_id,
                    "slot": slot,
                    "cm_start": round(cursor, 4),
                    "cm_end": round(cursor + width, 4),
                    "sku_id": row.sku_id,
                    "brand": row.brand,
                    "coverage_group_id": row.coverage_group_id,
                    "recommended_facings": row.recommended_facings,
                    "one_line_summary": row.one_line_summary,
                }
            )
            cursor += width
            slot += 1
    return pd.DataFrame(rows)


def build_one_pager(
    decision_table: pd.DataFrame,
    guardrails: dict[str, pd.DataFrame],
    pilot_summary: pd.DataFrame,
    params: OptimizeParams,
) -> str:
    total_delta = float(decision_table["delta_total_gp"].sum())
    direct = float(decision_table["delta_direct_gp"].sum())
    halo = float(decision_table["delta_halo_gp"].sum())
    dup = float(decision_table["delta_dup_penalty"].sum())
    kvi = float(decision_table["delta_kvi_penalty"].sum())
    ops = float(decision_table["delta_ops_penalty"].sum())
    add_count = int((decision_table["decision"] == "add").sum())
    delist_count = int((decision_table["decision"] == "delist").sum())
    retain_count = int((decision_table["decision"] == "retain").sum())
    coverage_red = guardrails["coverage"][guardrails["coverage"]["alert"] == "RED"]["cluster_id"].tolist()
    brand_amber = guardrails["brand_cap"][guardrails["brand_cap"]["alert"] == "AMBER"]["cluster_id"].tolist()
    pilot_lift = float(pilot_summary.loc[pilot_summary["group"] == "treatment", "post_gp"].mean() - pilot_summary.loc[pilot_summary["group"] == "treatment", "pre_gp"].mean())
    return f"""# 采购经理 1 页复盘

## 本次策略
- 策略对象：纸尿裤 cluster 级组合优化，按 need state 补齐覆盖，再按 direct GP + halo GP 排序补充 SKU 和 facings。
- 决策结构：retain {retain_count} 个，add {add_count} 个，delist {delist_count} 个。
- 硬约束：货架上限 {params.shelf_capacity_cm:.1f} cm，核心 need state 最低 {params.min_facings_core} 面，单 SKU 最多 {params.max_facings_per_sku} 面。

## 收益拆分
- 总增量 GP：{total_delta:.2f}
- Direct GP 增量：{direct:.2f}
- Halo GP 增量：{halo:.2f}
- 重复惩罚变化：{dup:.2f}
- KVI 惩罚变化：{kvi:.2f}
- 操作惩罚变化：{ops:.2f}

## 主要牺牲
- 下架动作主要牺牲的是被替换 SKU 的原有销量和陈列稳定性。
- 对高促销依赖 SKU，系统主动牺牲短期促销销量，换取更稳定的非促销结构。
- 若品牌占比过高，系统会牺牲强势品牌的边际面数，换取整体结构安全。

## 风险
- Coverage 红色告警 cluster：{", ".join(coverage_red) if coverage_red else "无"}
- Brand cap 告警 cluster：{", ".join(brand_amber) if brand_amber else "无"}
- 店长执行风险集中在高 OSA SKU，需要配合补货。

## 回滚
- 任一调整后连续 2 周周销低于基线 90%，回滚到 baseline facings。
- 若 KVI 价格指数超过 1.03，优先恢复 KVI facings。
- 若试点门店 post vs pre 的 treatment 提升转负，暂停扩大范围。当前 treatment 组模拟 post-pre 为 {pilot_lift:.2f}。
"""


def build_playbook(pilot_summary: pd.DataFrame) -> str:
    treatment = pilot_summary[pilot_summary["group"] == "treatment"].iloc[0]
    control = pilot_summary[pilot_summary["group"] == "control"].iloc[0]
    return f"""# 试点 Playbook

## 试点设计
- 单位：门店
- 分组：同 trade_area 内 treatment / control 对照
- 观测期：建议 8 周

## 当前模拟结果
- Treatment pre_gp: {treatment['pre_gp']:.2f}
- Treatment post_gp: {treatment['post_gp']:.2f}
- Control pre_gp: {control['pre_gp']:.2f}
- Control post_gp: {control['post_gp']:.2f}

## 守门指标
- Coverage 不掉线
- KVI price index 不超过 1.03
- OSA 风险高的 SKU 必须同步补货

## 回滚触发
- 连续 2 周 treatment uplift 为负
- 门店执行率低于 80%
- KVI 或 OSA 告警进入红色
"""


def build_export_bundle(
    decision_table: pd.DataFrame,
    clustered_stores: pd.DataFrame,
    guardrails: dict[str, pd.DataFrame],
    explain_trace: dict[str, Any],
    pilot_summary: pd.DataFrame,
    params: OptimizeParams,
) -> dict[str, Any]:
    store_task_sheet = build_store_task_sheet(decision_table, clustered_stores)
    planogram_proxy = build_planogram_proxy(decision_table)
    one_pager_md = build_one_pager(decision_table, guardrails, pilot_summary, params)
    playbook_md = build_playbook(pilot_summary)
    return {
        "decision_table": decision_table,
        "store_task_sheet": store_task_sheet,
        "planogram_proxy": planogram_proxy,
        "explain_trace": explain_trace,
        "one_pager_md": one_pager_md,
        "playbook_md": playbook_md,
    }


def write_export_bundle(bundle: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle["decision_table"].to_csv(out_dir / "decision_table.csv", index=False)
    bundle["store_task_sheet"].to_csv(out_dir / "store_task_sheet.csv", index=False)
    bundle["planogram_proxy"].to_csv(out_dir / "planogram_proxy.csv", index=False)
    (out_dir / "one_pager.md").write_text(bundle["one_pager_md"], encoding="utf-8")
    (out_dir / "playbook.md").write_text(bundle["playbook_md"], encoding="utf-8")
    (out_dir / "explain_trace.json").write_text(
        json.dumps(bundle["explain_trace"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def json_to_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
