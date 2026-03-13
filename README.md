# 聚焦超声精神科脑区演示

一个面向演示场景的 Streamlit 页面，用可点击脑图展示：

- 聚焦超声可能作用的脑区
- 每个脑区对应的潜在精神科研究方向
- 证据层级、当前研究状态和演示话术
- 参考研究与来源链接

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

启动后直接打开：

```text
http://localhost:8501
```

## 页面内容

当前页面包含：

- 更接近医学插画风格的脑区 SVG
- 点击热点后的动画弹窗
- “治疗方向总览”表格
- PubMed 研究来源折叠区

## 部署

如果你要部署到线上，推荐两种方式：

### 方式 1：GitHub Pages（固定域名）

仓库已经预留了静态导出和 Pages workflow：

- `scripts/export_static_site.py`
- `.github/workflows/deploy-pages.yml`
- `docs/index.html`

如果仓库名仍然是 `shinelicn/casestudy`，最终正式链接会是：

```text
https://shinelicn.github.io/casestudy/
```

### 方式 2：本地 Streamlit

本地启动命令直接用：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## 目录

```text
.
├── app.py
├── modules/
│   └── fus_demo.py
├── requirements.txt
├── render.yaml
├── Dockerfile
└── Procfile
```
