from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from cli import build_demo_artifacts
from modules.explain import build_reason_catalog, loads_json_cell
from modules.exports import json_to_bytes, text_to_bytes, to_csv_bytes

st.set_page_config(page_title="零售AI决策产品 DEMO", layout="wide")


@st.cache_data(show_spinner=False)
def load_payload(
    seed: int,
    shelf_capacity_cm: float,
    min_facings_core: int,
    max_facings_per_sku: int,
    brand_cap: float,
) -> dict[str, object]:
    return build_demo_artifacts(
        seed=seed,
        n_clusters=4,
        shelf_capacity_cm=shelf_capacity_cm,
        min_facings_core=min_facings_core,
        max_facings_per_sku=max_facings_per_sku,
        brand_cap=brand_cap,
    )


def render_overview(payload: dict[str, object], params: dict[str, float]) -> None:
    summary = payload["cluster_summary"]
    decision_table = payload["decision_table"]
    pilot_summary = payload["pilot_summary"]
    st.title("纸尿裤品类商品组合优化 DEMO")
    st.markdown(
        """
受众写死在产品里：
- 采购经理：看毛利、品牌结构、价格带、重复 SKU、谈判与策略一致性
- 店长：看卖不卖得动、缺货风险、货架空间、执行是否清晰

每条推荐都提供三层解释：
- 一句话结论：给店长直接执行
- 结构化原因码：给采购做策略复盘
- 证据面板：展示基线 vs 推荐 + 收益拆解 + 风险
"""
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cluster 数", int(summary["cluster_id"].nunique()))
    c2.metric("推荐 SKU 数", int((decision_table["recommended_facings"] > 0).sum()))
    c3.metric("周度总 GP 增量", f"{decision_table['delta_total_gp'].sum():,.1f}")
    c4.metric("平均货架利用率", f"{summary['shelf_utilization'].mean():.1%}")
    st.markdown("### 参数")
    st.json(params)
    st.markdown("### Cluster 总览 KPI")
    st.dataframe(summary, use_container_width=True)
    st.markdown("### 试点评估（模拟）")
    st.dataframe(pilot_summary, use_container_width=True)


def render_cluster_profile(payload: dict[str, object]) -> None:
    cluster_profile = payload["cluster_profile"]
    preference_tables = payload["preference_tables"]
    st.title("Cluster Profile")
    st.dataframe(cluster_profile, use_container_width=True)
    cluster_options = {
        row["cluster_id"]: f"{row['cluster_id']} | {row['cluster_name']}"
        for _, row in cluster_profile[["cluster_id", "cluster_name"]].drop_duplicates().iterrows()
    }
    cluster_id = st.selectbox("选择 Cluster", list(cluster_options.keys()), format_func=lambda x: cluster_options[x], key="cluster_profile")
    for title, table in preference_tables.items():
        st.markdown(f"### {title}")
        subset = table[table["cluster_id"] == cluster_id]
        st.dataframe(subset, use_container_width=True)


def render_recommendation(payload: dict[str, object]) -> None:
    decision_table = payload["decision_table"]
    task_sheet = payload["store_task_sheet"]
    st.title("Recommendation")
    cluster_meta = decision_table[["cluster_id", "cluster_name"]].drop_duplicates().sort_values("cluster_id")
    cluster_options = {row["cluster_id"]: f"{row['cluster_id']} | {row['cluster_name']}" for _, row in cluster_meta.iterrows()}
    cluster_id = st.selectbox("选择 Cluster", list(cluster_options.keys()), format_func=lambda x: cluster_options[x], key="rec_cluster")
    cluster_rows = decision_table[decision_table["cluster_id"] == cluster_id].copy()
    display_cols = [
        "sku_id",
        "decision",
        "baseline_facings",
        "recommended_facings",
        "one_line_summary",
        "operation_instruction",
        "delta_total_gp",
        "risk_summary",
        "rollback_hint",
    ]
    st.markdown("### 门店视角推荐清单")
    st.dataframe(cluster_rows[display_cols], use_container_width=True)
    sample_store = (
        task_sheet[task_sheet["cluster_id"] == cluster_id]["store_id"].drop_duplicates().sort_values().tolist()
    )
    if sample_store:
        store_id = st.selectbox("查看店长工单（门店）", sample_store, key="store_task")
        st.dataframe(task_sheet[task_sheet["store_id"] == store_id], use_container_width=True)


def render_explain(payload: dict[str, object]) -> None:
    decision_table = payload["decision_table"]
    reason_catalog = build_reason_catalog()
    st.title("Explain")
    cluster_meta = decision_table[["cluster_id", "cluster_name"]].drop_duplicates().sort_values("cluster_id")
    cluster_options = {row["cluster_id"]: f"{row['cluster_id']} | {row['cluster_name']}" for _, row in cluster_meta.iterrows()}
    cluster_id = st.selectbox("选择 Cluster", list(cluster_options.keys()), format_func=lambda x: cluster_options[x], key="exp_cluster")
    sku_options = decision_table[decision_table["cluster_id"] == cluster_id]["sku_id"].tolist()
    sku_id = st.selectbox("选择 SKU", sku_options, key="exp_sku")
    row = decision_table[(decision_table["cluster_id"] == cluster_id) & (decision_table["sku_id"] == sku_id)].iloc[0]

    st.markdown("### 结论")
    st.write(f"`{row['decision']}` | 推荐 `{int(row['recommended_facings'])}` 面")
    st.info(row["one_line_summary"])
    st.write(row["operation_instruction"])

    st.markdown("### 原因码")
    reason_details = loads_json_cell(row["reason_details"])
    for detail in reason_details:
        spec = reason_catalog[reason_catalog["reason_code"] == detail["reason_code"]].iloc[0]
        st.write(f"**{detail['reason_code']}**: {spec['definition']}")
        st.caption(f"触发规则: {spec['trigger_rule']}")
        evidence_df = pd.DataFrame(
            [{"字段": key, "数值": value} for key, value in detail["evidence"].items()]
        )
        st.dataframe(evidence_df, use_container_width=True)

    st.markdown("### 对比卡片")
    compare = pd.DataFrame(
        [
            {
                "metric": "direct_gp",
                "baseline": row["baseline_direct_gp"],
                "recommended": row["recommended_direct_gp"],
            },
            {
                "metric": "halo_gp",
                "baseline": row["baseline_halo_gp"],
                "recommended": row["recommended_halo_gp"],
            },
            {
                "metric": "total_gp",
                "baseline": row["baseline_total_gp"],
                "recommended": row["recommended_total_gp"],
            },
            {
                "metric": "shelf_cm",
                "baseline": row["baseline_shelf_cm"],
                "recommended": row["recommended_shelf_cm"],
            },
            {
                "metric": "coverage",
                "baseline": row["baseline_coverage"],
                "recommended": row["recommended_coverage"],
            },
            {
                "metric": "KVI price index",
                "baseline": row["baseline_kvi_price_index"],
                "recommended": row["recommended_kvi_price_index"],
            },
            {
                "metric": "OSA risk",
                "baseline": row["baseline_osa_risk"],
                "recommended": row["recommended_osa_risk"],
            },
        ]
    )
    st.dataframe(compare, use_container_width=True)

    st.markdown("### 贡献分解")
    contrib = pd.DataFrame(
        [
            {
                "delta_total_gp": row["delta_total_gp"],
                "delta_direct_gp": row["delta_direct_gp"],
                "delta_halo_gp": row["delta_halo_gp"],
                "delta_dup_penalty": row["delta_dup_penalty"],
                "delta_kvi_penalty": row["delta_kvi_penalty"],
                "delta_ops_penalty": row["delta_ops_penalty"],
            }
        ]
    )
    st.dataframe(contrib, use_container_width=True)

    st.markdown("### 反事实")
    counterfactual = loads_json_cell(row["counterfactual"])
    st.write(
        f"如果保留它：keep_cost = {counterfactual['keep_cost']:.2f}，"
        f"constraint_violation_flag = {counterfactual['constraint_violation_flag']}"
    )
    st.dataframe(pd.DataFrame([counterfactual]), use_container_width=True)


def render_guardrails(payload: dict[str, object]) -> None:
    guardrails = payload["guardrails"]
    st.title("Guardrails")
    for title, table in guardrails.items():
        st.markdown(f"### {title}")
        st.dataframe(table, use_container_width=True)
    if payload["constraint_report"]:
        st.markdown("### 约束检查")
        for line in payload["constraint_report"]:
            st.warning(line)


def render_export(payload: dict[str, object]) -> None:
    st.title("Export")
    st.markdown("### 业务导出")
    st.download_button(
        "下载 decision_table.csv",
        data=to_csv_bytes(payload["decision_table"]),
        file_name="decision_table.csv",
        mime="text/csv",
    )
    st.download_button(
        "下载 store_task_sheet.csv",
        data=to_csv_bytes(payload["store_task_sheet"]),
        file_name="store_task_sheet.csv",
        mime="text/csv",
    )
    st.download_button(
        "下载 planogram_proxy.csv",
        data=to_csv_bytes(payload["planogram_proxy"]),
        file_name="planogram_proxy.csv",
        mime="text/csv",
    )
    st.download_button(
        "下载 explain_trace.json",
        data=json_to_bytes(payload["explain_trace"]),
        file_name="explain_trace.json",
        mime="application/json",
    )
    st.download_button(
        "下载 one_pager.md",
        data=text_to_bytes(payload["one_pager_md"]),
        file_name="one_pager.md",
        mime="text/markdown",
    )
    st.download_button(
        "下载 playbook.md",
        data=text_to_bytes(payload["playbook_md"]),
        file_name="playbook.md",
        mime="text/markdown",
    )
    st.markdown("### 原因码字典")
    st.dataframe(build_reason_catalog(), use_container_width=True)
    st.markdown("### explain_trace 预览")
    st.code(json.dumps(payload["explain_trace"]["trace"][:2], ensure_ascii=False, indent=2))


def main() -> None:
    with st.sidebar:
        st.header("参数")
        seed = st.number_input("seed", min_value=1, max_value=999, value=7)
        st.caption("Cluster 数固定为 4，对应四类业务集群。")
        shelf_capacity_cm = st.slider("shelf_capacity_cm", min_value=140.0, max_value=260.0, value=180.0, step=5.0)
        min_facings_core = st.slider("min_facings_core", min_value=1, max_value=3, value=2)
        max_facings_per_sku = st.slider("max_facings_per_sku", min_value=2, max_value=6, value=4)
        brand_cap = st.slider("brand_cap", min_value=0.25, max_value=0.60, value=0.42, step=0.01)
        page = st.radio(
            "页面",
            ["Overview", "Cluster Profile", "Recommendation", "Explain", "Guardrails", "Export"],
        )

    payload = load_payload(
        seed=seed,
        shelf_capacity_cm=shelf_capacity_cm,
        min_facings_core=min_facings_core,
        max_facings_per_sku=max_facings_per_sku,
        brand_cap=brand_cap,
    )
    params = {
        "seed": seed,
        "n_clusters": 4,
        "shelf_capacity_cm": shelf_capacity_cm,
        "min_facings_core": min_facings_core,
        "max_facings_per_sku": max_facings_per_sku,
        "brand_cap": brand_cap,
    }

    if page == "Overview":
        render_overview(payload, params)
    elif page == "Cluster Profile":
        render_cluster_profile(payload)
    elif page == "Recommendation":
        render_recommendation(payload)
    elif page == "Explain":
        render_explain(payload)
    elif page == "Guardrails":
        render_guardrails(payload)
    else:
        render_export(payload)


if __name__ == "__main__":
    main()
