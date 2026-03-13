from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from modules.fus_demo import (
    FUS_BRAIN_REGIONS,
    FUS_REFERENCE_LINKS,
    build_fus_brain_demo_html,
    build_fus_treatment_overview,
)

st.set_page_config(page_title="聚焦超声精神科脑区演示", layout="wide")


def render_fus_brain_demo() -> None:
    st.title("聚焦超声脑区动态演示")
    st.caption("点击脑图中的热点，查看该区域在聚焦超声研究中被探索的潜在精神科适应证。")
    st.warning(
        "以下内容仅用于科研 / 产品演示，不构成医疗建议，也不代表这些适应证已经获批。页面里同时包含低强度神经调控和 MRgFUS 消融，两者不是同一类治疗。"
    )
    components.html(build_fus_brain_demo_html(FUS_BRAIN_REGIONS), height=980, scrolling=False)

    patient_data_count = sum(
        region["evidence_level"] not in {"健康受试者随机试验", "临床方案 / protocol"} for region in FUS_BRAIN_REGIONS
    )
    pure_neuromod_count = sum(region["type"] == "neuromod" for region in FUS_BRAIN_REGIONS)
    hybrid_count = sum(region["type"] == "hybrid" for region in FUS_BRAIN_REGIONS)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("可点击靶点", len(FUS_BRAIN_REGIONS))
    m2.metric("有人体患者数据", patient_data_count)
    m3.metric("纯低强度靶点", pure_neuromod_count)
    m4.metric("双路线靶点", hybrid_count)

    st.markdown("### 治疗方向总览")
    st.caption("这张表适合演示时快速扫一遍；详细说明看上面的脑图交互。")
    overview_df = build_fus_treatment_overview(FUS_BRAIN_REGIONS)
    st.dataframe(
        overview_df,
        width="stretch",
        hide_index=True,
        column_config={
            "脑区": st.column_config.TextColumn(width="large"),
            "超声路线": st.column_config.TextColumn(width="medium"),
            "潜在精神科方向": st.column_config.TextColumn(width="medium"),
            "证据层级": st.column_config.TextColumn(width="medium"),
            "当前状态": st.column_config.TextColumn(width="medium"),
            "演示话术": st.column_config.TextColumn(width="large"),
            "代表进展": st.column_config.TextColumn(width="large"),
        },
    )

    with st.expander("参考研究与来源", expanded=False):
        for ref in FUS_REFERENCE_LINKS:
            st.markdown(f"- [{ref['label']}]({ref['url']})")

    tip1, tip2, tip3, tip4 = st.columns(4)
    tip1.info("低强度调控：通常指可逆 neuromodulation，目前大多仍是早期临床。")
    tip2.info("双路线靶点：像 ALIC 这种区域，既可以做可逆调控，也可能做 MRgFUS 消融。")
    tip3.info("更稳妥的演示措辞是“可能研究方向”或“潜在适应证”，不要写成确定疗效。")
    tip4.info("PCC、caudate、thalamus 这类区域证据更早，讲解时要主动注明“机制研究 / 结果待出”。")


def main() -> None:
    render_fus_brain_demo()


if __name__ == "__main__":
    main()
