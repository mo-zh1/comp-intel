# 最终设置指南 - Google Sheet 自动创建

## 前置条件

Google Sheets API 需要认证。有三个选项：

### 选项 1: 使用 gcloud 认证（推荐）

```bash
# 1. 登录 gcloud（只需一次）
gcloud auth application-default login

# 2. 选择你的 Google 账户 (jajamoaa@gmail.com)
# 3. 授予权限

# 4. 运行创建脚本
cd ~/.openclaw/competitor-intel
python3 create_sheet_direct.py
```

输出会是：
```
✅ Spreadsheet created: [SHEET_ID]
✅ Sharing enabled: Anyone with link can edit
✅ Google Sheet created successfully!
📊 Sheet ID: [SHEET_ID]
🔗 Link: https://docs.google.com/spreadsheets/d/[SHEET_ID]
```

---

### 选项 2: 使用 gog CLI（如果已配置）

```bash
# 需要先设置 gog 认证（一次性）
gog auth credentials /path/to/credentials.json
gog auth add jajamoaa@gmail.com --services sheets

# 然后运行
gog sheets create "Mohan - Competitive Intelligence" --account jajamoaa@gmail.com
```

---

### 选项 3: 完全手动（如果 API 配置困难）

如果上面两个选项都不行，按照 `GOOGLE_SHEET_SETUP.md` 手动创建 sheet。

---

## 推荐步骤

### 第一步：设置认证

在终端中运行：

```bash
gcloud auth application-default login
```

这会打开浏览器让你登录。选择 `jajamoaa@gmail.com`，然后授予权限。

### 第二步：运行创建脚本

```bash
cd ~/.openclaw/competitor-intel
python3 create_sheet_direct.py
```

脚本会：
1. ✅ 创建 "Mohan - Competitive Intelligence" Google Sheet
2. ✅ 创建 6 个 tabs（companies, events, update_log, data_sources, raw_signals, discovery_queue）
3. ✅ 填充所有初始数据
4. ✅ 设置分享权限为 "Anyone with link can edit"
5. ✅ 保存 Sheet ID 到 `GOOGLE_SHEET_ID.txt`

### 第三步：配置 Skills

脚本完成后，更新 `config.yaml`：

```yaml
google_sheets:
  sheet_id: "[从 GOOGLE_SHEET_ID.txt 复制]"
  tabs:
    companies: "companies"
    events: "events"
    update_log: "update_log"
    data_sources: "data_sources"
    raw_signals: "raw_signals"
    discovery_queue: "discovery_queue"
```

---

## 现在就做

```bash
# 1. 认证
gcloud auth application-default login

# 2. 创建并填充 Google Sheet
cd ~/.openclaw/competitor-intel
python3 create_sheet_direct.py

# 3. 复制 Sheet ID
cat GOOGLE_SHEET_ID.txt

# 4. 更新 config.yaml
# 编辑 config.yaml，替换 sheet_id 值
```

完成后，告诉我 Sheet ID，我就能配置 Skill 1/2/3 来读写这个 sheet。

---

## 失败排查

**如果 `gcloud auth application-default login` 失败：**
- 确保已安装 Google Cloud SDK：`gcloud --version`
- 如果没安装：`brew install google-cloud-sdk`

**如果脚本说"Missing credentials"：**
- 再次运行 `gcloud auth application-default login`
- 确保选择了 `jajamoaa@gmail.com` 账户

**如果脚本运行超时：**
- 可能是网络问题，重试即可

**最后的办法：**
- 按照 `GOOGLE_SHEET_SETUP.md` 手动创建 sheet（5 分钟）

