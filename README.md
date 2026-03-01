# 零售AI决策产品 DEMO

一个可解释的纸尿裤品类商品组合优化 Demo，面向采购经理和店长展示：
- 门店分层（4 类语义 cluster）
- CDT need state
- Halo 联动利润
- 货架与覆盖约束
- 可解释推荐与反事实
- 业务导出与试点评估

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

CLI 导出：

```bash
python3 cli.py
```

测试：

```bash
pytest -q
```

## 一键部署

这个项目已经补齐了以下部署文件：
- `.streamlit/config.toml`
- `render.yaml`
- `Dockerfile`
- `.dockerignore`
- `Procfile`
- `.gitignore`

### 方案 1：Streamlit Community Cloud（最快拿公开链接）

1. 把仓库推到 GitHub。
2. 打开 [Streamlit Community Cloud](https://share.streamlit.io/)。
3. 选择 `New app`。
4. 选择你的 GitHub 仓库。
5. Main file path 填 `app.py`。
6. 点击 `Deploy`。

部署成功后，平台会给你一个可直接分享的公网链接。

推荐设置：
- Python 版本：3.11
- Branch：你的默认分支

### 方案 2：Render Blueprint（接近一键）

1. 把仓库推到 GitHub。
2. 登录 [Render](https://render.com/)。
3. 选择 `New` -> `Blueprint`。
4. 选择这个仓库。
5. Render 会自动识别 `render.yaml`。
6. 点击创建服务。

部署后会得到一个固定公网地址。

### 方案 3：Docker（任意云主机 / 容器平台）

构建镜像：

```bash
docker build -t retail-ai-demo .
```

本地运行：

```bash
docker run -p 8501:8501 retail-ai-demo
```

然后访问：

```text
http://localhost:8501
```

## 线上启动命令

如果你在任意支持 Python 的平台手动填写启动命令，直接用：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

如果平台不提供 `$PORT`，改成固定端口：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 导出文件

运行 `python3 cli.py` 后会输出到 `out/`：
- `decision_table.csv`
- `store_task_sheet.csv`
- `planogram_proxy.csv`
- `one_pager.md`
- `playbook.md`
- `explain_trace.json`

## 目录

```text
.
├── app.py
├── cli.py
├── requirements.txt
├── render.yaml
├── Dockerfile
├── Procfile
├── .streamlit/
│   └── config.toml
├── modules/
└── tests/
```
