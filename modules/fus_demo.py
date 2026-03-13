from __future__ import annotations

import json

import pandas as pd

FUS_BRAIN_REGIONS: list[dict[str, object]] = [
    {
        "id": "dlpfc",
        "short": "DLPFC",
        "title": "左背外侧前额叶（DLPFC）",
        "summary": "这是目前聚焦超声抑郁研究里最接近临床主靶点的区域之一，常被用作进入前额叶-边缘系统的皮层入口。",
        "conditions": ["重性抑郁障碍（MDD）", "难治性抑郁（TRD）", "伴发焦虑 / 睡眠问题的抑郁表型"],
        "evidence": "2024 年随机双盲 sham 对照试验和 2026 年单盲随机 sham 对照研究都刺激左 dlPFC，并观察到抑郁量表改善，以及与 sgACC、PCC 相关的连接变化。样本量仍不大，但这是当前患者级 sham 对照证据最明确的靶点之一。",
        "note": "演示时适合说“可能帮助缓解抑郁症状”，不要说成已确立标准治疗。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "随机对照患者研究",
        "status": "人体 sham 对照最充分",
        "popup": "可能研究方向：MDD、TRD，以及抑郁伴焦虑/睡眠问题。",
        "popup_side": "left",
        "type": "neuromod",
        "x": 186,
        "y": 138,
        "label_x": 82,
        "label_y": 106,
        "anchor": "start",
        "focus_rx": 42,
        "focus_ry": 24,
        "focus_rotate": -24,
        "overview_conditions": "MDD / TRD",
        "overview_line": "最适合讲“抑郁一线研究靶点”。",
        "study": "2024 + 2026 两项 dlPFC sham 对照抑郁研究",
        "evidence_sort": 1,
    },
    {
        "id": "scc",
        "short": "SCC / sgACC",
        "title": "下扣带 / 皮层下前扣带（SCC / sgACC）",
        "summary": "这是深部抑郁环路里最经典的节点之一，过去更常见于 DBS，如今聚焦超声开始直接、非侵入式地瞄准它。",
        "conditions": ["难治性抑郁（TRD）", "重度抑郁的悲伤 / 负性情绪表型", "深部情绪环路调控"],
        "evidence": "2025 年随机、双盲、sham 对照 SCC 研究显示，真实刺激能降低 SCC 活性，并在 24 小时和 7 天尺度上带来更好的情绪 / 抑郁评分变化。另一项 2025 年首个人体 metalens 深部超声开放研究也报告了 TRD 症状快速下降。",
        "note": "适合讲成“深部抑郁环路靶点，已经开始有人体随机试验”，但仍不是获批疗法。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "随机对照 + 开放标签",
        "status": "深部抑郁环路已有患者随机试验",
        "popup": "可能研究方向：难治性抑郁和重度负性情绪。",
        "popup_side": "center",
        "type": "neuromod",
        "x": 320,
        "y": 224,
        "label_x": 422,
        "label_y": 98,
        "anchor": "middle",
        "focus_rx": 28,
        "focus_ry": 18,
        "focus_rotate": -10,
        "overview_conditions": "TRD / severe depression",
        "overview_line": "适合强调“深部抑郁回路直接调控”。",
        "study": "2025 SCC 双盲 sham 试验 + metalens 开放研究",
        "evidence_sort": 2,
    },
    {
        "id": "ampfc",
        "short": "amPFC / DMN",
        "title": "前内侧前额叶 / 默认网络枢纽（amPFC / DMN）",
        "summary": "这一方向的核心思路是调节默认网络，减少抑郁中的反刍和持续负性思维。",
        "conditions": ["抑郁症状", "反复负性思维 / 反刍", "生活质量受损的抑郁表型"],
        "evidence": "2025 年开放标签研究把前内侧前额叶作为默认网络靶点，连续 11 次 tFUS 后观察到抑郁量表、反刍和生活质量指标改善；但没有对照组，目前更偏可行性与机制展示。",
        "note": "更稳妥的演示话术是“默认网络调控方向”，不宜包装成成熟抗抑郁疗法。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "开放标签早期临床",
        "status": "机制导向，偏反刍网络",
        "popup": "可能研究方向：抑郁、反刍和持续负性思维。",
        "popup_side": "center",
        "type": "neuromod",
        "x": 270,
        "y": 148,
        "label_x": 278,
        "label_y": 64,
        "anchor": "middle",
        "focus_rx": 34,
        "focus_ry": 20,
        "focus_rotate": 15,
        "overview_conditions": "MDD / rumination",
        "overview_line": "适合讲“默认网络和反刍”而不是“治愈抑郁”。",
        "study": "2025 amPFC / DMN 开放标签抑郁研究",
        "evidence_sort": 4,
    },
    {
        "id": "pcc",
        "short": "PCC",
        "title": "后扣带皮层（Posterior Cingulate Cortex, PCC）",
        "summary": "PCC 是默认网络后部核心节点，更适合被展示为“自我相关加工 / 反刍回路”的机制靶点。",
        "conditions": ["抑郁中的反刍", "过度自我聚焦", "默认网络异常相关症状"],
        "evidence": "2024 年一项随机、单盲、健康受试者 fMRI pilot 研究显示，PCC 超声刺激可降低默认网络中线连接，并改变主观体验。它证明了 target engagement，但还不能等同于患者疗效证据。",
        "note": "如果一定要映射疾病，建议写成“抑郁中的反刍 / 自我加工异常候选靶点”，不要写成已经治疗某个诊断。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "健康受试者随机试验",
        "status": "机制 / target-engagement 证据",
        "popup": "可能研究方向：反刍、自我加工异常、默认网络紊乱。",
        "popup_side": "right",
        "type": "neuromod",
        "x": 396,
        "y": 198,
        "label_x": 584,
        "label_y": 154,
        "anchor": "start",
        "focus_rx": 28,
        "focus_ry": 18,
        "focus_rotate": 14,
        "overview_conditions": "rumination / self-processing",
        "overview_line": "更适合讲机制，不适合讲确定疗效。",
        "study": "2024 PCC 单盲随机 fMRI pilot",
        "evidence_sort": 7,
    },
    {
        "id": "thalamus",
        "short": "ANT / dmThal",
        "title": "前丘脑 / 背内侧丘脑（ANT / dmThal）",
        "summary": "丘脑是连接边缘系统、默认网络和觉醒调节的重要中继核团，因此被探索为超深部抑郁环路靶点。",
        "conditions": ["难治性抑郁（TRD）", "抑郁情绪强度", "默认网络异常"],
        "evidence": "2024 年 Brain Stimulation letter 报告了丘脑超声用于难治性抑郁；图注明确写到 ANT 刺激与抑郁视觉评分下降及默认网络连接抑制相关。这仍属于超早期人体信号。",
        "note": "更适合写成“极早期深部候选靶点”，避免过度渲染疗效。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "超早期人体报道",
        "status": "letter / 小样本信号",
        "popup": "可能研究方向：难治性抑郁和默认网络异常。",
        "popup_side": "right",
        "type": "neuromod",
        "x": 394,
        "y": 250,
        "label_x": 610,
        "label_y": 238,
        "anchor": "start",
        "focus_rx": 34,
        "focus_ry": 22,
        "focus_rotate": -4,
        "overview_conditions": "TRD / DMN dysregulation",
        "overview_line": "适合讲“超深部靶点，但证据还很早”。",
        "study": "2024 丘脑 TUS 用于 TRD 的早期人体报道",
        "evidence_sort": 6,
    },
    {
        "id": "caudate",
        "short": "Caudate",
        "title": "尾状核头部（Caudate Head）",
        "summary": "尾状核头部位于奖赏学习和动机回路中，因此在“快感缺失型抑郁”里尤其有吸引力。",
        "conditions": ["快感缺失型抑郁", "动机低下", "奖赏加工受损"],
        "evidence": "2025 年 protocol 论文发布了针对快感缺失型抑郁的随机 sham 对照设计，计划刺激左尾状核头部或右伏隔核。目前这是正式进入临床验证路径的候选靶点，但结果仍待发表。",
        "note": "页面里应明确写“随机研究进行中 / 结果待出”，不要暗示已经证实有效。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "临床方案 / protocol",
        "status": "随机试验设计已发布",
        "popup": "可能研究方向：快感缺失型抑郁和动机低下。",
        "popup_side": "left",
        "type": "neuromod",
        "x": 308,
        "y": 258,
        "label_x": 92,
        "label_y": 334,
        "anchor": "start",
        "focus_rx": 28,
        "focus_ry": 18,
        "focus_rotate": -24,
        "overview_conditions": "anhedonic depression",
        "overview_line": "这类靶点更适合讲“奖赏回路”而不是泛抑郁。",
        "study": "2025 快感缺失抑郁 caudate / NAc RCT protocol",
        "evidence_sort": 8,
    },
    {
        "id": "nac",
        "short": "NAc",
        "title": "伏隔核（Nucleus Accumbens, NAc）",
        "summary": "伏隔核是奖赏、渴求和强化学习回路中心，目前成瘾方向的人体 FUS 数据主要集中在这里。",
        "conditions": ["阿片使用障碍（OUD）", "甲基苯丙胺使用障碍（MUD）", "物质使用障碍中的渴求 / 复吸风险"],
        "evidence": "2025 年 severe OUD 单臂开放研究在 8 名受试者中报告了即时且持续到 90 天的渴求下降；2025 年 MUD 个案报告也描述了 90 天持续抑制渴求和阴性尿检。总体仍需 sham 对照扩大验证。",
        "note": "更稳妥的演示表述是“可能帮助降低渴求和复吸风险”，不要直接说治愈成瘾。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "开放标签 + 病例报告",
        "status": "成瘾方向已有患者临床信号",
        "popup": "可能研究方向：阿片 / 兴奋剂成瘾中的渴求控制。",
        "popup_side": "left",
        "type": "neuromod",
        "x": 292,
        "y": 300,
        "label_x": 106,
        "label_y": 396,
        "anchor": "start",
        "focus_rx": 24,
        "focus_ry": 16,
        "focus_rotate": -8,
        "overview_conditions": "OUD / MUD / craving",
        "overview_line": "成瘾演示时最好用“渴求控制”而不是“戒断”。",
        "study": "2025 OUD 开放研究 + 2025 MUD 个案",
        "evidence_sort": 5,
    },
    {
        "id": "alic",
        "short": "ALIC",
        "title": "前内囊（Anterior Limb of Internal Capsule, ALIC）",
        "summary": "这是精神外科里最经典的深部白质通路靶点之一，聚焦超声现在已经同时沿着“可逆调控”和“MRgFUS 消融”两条路线推进。",
        "conditions": ["难治性强迫症（OCD）", "难治性抑郁（MDD / TRD）", "强迫 / 反刍性回路失衡"],
        "evidence": "2025 年 MRgFUS capsulotomy 长期随访显示，OCD 改善更稳定，MDD 结果相对弱一些；2026 年又有随机、双盲、sham 对照低强度 LIFU 研究，证明 ALIC 白质束可以被可逆调控，并带来正性情绪变化。",
        "note": "这里必须明确区分两类路线：capsulotomy 是不可逆病灶制作，LIFU white-matter modulation 是可逆调控。",
        "mode": "低强度调控 + MRgFUS 消融",
        "modality_badge": "双路线靶点",
        "evidence_level": "随机对照 + 长期随访",
        "status": "同一靶点已有两种 FUS 路线",
        "popup": "可能研究方向：OCD、TRD，以及强迫 / 反刍回路。",
        "popup_side": "center",
        "type": "hybrid",
        "x": 336,
        "y": 284,
        "label_x": 336,
        "label_y": 470,
        "anchor": "middle",
        "focus_rx": 30,
        "focus_ry": 16,
        "focus_rotate": 24,
        "overview_conditions": "OCD / TRD",
        "overview_line": "这是最适合讲“同靶点不同路线”的一行。",
        "study": "2025 capsulotomy 随访 + 2026 ALIC LIFU RCT",
        "evidence_sort": 3,
    },
    {
        "id": "amygdala",
        "short": "Amygdala",
        "title": "杏仁核（Amygdala）",
        "summary": "杏仁核与威胁反应、恐惧学习、情绪唤醒高度相关，因此是焦虑与创伤相关障碍最自然的深部候选靶点之一。",
        "conditions": ["广泛性焦虑障碍（GAD）", "情绪 / 焦虑 / 创伤相关障碍", "恐惧反应过强和高唤醒症状"],
        "evidence": "2023 年 pilot study 在治疗抵抗性 GAD 中报告显著焦虑量表下降；2024 年随机 sham 对照研究显示健康受试者左杏仁核刺激后，杏仁核激活和恐惧网络连接改变并与主观焦虑下降相关；2025 年 MATRD 双盲 target-engagement + 单臂临床研究进一步报告了症状下降和情绪面孔反应降低。",
        "note": "更保守的说法是“可能改善焦虑、恐惧反应和创伤相关症状”，不要直接说能治疗 PTSD。",
        "mode": "低强度可逆神经调控",
        "modality_badge": "低强度调控",
        "evidence_level": "pilot + 随机机制试验 + 单臂临床",
        "status": "焦虑 / 创伤方向证据增长最快",
        "popup": "可能研究方向：GAD、创伤相关症状和高恐惧反应。",
        "popup_side": "right",
        "type": "neuromod",
        "x": 448,
        "y": 312,
        "label_x": 614,
        "label_y": 360,
        "anchor": "start",
        "focus_rx": 30,
        "focus_ry": 20,
        "focus_rotate": 28,
        "overview_conditions": "GAD / trauma-related symptoms",
        "overview_line": "这一行最适合讲“恐惧回路和高唤醒”。",
        "study": "2023 GAD pilot + 2024 fear RCT + 2025 MATRD study",
        "evidence_sort": 4,
    },
]

FUS_REFERENCE_LINKS: list[dict[str, str]] = [
    {"label": "DLPFC 抑郁随机双盲 sham 对照，2024", "url": "https://pubmed.ncbi.nlm.nih.gov/39111747/"},
    {"label": "DLPFC 抑郁单盲随机 sham 对照，2026", "url": "https://pubmed.ncbi.nlm.nih.gov/41232683/"},
    {"label": "SCC/sgACC 抑郁随机双盲 sham 对照，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/39396736/"},
    {"label": "subcallosal cingulate metalens 首个人体开放研究，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40311843/"},
    {"label": "amPFC / DMN 抑郁开放标签研究，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40256163/"},
    {"label": "PCC 默认网络 fMRI pilot，2024", "url": "https://pubmed.ncbi.nlm.nih.gov/38895168/"},
    {"label": "ALIC MRgFUS capsulotomy 长期随访，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/39187171/"},
    {"label": "ALIC 可逆白质调控随机 sham 对照，2026", "url": "https://pubmed.ncbi.nlm.nih.gov/40999237/"},
    {"label": "伏隔核 severe OUD 开放研究，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/39798597/"},
    {"label": "伏隔核 MUD 个案报告，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40892597/"},
    {"label": "快感缺失抑郁 caudate / NAc 随机试验 protocol，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40196448/"},
    {"label": "杏仁核治疗抵抗性 GAD pilot，2023", "url": "https://pubmed.ncbi.nlm.nih.gov/39491902/"},
    {"label": "杏仁核 fear network 随机 sham 对照，2024", "url": "https://pubmed.ncbi.nlm.nih.gov/38447773/"},
    {"label": "杏仁核 MATRD 双盲 target-engagement + 单臂临床，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40275098/"},
    {"label": "丘脑 TUS 用于难治性抑郁早期人体报道，2024", "url": "https://pubmed.ncbi.nlm.nih.gov/39173737/"},
    {"label": "精神科聚焦超声路线图综述，2025", "url": "https://pubmed.ncbi.nlm.nih.gov/40854478/"},
]

REGION_VISUALS: dict[str, dict[str, str]] = {
    "dlpfc": {"accent": "#0f7b76", "soft": "rgba(15, 123, 118, 0.20)", "glow": "rgba(15, 123, 118, 0.34)"},
    "scc": {"accent": "#b54441", "soft": "rgba(181, 68, 65, 0.22)", "glow": "rgba(181, 68, 65, 0.34)"},
    "ampfc": {"accent": "#3d5bb8", "soft": "rgba(61, 91, 184, 0.20)", "glow": "rgba(61, 91, 184, 0.34)"},
    "pcc": {"accent": "#5d74c4", "soft": "rgba(93, 116, 196, 0.20)", "glow": "rgba(93, 116, 196, 0.34)"},
    "thalamus": {"accent": "#6b56a8", "soft": "rgba(107, 86, 168, 0.20)", "glow": "rgba(107, 86, 168, 0.34)"},
    "caudate": {"accent": "#c66c2f", "soft": "rgba(198, 108, 47, 0.20)", "glow": "rgba(198, 108, 47, 0.34)"},
    "nac": {"accent": "#dd8a2d", "soft": "rgba(221, 138, 45, 0.20)", "glow": "rgba(221, 138, 45, 0.34)"},
    "alic": {"accent": "#926a33", "soft": "rgba(146, 106, 51, 0.20)", "glow": "rgba(146, 106, 51, 0.34)"},
    "amygdala": {"accent": "#b24572", "soft": "rgba(178, 69, 114, 0.20)", "glow": "rgba(178, 69, 114, 0.34)"},
}


def build_fus_treatment_overview(regions: list[dict[str, object]]) -> pd.DataFrame:
    rows = [
        {
            "脑区": region["title"],
            "缩写": region["short"],
            "超声路线": region["mode"],
            "潜在精神科方向": region["overview_conditions"],
            "证据层级": region["evidence_level"],
            "当前状态": region["status"],
            "演示话术": region["overview_line"],
            "代表进展": region["study"],
            "_sort": int(region["evidence_sort"]),
        }
        for region in regions
    ]
    return pd.DataFrame(rows).sort_values(["_sort", "脑区"]).drop(columns=["_sort"]).reset_index(drop=True)


def build_fus_brain_demo_html(regions: list[dict[str, object]]) -> str:
    focus_markup: list[str] = []
    trigger_markup: list[str] = []
    visual_regions: list[dict[str, object]] = []
    for region in regions:
        visual = REGION_VISUALS[str(region["id"])]
        enriched_region = {**region, "accent": visual["accent"], "accent_soft": visual["soft"], "accent_glow": visual["glow"]}
        visual_regions.append(enriched_region)
        region_type = str(region["type"])
        qx = int((int(region["x"]) + int(region["label_x"])) / 2)
        qy = int((int(region["y"]) + int(region["label_y"])) / 2)
        focus_rx = int(region["focus_rx"])
        focus_ry = int(region["focus_ry"])
        inner_rx = max(10, int(focus_rx * 0.58))
        inner_ry = max(8, int(focus_ry * 0.58))
        label_text = str(region["short"])
        label_width = max(88, len(label_text) * 10 + 24)
        anchor = str(region["anchor"])
        label_x = int(region["label_x"])
        label_y = int(region["label_y"])
        if anchor == "middle":
            pill_x = int(label_x - (label_width / 2))
        elif anchor == "end":
            pill_x = label_x - label_width + 10
        else:
            pill_x = label_x - 10
        pill_y = label_y - 18
        pill_text_x = pill_x + int(label_width / 2)
        focus_markup.append(
            f"""
            <g
              class="region-layer {region_type} region-trigger"
              data-id="{region['id']}"
              style="--accent: {visual['accent']}; --accent-soft: {visual['soft']}; --accent-glow: {visual['glow']};"
            >
              <ellipse
                class="region-focus"
                cx="{region['x']}"
                cy="{region['y']}"
                rx="{focus_rx}"
                ry="{focus_ry}"
                transform="rotate({region['focus_rotate']} {region['x']} {region['y']})"
              ></ellipse>
              <ellipse
                class="region-core-fill"
                cx="{region['x']}"
                cy="{region['y']}"
                rx="{inner_rx}"
                ry="{inner_ry}"
                transform="rotate({region['focus_rotate']} {region['x']} {region['y']})"
              ></ellipse>
            </g>
            """
        )
        trigger_markup.append(
            f"""
            <g
              class="callout-group {region_type} region-trigger"
              data-id="{region['id']}"
              style="--accent: {visual['accent']}; --accent-soft: {visual['soft']}; --accent-glow: {visual['glow']};"
            >
              <path class="callout-line" d="M {region['x']} {region['y']} Q {qx} {qy} {region['label_x']} {region['label_y']}" />
              <rect class="callout-pill" x="{pill_x}" y="{pill_y}" width="{label_width}" height="30" rx="15"></rect>
              <text class="callout-label" x="{pill_text_x}" y="{label_y}" text-anchor="middle" dominant-baseline="middle">{region['short']}</text>
            </g>
            <g
              class="hotspot {region_type} region-trigger"
              data-id="{region['id']}"
              style="--accent: {visual['accent']}; --accent-soft: {visual['soft']}; --accent-glow: {visual['glow']};"
            >
              <circle class="pulse" cx="{region['x']}" cy="{region['y']}" r="26"></circle>
              <circle class="ring" cx="{region['x']}" cy="{region['y']}" r="14"></circle>
              <circle class="core" cx="{region['x']}" cy="{region['y']}" r="7"></circle>
            </g>
            """
        )

    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          :root {
            --bg: #07111d;
            --panel: rgba(9, 19, 31, 0.82);
            --ink: #edf4fb;
            --muted: #9fb2c3;
            --line: rgba(194, 221, 238, 0.12);
            --teal: #0f7b76;
            --teal-soft: rgba(15, 123, 118, 0.16);
            --danger: #b54441;
            --hybrid: #926a33;
            --hybrid-soft: rgba(146, 106, 51, 0.18);
            --shadow: 0 42px 120px rgba(0, 0, 0, 0.42);
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", sans-serif;
            background:
              radial-gradient(circle at 18% 16%, rgba(75, 207, 255, 0.20), transparent 26%),
              radial-gradient(circle at 84% 12%, rgba(255, 117, 95, 0.18), transparent 24%),
              radial-gradient(circle at 50% 78%, rgba(84, 96, 255, 0.14), transparent 36%),
              linear-gradient(180deg, #081321 0%, #09111d 46%, #050b14 100%);
            color: var(--ink);
          }

          .fus-app {
            min-height: 100vh;
            padding: 24px;
          }

          .hero {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(260px, 0.9fr);
            gap: 18px;
            align-items: start;
            margin-bottom: 18px;
          }

          .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(11, 23, 37, 0.68);
            border: 1px solid rgba(134, 190, 220, 0.20);
            color: #d8ecfb;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }

          .hero h2 {
            margin: 12px 0 10px;
            font-size: 34px;
            line-height: 1.06;
            color: #ffffff;
          }

          .hero p {
            margin: 0;
            max-width: 700px;
            color: var(--muted);
            line-height: 1.68;
          }

          .legend {
            display: grid;
            gap: 10px;
          }

          .legend-card {
            padding: 14px 16px;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(14, 27, 43, 0.88), rgba(8, 18, 30, 0.78));
            border: 1px solid rgba(175, 215, 238, 0.12);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
          }

          .legend-card strong {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
          }

          .legend-card span {
            display: block;
            font-size: 12px;
            line-height: 1.55;
            color: var(--muted);
          }

          .legend-card.teal strong {
            color: var(--teal);
          }

          .legend-card.danger strong {
            color: var(--danger);
          }

          .legend-card.hybrid strong {
            color: var(--hybrid);
          }

          .stage {
            display: grid;
            grid-template-columns: minmax(0, 1.22fr) minmax(330px, 0.78fr);
            gap: 18px;
            align-items: stretch;
          }

          .brain-card,
          .info-panel {
            position: relative;
            overflow: hidden;
            background: var(--panel);
            border: 1px solid rgba(187, 223, 244, 0.12);
            border-radius: 30px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
          }

          .brain-card {
            min-height: 710px;
            padding: 14px 14px 18px;
            background:
              radial-gradient(circle at 25% 18%, rgba(99, 226, 255, 0.18), transparent 22%),
              radial-gradient(circle at 76% 16%, rgba(255, 156, 118, 0.14), transparent 24%),
              radial-gradient(circle at 52% 78%, rgba(74, 96, 255, 0.14), transparent 28%),
              linear-gradient(180deg, rgba(11, 22, 35, 0.96) 0%, rgba(8, 16, 26, 0.98) 100%);
          }

          .brain-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
              linear-gradient(135deg, rgba(255, 255, 255, 0.10), transparent 24%),
              linear-gradient(220deg, rgba(74, 210, 255, 0.08), transparent 34%);
            pointer-events: none;
          }

          .brain-card::after {
            content: "";
            position: absolute;
            inset: 18px;
            border-radius: 26px;
            border: 1px solid rgba(170, 215, 241, 0.08);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
            pointer-events: none;
          }

          .brain-wrap {
            position: relative;
            width: 100%;
            height: 100%;
          }

          .brain-caption {
            position: absolute;
            right: 18px;
            top: 16px;
            z-index: 5;
            padding: 9px 14px;
            border-radius: 999px;
            background: rgba(11, 23, 37, 0.72);
            border: 1px solid rgba(146, 207, 238, 0.18);
            font-size: 12px;
            color: #d8ecfb;
            font-weight: 800;
            letter-spacing: 0.04em;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
          }

          .brain-guide {
            position: absolute;
            left: 16px;
            top: 16px;
            z-index: 5;
            display: grid;
            gap: 6px;
            padding: 12px 14px;
            border-radius: 18px;
            background: rgba(11, 23, 37, 0.72);
            border: 1px solid rgba(146, 207, 238, 0.16);
            box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
            font-size: 12px;
            color: #d3e5f4;
          }

          .brain-guide span {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            line-height: 1.4;
          }

          .guide-chip,
          .guide-outline {
            width: 14px;
            height: 14px;
            border-radius: 999px;
            flex: 0 0 auto;
          }

          .guide-chip {
            background: rgba(15, 123, 118, 0.20);
            border: 2px solid rgba(15, 123, 118, 0.72);
          }

          .guide-outline {
            background: rgba(12, 22, 34, 0.94);
            border: 2px solid rgba(214, 188, 168, 0.58);
          }

          svg {
            width: 100%;
            height: 100%;
            shape-rendering: geometricPrecision;
            text-rendering: geometricPrecision;
          }

          .cortex-shell {
            fill: url(#cortexGradient);
            stroke: rgba(255, 221, 205, 0.46);
            stroke-width: 4.4;
          }

          .cortex-rim {
            fill: none;
            stroke: rgba(255, 249, 243, 0.66);
            stroke-width: 2.4;
            stroke-linecap: round;
          }

          .cortex-shadow {
            fill: rgba(172, 114, 95, 0.14);
          }

          .brain-object {
            filter: url(#brainDepth);
          }

          .brain-back-glow {
            fill: url(#brainGlowGradient);
            opacity: 0.88;
          }

          .stage-shadow {
            fill: rgba(3, 10, 18, 0.78);
          }

          .stage-rim {
            fill: url(#stageGlowGradient);
            opacity: 0.92;
          }

          .shell-highlight {
            fill: url(#shellHighlightGradient);
            opacity: 0.78;
            mix-blend-mode: screen;
          }

          .shell-highlight.soft {
            opacity: 0.42;
          }

          .cortex-inner-shade {
            fill: rgba(109, 70, 74, 0.10);
          }

          .white-matter-shadow {
            fill: rgba(169, 118, 98, 0.10);
          }

          .white-matter {
            fill: url(#whiteMatterGradient);
            stroke: rgba(124, 81, 72, 0.22);
            stroke-width: 3;
          }

          .corpus-callosum {
            fill: rgba(250, 241, 228, 0.95);
            stroke: rgba(124, 81, 72, 0.24);
            stroke-width: 2.6;
            filter: url(#subsurfaceSoftGlow);
          }

          .lobe-zone {
            stroke-width: 2;
            stroke-linejoin: round;
          }

          .frontal-zone {
            fill: rgba(15, 123, 118, 0.08);
            stroke: rgba(15, 123, 118, 0.18);
          }

          .cingulate-zone {
            fill: rgba(181, 68, 65, 0.08);
            stroke: rgba(181, 68, 65, 0.18);
          }

          .deep-zone {
            fill: rgba(107, 86, 168, 0.07);
            stroke: rgba(107, 86, 168, 0.16);
          }

          .temporal-zone {
            fill: rgba(178, 69, 114, 0.08);
            stroke: rgba(178, 69, 114, 0.16);
          }

          .deep-structure {
            fill: rgba(116, 79, 88, 0.30);
            stroke: rgba(250, 218, 206, 0.18);
            stroke-width: 1.8;
          }

          .ventricle {
            fill: rgba(233, 246, 255, 0.92);
            stroke: rgba(255, 235, 222, 0.14);
            stroke-width: 1.8;
          }

          .hippocampus {
            fill: rgba(209, 121, 148, 0.22);
            stroke: rgba(255, 212, 224, 0.18);
            stroke-width: 1.8;
          }

          .fiber-bundle {
            fill: none;
            stroke: rgba(227, 205, 157, 0.32);
            stroke-width: 2.2;
            stroke-linecap: round;
          }

          .midline-cut {
            fill: none;
            stroke: rgba(255, 228, 214, 0.18);
            stroke-width: 2.4;
            stroke-dasharray: 5 6;
          }

          .sulcus {
            fill: none;
            stroke: rgba(125, 73, 84, 0.36);
            stroke-width: 2.2;
            stroke-linecap: round;
            opacity: 0.95;
          }

          .sulcus.deep {
            stroke: rgba(115, 66, 75, 0.44);
            stroke-width: 3;
          }

          .sulcus.fine {
            stroke: rgba(132, 80, 87, 0.22);
            stroke-width: 1.4;
          }

          .cerebellum {
            fill: url(#cerebellumGradient);
            stroke: rgba(249, 221, 206, 0.18);
            stroke-width: 2.6;
          }

          .cerebellar-fold {
            fill: none;
            stroke: rgba(130, 80, 88, 0.28);
            stroke-width: 1.8;
            stroke-linecap: round;
          }

          .brainstem {
            fill: url(#stemGradient);
            stroke: rgba(255, 228, 214, 0.18);
            stroke-width: 2.4;
          }

          .anatomy-line {
            fill: none;
            stroke: rgba(141, 180, 202, 0.28);
            stroke-width: 2.6;
            stroke-linecap: round;
          }

          .anatomy-line.soft {
            stroke-width: 2;
            stroke: rgba(141, 180, 202, 0.16);
          }

          .anatomy-label {
            fill: #e4f0fa;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.02em;
            paint-order: stroke;
            stroke: rgba(6, 12, 20, 0.84);
            stroke-width: 5;
            stroke-linejoin: round;
          }

          .region-layer {
            cursor: pointer;
          }

          .region-focus {
            fill: var(--accent-soft);
            stroke: var(--accent);
            stroke-width: 2.2;
            opacity: 0.92;
            transition: fill 220ms ease, stroke 220ms ease, opacity 220ms ease, transform 220ms ease;
          }

          .region-core-fill {
            fill: var(--accent);
            opacity: 0.18;
            transition: opacity 220ms ease, transform 220ms ease;
          }

          .region-layer.active .region-focus {
            fill: var(--accent-soft);
            stroke: var(--accent);
            stroke-width: 3;
            filter: drop-shadow(0 0 18px var(--accent-glow));
          }

          .region-layer.active .region-core-fill {
            opacity: 0.34;
          }

          .callout-line {
            fill: none;
            stroke: var(--accent);
            stroke-width: 2.6;
            stroke-dasharray: 5 4;
            opacity: 0.66;
            stroke-linecap: round;
          }

          .callout-pill {
            fill: rgba(6, 15, 24, 0.78);
            stroke: var(--accent);
            stroke-width: 2;
            filter: drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28));
          }

          .callout-label {
            fill: #f3fbff;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.04em;
            cursor: pointer;
          }

          .callout-group.active .callout-line {
            opacity: 1;
            stroke-width: 3;
          }

          .callout-group.active .callout-pill {
            fill: var(--accent);
            filter: drop-shadow(0 8px 20px var(--accent-glow));
          }

          .callout-group.active .callout-label {
            fill: #ffffff;
          }

          .hotspot {
            cursor: pointer;
          }

          .pulse {
            fill: var(--accent-soft);
            animation: pulse 2.4s ease-in-out infinite;
            transform-origin: center;
          }

          .ring {
            fill: rgba(255, 255, 255, 0.94);
            stroke: var(--accent);
            stroke-width: 3.2;
          }

          .core {
            fill: var(--accent);
          }

          .hotspot.active .ring {
            stroke-width: 5.2;
            filter: drop-shadow(0 0 18px var(--accent-glow));
          }

          .hotspot.active .core {
            transform: scale(1.28);
            transform-origin: center;
          }

          .popup-shell {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 6;
          }

          .spotlight {
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(15, 123, 118, 0.28) 0%, rgba(15, 123, 118, 0.08) 38%, transparent 72%);
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.22);
          }

          .spotlight.hybrid {
            background: radial-gradient(circle, rgba(146, 106, 51, 0.30) 0%, rgba(146, 106, 51, 0.10) 38%, transparent 72%);
          }

          .spotlight.visible {
            animation: spotlightIn 420ms cubic-bezier(0.17, 0.84, 0.44, 1) forwards;
          }

          .popup-card {
            position: absolute;
            min-width: 214px;
            max-width: 270px;
            padding: 14px 16px;
            border-radius: 20px;
            background: linear-gradient(180deg, rgba(9, 18, 30, 0.94), rgba(4, 10, 17, 0.96));
            color: #fff;
            font-size: 13px;
            line-height: 1.5;
            box-shadow: 0 24px 56px rgba(0, 0, 0, 0.38);
            backdrop-filter: blur(12px);
            opacity: 0;
          }

          .popup-card strong {
            display: block;
            margin-bottom: 4px;
            font-size: 14px;
          }

          .popup-card::after {
            content: "";
            position: absolute;
            bottom: -7px;
            left: 18px;
            width: 14px;
            height: 14px;
            background: inherit;
            transform: rotate(45deg);
            border-radius: 2px;
          }

          .popup-card[data-side="left"]::after {
            left: auto;
            right: 22px;
          }

          .popup-card[data-side="center"]::after {
            left: calc(50% - 7px);
          }

          .popup-card.visible {
            animation: popupIn 340ms cubic-bezier(0.2, 0.85, 0.25, 1) forwards;
          }

          .popup-card[data-side="left"] {
            transform: translate(-92%, -122%) scale(0.82);
          }

          .popup-card[data-side="center"] {
            transform: translate(-48%, -134%) scale(0.82);
          }

          .popup-card[data-side="right"] {
            transform: translate(4%, -122%) scale(0.82);
          }

          .info-panel {
            padding: 24px;
            background:
              radial-gradient(circle at 84% 10%, rgba(84, 215, 255, 0.12), transparent 26%),
              linear-gradient(180deg, rgba(10, 21, 34, 0.90), rgba(8, 16, 26, 0.94));
          }

          .info-label {
            display: inline-flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(15, 123, 118, 0.16);
            color: var(--teal);
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 14px;
          }

          .info-label.hybrid {
            background: var(--hybrid-soft);
            color: var(--hybrid);
          }

          .info-panel h3 {
            margin: 0 0 10px;
            font-size: 29px;
            line-height: 1.14;
          }

          .summary {
            margin: 0 0 16px;
            color: #5d7077;
            line-height: 1.7;
          }

          .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 18px;
          }

          .chip {
            display: inline-flex;
            align-items: center;
            padding: 7px 11px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(197, 223, 239, 0.10);
            color: var(--ink);
            font-size: 12px;
            font-weight: 800;
          }

          .block {
            padding: 16px 0;
            border-top: 1px solid rgba(33, 52, 59, 0.14);
          }

          .block-title {
            margin-bottom: 10px;
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            font-weight: 800;
          }

          .list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }

          .bullet {
            display: inline-flex;
            align-items: center;
            padding: 8px 10px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(194, 221, 238, 0.10);
            font-size: 13px;
          }

          .body-copy {
            color: var(--ink);
            line-height: 1.74;
            font-size: 14px;
          }

          .footnote {
            margin-top: 16px;
            padding: 14px 18px;
            border-radius: 18px;
            background: rgba(9, 19, 31, 0.74);
            color: var(--muted);
            font-size: 13px;
            line-height: 1.64;
            border: 1px solid rgba(194, 221, 238, 0.10);
          }

          @keyframes pulse {
            0%, 100% { transform: scale(0.92); opacity: 0.46; }
            50% { transform: scale(1.18); opacity: 0.10; }
          }

          @keyframes spotlightIn {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.18); }
            55% { opacity: 1; transform: translate(-50%, -50%) scale(1.06); }
            100% { opacity: 0.92; transform: translate(-50%, -50%) scale(1); }
          }

          @keyframes popupIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
          }

          @media (max-width: 920px) {
            .fus-app {
              padding: 14px;
            }

            .hero,
            .stage {
              grid-template-columns: 1fr;
            }

            .brain-card {
              min-height: 560px;
              padding: 10px;
            }

            .brain-caption {
              right: 12px;
              top: 12px;
            }

            .brain-guide {
              left: 12px;
              top: 12px;
              max-width: calc(100% - 24px);
            }

            .hero h2 {
              font-size: 26px;
            }
          }
        </style>
      </head>
      <body>
        <div class="fus-app">
          <div class="hero">
            <div>
              <div class="eyebrow">Focused Ultrasound Demo</div>
              <h2>点击脑区，查看聚焦超声可能对应的精神科研究方向</h2>
              <p>这张图现在改成了更像发布会舞台上的 3D 脑切面示意图，默认就能看见主要靶点轮廓、深部结构和中文解剖提示。页面里的“可能治疗”都应理解为“研究中的潜在适应证”。</p>
            </div>
            <div class="legend">
              <div class="legend-card teal">
                <strong>低强度调控</strong>
                <span>通常指可逆 neuromodulation，目前绝大多数精神科应用还处于早期临床。</span>
              </div>
              <div class="legend-card hybrid">
                <strong>双路线靶点</strong>
                <span>同一个解剖靶点同时存在可逆调控和 MRgFUS 消融两条研发路径。</span>
              </div>
              <div class="legend-card danger">
                <strong>MRgFUS 消融</strong>
                <span>属于不可逆病灶制作，风险、适应证与低强度调控完全不同。</span>
              </div>
            </div>
          </div>

          <div class="stage">
            <div class="brain-card">
              <div class="brain-wrap">
                <div class="brain-guide">
                  <span><i class="guide-chip"></i>彩色半透明区 = 可点击靶点</span>
                  <span><i class="guide-outline"></i>中文文字 = 解剖导视</span>
                </div>
                <div class="brain-caption">Keynote-Style 3D Cutaway</div>
                <div class="popup-shell">
                  <div class="spotlight" id="spotlight"></div>
                  <div class="popup-card" id="popup" data-side="right"></div>
                </div>
                <svg viewBox="0 0 760 560" role="img" aria-label="聚焦超声脑区交互图">
                  <defs>
                    <clipPath id="brainClip">
                      <path d="M142 270 C114 196 136 120 210 88 C292 51 414 58 522 104 C614 143 680 219 684 298 C687 363 653 437 570 486 C496 531 364 534 266 503 C207 485 172 479 145 489 C118 500 94 489 83 468 C70 443 77 413 95 381 C112 349 120 313 142 270 Z" />
                    </clipPath>
                    <clipPath id="cerebellumClip">
                      <path d="M510 376 C553 372 589 390 603 428 C616 468 594 506 556 522 C515 540 468 523 450 487 C437 460 442 417 468 394 C480 382 495 377 510 376 Z" />
                    </clipPath>
                    <filter id="brainDepth" x="-20%" y="-20%" width="140%" height="160%">
                      <feDropShadow dx="0" dy="26" stdDeviation="18" flood-color="#02060c" flood-opacity="0.44" />
                      <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#57d8ff" flood-opacity="0.08" />
                    </filter>
                    <filter id="stageBlur" x="-30%" y="-30%" width="160%" height="160%">
                      <feGaussianBlur stdDeviation="16" />
                    </filter>
                    <filter id="subsurfaceSoftGlow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="3" result="blur" />
                      <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 0.96 0 0 0  0 0 0.92 0 0  0 0 0 0.38 0" />
                    </filter>
                    <linearGradient id="cortexGradient" x1="0%" x2="100%" y1="0%" y2="100%">
                      <stop offset="0%" stop-color="#ffd9cb" />
                      <stop offset="28%" stop-color="#f7c2b2" />
                      <stop offset="62%" stop-color="#db8f8a" />
                      <stop offset="100%" stop-color="#945d66" />
                    </linearGradient>
                    <radialGradient id="brainGlowGradient" cx="50%" cy="50%" r="50%">
                      <stop offset="0%" stop-color="#6be2ff" stop-opacity="0.42" />
                      <stop offset="55%" stop-color="#63b2ff" stop-opacity="0.16" />
                      <stop offset="100%" stop-color="#63b2ff" stop-opacity="0" />
                    </radialGradient>
                    <radialGradient id="shellHighlightGradient" cx="28%" cy="18%" r="74%">
                      <stop offset="0%" stop-color="#fff6f1" stop-opacity="0.92" />
                      <stop offset="34%" stop-color="#ffd6c8" stop-opacity="0.42" />
                      <stop offset="100%" stop-color="#ffd6c8" stop-opacity="0" />
                    </radialGradient>
                    <radialGradient id="whiteMatterGradient" cx="42%" cy="34%" r="78%">
                      <stop offset="0%" stop-color="#fffdf8" />
                      <stop offset="65%" stop-color="#fbf3e7" />
                      <stop offset="100%" stop-color="#efe0cd" />
                    </radialGradient>
                    <radialGradient id="stageGlowGradient" cx="50%" cy="50%" r="50%">
                      <stop offset="0%" stop-color="#6fe4ff" stop-opacity="0.58" />
                      <stop offset="58%" stop-color="#4e84ff" stop-opacity="0.20" />
                      <stop offset="100%" stop-color="#4e84ff" stop-opacity="0" />
                    </radialGradient>
                    <linearGradient id="cerebellumGradient" x1="0%" x2="100%" y1="0%" y2="100%">
                      <stop offset="0%" stop-color="#f1cbbc" />
                      <stop offset="100%" stop-color="#9f6772" />
                    </linearGradient>
                    <linearGradient id="stemGradient" x1="0%" x2="0%" y1="0%" y2="100%">
                      <stop offset="0%" stop-color="#f6ddcf" />
                      <stop offset="100%" stop-color="#b58d87" />
                    </linearGradient>
                  </defs>
                  <ellipse class="stage-shadow" cx="390" cy="504" rx="228" ry="36" filter="url(#stageBlur)" />
                  <ellipse class="stage-rim" cx="391" cy="504" rx="182" ry="19" />
                  <ellipse class="brain-back-glow" cx="388" cy="284" rx="244" ry="188" filter="url(#stageBlur)" />
                  <g class="brain-object">
                  <path class="cortex-shadow" d="M142 270 C116 202 136 132 205 96 C278 58 401 60 505 105 C595 144 661 219 666 292 C670 351 638 424 561 469 C487 512 362 516 275 490 C220 473 180 469 149 478 C121 486 98 474 89 453 C80 433 86 406 99 378 C115 344 116 302 142 270 Z" />
                  <path class="cortex-shell" d="M142 270 C114 196 136 120 210 88 C292 51 414 58 522 104 C614 143 680 219 684 298 C687 363 653 437 570 486 C496 531 364 534 266 503 C207 485 172 479 145 489 C118 500 94 489 83 468 C70 443 77 413 95 381 C112 349 120 313 142 270 Z" />
                  <path class="cortex-inner-shade" d="M171 264 C159 210 178 151 233 122 C306 82 413 89 503 128 C571 157 621 213 625 278 C630 337 603 394 541 430 C484 462 391 466 315 451 C254 439 210 415 186 378 C170 351 164 306 171 264 Z" />
                  <path class="shell-highlight" d="M209 126 C288 74 411 73 518 119 C570 141 610 171 631 208 C579 184 515 170 446 166 C352 160 277 175 213 205 C188 185 186 149 209 126 Z" />
                  <path class="shell-highlight soft" d="M182 292 C247 258 338 246 430 252 C508 256 578 275 633 310 C619 361 582 404 530 432 C469 466 379 470 299 457 C227 444 181 400 168 337 C166 321 171 305 182 292 Z" />
                  <path class="cortex-rim" d="M153 260 C131 201 149 136 216 105 C294 68 408 76 506 118 C592 154 649 223 653 292 C656 352 625 414 554 457 C485 498 369 501 286 475" />
                  <g clip-path="url(#brainClip)">
                    <path class="sulcus deep" d="M178 176 C215 150 269 136 328 139 C390 141 453 158 507 192" />
                    <path class="sulcus" d="M168 214 C221 181 299 171 382 179 C452 186 518 207 567 246" />
                    <path class="sulcus deep" d="M160 258 C232 221 334 213 439 226 C507 235 564 255 608 286" />
                    <path class="sulcus" d="M164 304 C246 273 357 271 464 285 C531 294 587 315 626 340" />
                    <path class="sulcus" d="M186 349 C263 330 359 333 448 349 C507 359 556 377 593 404" />
                    <path class="sulcus fine" d="M212 147 C247 128 292 121 340 123 C385 124 430 133 470 154" />
                    <path class="sulcus fine" d="M227 195 C286 167 375 168 458 190" />
                    <path class="sulcus fine" d="M218 240 C295 213 398 218 501 245" />
                    <path class="sulcus fine" d="M232 289 C315 268 418 276 518 304" />
                    <path class="sulcus fine" d="M250 337 C329 325 420 336 503 360" />
                    <path class="sulcus fine" d="M287 383 C343 376 405 383 459 399" />
                    <path class="sulcus" d="M477 146 C533 170 579 210 603 255" />
                    <path class="sulcus fine" d="M522 178 C559 203 588 235 606 269" />
                  </g>
                  <path class="white-matter" d="M196 164 C270 110 406 112 520 172 C584 207 609 277 585 348 C559 423 446 459 313 452 C221 447 161 396 151 320 C144 265 156 199 196 164 Z" />
                  <path class="white-matter-shadow" d="M223 195 C292 149 400 150 500 200 C545 223 571 261 572 303 C572 360 528 406 457 431 C389 455 288 451 222 423 C182 406 162 370 160 321 C159 273 177 227 223 195 Z" />
                  <path class="corpus-callosum" d="M275 187 C318 148 394 146 449 180 C473 195 482 230 466 252 C446 279 398 289 340 281 C300 276 265 253 255 224 C249 208 256 194 275 187 Z" />
                  <path class="midline-cut" d="M369 122 C363 168 360 214 362 261 C363 314 370 368 385 425" />
                  <path class="lobe-zone frontal-zone" d="M191 165 C239 125 327 121 399 139 C389 182 361 226 319 254 C266 288 213 283 182 239 C167 214 173 187 191 165 Z" />
                  <path class="lobe-zone cingulate-zone" d="M278 178 C320 150 395 149 447 178 C450 197 440 212 421 223 C387 243 325 241 289 222 C273 213 270 193 278 178 Z" />
                  <path class="lobe-zone deep-zone" d="M290 220 C335 194 407 201 450 235 C451 289 416 332 355 340 C307 344 279 315 277 271 C276 251 281 234 290 220 Z" />
                  <path class="lobe-zone temporal-zone" d="M398 275 C439 266 486 278 516 307 C512 345 484 377 442 385 C406 390 378 365 378 327 C378 307 385 287 398 275 Z" />
                  <path class="deep-structure" d="M314 214 C340 191 391 193 423 216 C409 235 380 248 344 247 C331 244 321 232 314 214 Z" />
                  <path class="deep-structure" d="M299 232 C329 212 370 220 388 246 C373 266 346 274 319 269 C299 260 291 244 299 232 Z" />
                  <path class="ventricle" d="M332 208 C347 198 374 198 389 208 C383 220 370 228 352 228 C342 226 334 219 332 208 Z" />
                  <path class="ventricle" d="M341 227 C356 219 376 220 387 231 C380 241 366 247 351 246 C343 243 339 236 341 227 Z" />
                  <path class="deep-structure" d="M421 292 C450 279 482 281 510 297 C513 322 487 345 451 348 C425 344 413 322 421 292 Z" />
                  <ellipse class="deep-structure" cx="448" cy="314" rx="28" ry="20" transform="rotate(24 448 314)" />
                  <ellipse class="deep-structure" cx="394" cy="250" rx="35" ry="23" />
                  <path class="deep-structure" d="M329 244 C339 231 357 228 367 233 C357 259 356 292 369 322 C356 329 340 320 331 304 C323 287 321 259 329 244 Z" />
                  <path class="hippocampus" d="M404 315 C425 302 451 304 469 319 C468 336 454 349 432 353 C415 352 402 341 399 327 C398 322 400 318 404 315 Z" />
                  <path class="fiber-bundle" d="M285 212 C303 238 318 284 321 327" />
                  <path class="fiber-bundle" d="M455 197 C431 223 418 255 414 292" />
                  <path class="fiber-bundle" d="M330 284 C342 295 352 316 356 338" />
                  <path class="brainstem" d="M498 350 C530 352 553 366 565 392 C577 423 568 467 539 497 C518 518 491 517 482 496 C476 483 478 463 483 440 C459 424 448 399 454 375 C460 355 474 347 498 350 Z" />
                  <path class="cerebellum" d="M510 376 C553 372 589 390 603 428 C616 468 594 506 556 522 C515 540 468 523 450 487 C437 460 442 417 468 394 C480 382 495 377 510 376 Z" />
                  <g clip-path="url(#cerebellumClip)">
                    <path class="cerebellar-fold" d="M462 401 C494 388 528 387 563 396" />
                    <path class="cerebellar-fold" d="M454 420 C490 407 533 409 577 422" />
                    <path class="cerebellar-fold" d="M452 440 C493 425 541 429 587 446" />
                    <path class="cerebellar-fold" d="M457 460 C500 445 545 450 587 466" />
                    <path class="cerebellar-fold" d="M470 481 C507 469 545 472 578 484" />
                    <path class="cerebellar-fold" d="M486 500 C514 493 541 494 564 501" />
                  </g>
                  </g>
                  <path class="anatomy-line" d="M181 189 C229 144 331 136 429 154 C492 166 550 197 577 241" />
                  <path class="anatomy-line soft" d="M177 241 C248 203 370 194 501 214" />
                  <path class="anatomy-line" d="M178 294 C260 261 386 258 540 293" />
                  <path class="anatomy-line soft" d="M208 349 C286 330 403 336 503 366" />
                  <path class="anatomy-line soft" d="M243 171 C315 122 430 131 489 186" />
                  <path class="anatomy-line soft" d="M468 384 C494 405 514 441 519 485" />
                  <path class="anatomy-line soft" d="M500 401 C528 419 545 451 547 486" />
                  <path class="anatomy-line soft" d="M480 369 C509 386 531 416 535 447" />
                  <text class="anatomy-label" x="148" y="156">额叶皮层</text>
                  <text class="anatomy-label" x="286" y="201">扣带回</text>
                  <text class="anatomy-label" x="282" y="255">纹状体</text>
                  <text class="anatomy-label" x="326" y="288">内囊前肢</text>
                  <text class="anatomy-label" x="386" y="249">丘脑</text>
                  <text class="anatomy-label" x="438" y="320">杏仁核</text>
                  <text class="anatomy-label" x="526" y="518">小脑</text>
                  __FOCUS_MARKUP__
                  __TRIGGER_MARKUP__
                </svg>
              </div>
            </div>

            <div class="info-panel">
              <div class="info-label" id="status-pill">研究中</div>
              <h3 id="region-title"></h3>
              <p class="summary" id="region-summary"></p>
              <div class="chip-row" id="chip-row"></div>

              <div class="block">
                <div class="block-title">可能研究方向</div>
                <div class="list" id="conditions"></div>
              </div>

              <div class="block">
                <div class="block-title">代表进展</div>
                <div class="body-copy" id="study"></div>
              </div>

              <div class="block">
                <div class="block-title">证据状态</div>
                <div class="body-copy" id="evidence"></div>
              </div>

              <div class="block">
                <div class="block-title">展示时要保留的风险提示</div>
                <div class="body-copy" id="note"></div>
              </div>
            </div>
          </div>

          <div class="footnote">
            注：不同研究使用的声学参数、导航方式、疗程长度和终点指标差异很大。页面里的“可能治疗”应理解为“正在研究的潜在适应证”，不是临床承诺。
          </div>
        </div>

        <script>
          const regions = __REGIONS_JSON__;
          const popup = document.getElementById("popup");
          const spotlight = document.getElementById("spotlight");
          const title = document.getElementById("region-title");
          const summary = document.getElementById("region-summary");
          const chipRow = document.getElementById("chip-row");
          const conditions = document.getElementById("conditions");
          const study = document.getElementById("study");
          const evidence = document.getElementById("evidence");
          const note = document.getElementById("note");
          const statusPill = document.getElementById("status-pill");

          function escapeHtml(value) {
            return value
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;");
          }

          function render(region) {
            title.textContent = region.title;
            summary.textContent = region.summary;
            statusPill.textContent = region.status;
            statusPill.className = "info-label" + (region.type === "hybrid" ? " hybrid" : "");
            chipRow.innerHTML = [
              region.modality_badge,
              region.evidence_level,
              region.mode
            ].map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");
            conditions.innerHTML = region.conditions
              .map((item) => `<span class="bullet">${escapeHtml(item)}</span>`)
              .join("");
            study.textContent = region.study;
            evidence.textContent = region.evidence;
            note.textContent = region.note;

            popup.innerHTML = `<strong>${escapeHtml(region.short)}</strong><span>${escapeHtml(region.popup)}</span>`;
            popup.style.left = `${(region.x / 760) * 100}%`;
            popup.style.top = `${(region.y / 560) * 100}%`;
            popup.dataset.side = region.popup_side;
            popup.className = "popup-card";
            popup.style.border = `1px solid ${region.accent}`;
            popup.offsetWidth;
            popup.classList.add("visible");

            spotlight.style.left = `${(region.x / 760) * 100}%`;
            spotlight.style.top = `${(region.y / 560) * 100}%`;
            spotlight.className = "spotlight";
            if (region.type === "hybrid") {
              spotlight.classList.add("hybrid");
            }
            spotlight.offsetWidth;
            spotlight.classList.add("visible");

            document.querySelectorAll(".hotspot").forEach((node) => {
              node.classList.toggle("active", node.dataset.id === region.id);
            });
            document.querySelectorAll(".callout-group").forEach((node) => {
              node.classList.toggle("active", node.dataset.id === region.id);
            });
            document.querySelectorAll(".region-layer").forEach((node) => {
              node.classList.toggle("active", node.dataset.id === region.id);
            });
          }

          document.querySelectorAll(".region-trigger").forEach((node) => {
            node.addEventListener("click", () => {
              const region = regions.find((item) => item.id === node.dataset.id);
              if (region) {
                render(region);
              }
            });
          });

          render(regions[0]);
        </script>
      </body>
    </html>
    """
    return (
        html.replace("__FOCUS_MARKUP__", "".join(focus_markup))
        .replace("__TRIGGER_MARKUP__", "".join(trigger_markup))
        .replace("__REGIONS_JSON__", json.dumps(visual_regions, ensure_ascii=False))
    )
