from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.fus_demo import (  # noqa: E402
    FUS_BRAIN_REGIONS,
    FUS_REFERENCE_LINKS,
    build_fus_brain_demo_html,
    build_fus_treatment_overview,
)


def build_appendix_html() -> str:
    overview = build_fus_treatment_overview(FUS_BRAIN_REGIONS)
    headers = overview.columns.tolist()
    header_html = "".join(f"<th>{header}</th>" for header in headers)

    row_html = []
    for row in overview.to_dict(orient="records"):
        cells = "".join(f"<td>{row[header]}</td>" for header in headers)
        row_html.append(f"<tr>{cells}</tr>")

    refs_html = "".join(
        f'<li><a href="{ref["url"]}" target="_blank" rel="noreferrer">{ref["label"]}</a></li>'
        for ref in FUS_REFERENCE_LINKS
    )

    return f"""
    <style>
      .page-shell {{
        max-width: 1220px;
        margin: 0 auto;
        padding: 0 24px 56px;
      }}

      .section-card {{
        margin-top: 18px;
        background: rgba(255, 251, 246, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.52);
        border-radius: 30px;
        box-shadow: 0 28px 90px rgba(58, 50, 42, 0.14);
        padding: 24px;
      }}

      .section-card h3 {{
        margin: 0 0 8px;
        font-size: 28px;
        line-height: 1.14;
      }}

      .section-card p {{
        margin: 0 0 16px;
        color: var(--muted);
        line-height: 1.68;
      }}

      .table-wrap {{
        overflow-x: auto;
        border-radius: 20px;
        border: 1px solid rgba(33, 52, 59, 0.08);
        background: rgba(255, 255, 255, 0.72);
      }}

      table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 980px;
      }}

      thead {{
        background: rgba(15, 123, 118, 0.08);
      }}

      th,
      td {{
        text-align: left;
        vertical-align: top;
        padding: 14px 16px;
        border-bottom: 1px solid rgba(33, 52, 59, 0.08);
        font-size: 14px;
        line-height: 1.55;
      }}

      th {{
        font-size: 12px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--muted);
      }}

      .ref-list {{
        margin: 0;
        padding-left: 18px;
      }}

      .ref-list li {{
        margin: 0 0 10px;
        color: var(--ink);
        line-height: 1.6;
      }}

      .ref-list a {{
        color: var(--teal);
        text-decoration: none;
      }}

      .ref-list a:hover {{
        text-decoration: underline;
      }}
    </style>

    <div class="page-shell">
      <section class="section-card">
        <h3>治疗方向总览</h3>
        <p>这张表适合正式线上演示时快速扫一遍。点击上方脑图热点，再讲对应靶点的详细证据和风险提示。</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>{header_html}</tr>
            </thead>
            <tbody>
              {''.join(row_html)}
            </tbody>
          </table>
        </div>
      </section>

      <section class="section-card">
        <h3>参考研究与来源</h3>
        <p>以下链接均指向公开来源页，适合在正式演示或会后追溯时使用。</p>
        <ul class="ref-list">
          {refs_html}
        </ul>
      </section>
    </div>
    """


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    html = build_fus_brain_demo_html(FUS_BRAIN_REGIONS)
    appendix = build_appendix_html()
    final_html = html.replace("</body>", f"{appendix}</body>")
    (DOCS_DIR / "index.html").write_text(final_html, encoding="utf-8")
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
