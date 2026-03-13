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

### GitHub Pages（固定域名）

这个仓库现在已经直接发布到 GitHub Pages，正式链接是：

```text
https://shinelicn.github.io/casestudy/
```

后续更新线上内容，直接在仓库根目录执行一条命令：

```bash
./publish "更新说明"
```

不传提交信息也可以，脚本会自动生成带时间戳的提交说明：

```bash
./publish
```

这条命令会依次完成：

- 校验 `app.py`、`modules/fus_demo.py`、`scripts/export_static_site.py`
- 重新生成 `docs/index.html`
- 自动 `git add` 和 `git commit`
- 拉取远端 `origin/main`
- 必要时自动 rebase
- 把当前分支推送到 `origin/main`

发布脚本在：

- `publish`
- `scripts/publish_pages.sh`
- `scripts/export_static_site.py`

### 本地 Streamlit

本地启动命令直接用：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## 目录

```text
.
├── app.py
├── publish
├── modules/
│   └── fus_demo.py
├── scripts/
│   ├── export_static_site.py
│   └── publish_pages.sh
├── requirements.txt
├── render.yaml
├── Dockerfile
└── Procfile
```
