# 🚀 立即操作 — 创建 Google Sheet

## 现状

项目 95% 完成。缺最后一步：创建 Google Sheet 并获取 Sheet ID。

## 为什么我无法直接做

sandbox 环境中没有交互式浏览器，gcloud/Python 的交互式认证方式都需要人工输入 2FA 或确认。

## 你需要做的（3 种方式，选一个）

### 方式 1：使用提供的 Python 脚本（推荐）

在你的本机（Mac/Linux）上运行：

```bash
# 1. 登录
gcloud auth login

# 2. 创建 Google Sheet
cd ~/.openclaw/competitor-intel
python3 deploy.py
```

脚本会打印 Sheet ID。复制并告诉我。

---

### 方式 2：手动在浏览器创建

按照 `GOOGLE_SHEET_SETUP.md` 的步骤（5 分钟）：
1. 打开 Google Sheets: https://sheets.google.com
2. 新建 6 个 tabs（companies, events, update_log, data_sources, raw_signals, discovery_queue）
3. 复制数据进去
4. 告诉我 Sheet ID

---

### 方式 3：用 gog CLI

```bash
gog auth add jajamoaa@gmail.com --services sheets
gog sheets create "Mohan - Competitive Intelligence"
```

---

## 之后

一旦你给我 Sheet ID，我会：
1. ✅ 配置 config.yaml
2. ✅ 部署 Skill 1/2/3
3. ✅ 配置每天 18:00 EST 自动运行
4. ✅ 完成剩余 5%

---

## 文件已准备

- `deploy.py` — 一键创建 + 填充 Google Sheet
- `create_sheet_gcloud.py` — 详细版本
- `GOOGLE_SHEET_SETUP.md` — 手动步骤
- 所有 skills + 配置 → GitHub

---

## 关键：告诉我 Sheet ID

完成后，运行：

```bash
cat GOOGLE_SHEET_ID.txt
```

复制输出的 ID 告诉我。

