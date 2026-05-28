# 最终验证 — Google Sheets API 认证

## 状态：需要在你本机运行认证

sandbox 环境（OpenClaw）无法进行交互式浏览器认证。这是技术限制，无法绕过。

---

## ✅ 代码已完成

所有 3 个 Skills 都已准备好，现在支持多种认证方式：

1. **Application Default Credentials (ADC)** — 推荐
2. **gcloud 缓存的 token**
3. **Service Account 密钥**
4. **环境变量** (`GOOGLE_APPLICATION_CREDENTIALS`)

---

## 🚀 需要你做的：在本机上运行一次

### 方式 A: 使用 OAuth (推荐)

```bash
# 在你的本机（Mac/Linux），有浏览器的地方

# 1. 登录
gcloud auth login

# 2. 设置应用默认凭证
gcloud auth application-default login

# 3. 选择你的 Google 账户
# 4. 授予权限

# 完成后，凭证会保存到：
# ~/.config/gcloud/application_default_credentials.json
```

完成后，所有 Skills 会自动使用这个凭证。

### 方式 B: 使用 Service Account（如果你有企业 Google Workspace）

1. 去 Google Cloud Console
2. 创建 Service Account
3. 下载 JSON 密钥
4. 设置环境变量：
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

---

## ✅ 完成后验证

在 sandbox 或本机运行：

```bash
cd ~/.openclaw/competitor-intel
python3 auth_helper.py
```

应该看到：
```
Testing Google Sheets credentials...
✅ Using Application Default Credentials
✅ Credentials working! Sheet: Mohan - Competitive Intelligence
```

---

## 🚀 一旦认证完成

所有 Skills 会自动工作：

```bash
# 完整端到端测试
python3 run_pipeline.py

# 或设置 Cron 自动运行
./setup_cron.sh
```

---

## 📋 当前代码状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Skill 1: Discovery | ✅ 就绪 | 读/写 Google Sheets |
| Skill 2: Research | ✅ 就绪 | 交叉验证 + 合并 |
| Skill 3: Dashboard | ✅ 就绪 | CSV + HTML 导出 |
| Auth Helper | ✅ 完成 | 支持 4 种认证方式 |
| Pipeline Orchestrator | ✅ 完成 | 顺序运行 Skills |

**所有代码已在 GitHub:**  
https://github.com/jajamoa/competitor-intel

---

## ⏸️ 为什么不能在 Sandbox 自动化

1. **交互式认证需要浏览器** — sandbox 没有 GUI
2. **OAuth flow 需要用户确认** — 无法跳过
3. **Service Account 需要密钥文件** — 你需要提供

---

## 💡 最快的方式

你的本机上：
```bash
# 3 个命令
gcloud auth login
gcloud auth application-default login
echo "✅ Done"

# 然后任何地方都可以用（包括 sandbox）
python3 ~/.openclaw/competitor-intel/run_pipeline.py
```

就这么简单。

---

## 下一步

1. **你本机运行认证**（一次性，5 分钟）
2. **验证** `python3 auth_helper.py` 成功
3. **部署** `./setup_cron.sh` 设置每日自动运行

所有代码和脚本都已准备好，只差这一步认证。

