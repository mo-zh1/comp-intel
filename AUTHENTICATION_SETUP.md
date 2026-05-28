# Google Sheets API 认证设置指南

## 问题

Skills 现在可以读写 Google Sheets，但需要有效的认证凭证。目前测试环境没有 ADC（Application Default Credentials）配置。

## ✅ Skills 代码已修复

所有 3 个 skills 现在都有真实的 Google Sheets 集成：

### Skill 1: Competitor Discovery
- ✅ 真正读取 `companies` 页面
- ✅ 发现新竞争对手
- ✅ 写入 `discovery_queue` 页面

### Skill 2: Competitor Research  
- ✅ 读取所有公司
- ✅ 深度研究每个公司
- ✅ 应用 2+ 源交叉验证合并逻辑
- ✅ 写入 `update_log` 页面

### Skill 3: Competitor Dashboard
- ✅ 读取 `companies` 和 `events` 页面
- ✅ 生成 CSV 导出
- ✅ 生成 HTML 仪表板

---

## ⏳ 下一步：配置认证

你需要设置 **Google Sheets API 认证**。有 3 个选项：

### 选项 1: Service Account (推荐用于自动化)

1. 去 Google Cloud Console: https://console.cloud.google.com
2. 创建新 Service Account
3. 下载 JSON 密钥文件
4. 设置环境变量：
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```
5. 在 Google Sheet 中与 service account email 共享访问权限

### 选项 2: OAuth (推荐用于个人账户)

```bash
# 在你的本机运行一次
gcloud auth application-default login

# 选择你的 Google 账户
# 授予权限

# 这会生成 ~/.config/gcloud/application_default_credentials.json
```

### 选项 3: User Account Credentials

1. 从 Google API 控制面板创建 OAuth 2.0 凭证
2. 保存到文件
3. 在 skills 中加载

---

## 🔍 测试认证

配置后，运行这个来验证：

```bash
cd ~/.openclaw/competitor-intel
python3 -c "
from google.auth import default
credentials, project = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
print('✅ Credentials configured')
print(f'Project: {project}')
"
```

---

## 📋 目前的测试状态

| Skill | 状态 | 代码 | Google Sheets |
|-------|------|------|----------------|
| 1: Discovery | ✅ 可运行 | ✅ 真实实现 | ⏳ 需要认证 |
| 2: Research | ✅ 可运行 | ✅ 真实实现 | ⏳ 需要认证 |
| 3: Dashboard | ✅ 可运行 | ✅ 真实实现 | ⏳ 需要认证 |

---

## 🚀 一旦认证配置完成

```bash
# 重新运行完整管道
python3 run_pipeline.py

# 这次会：
# ✅ 从 Google Sheet 读取数据
# ✅ 写入发现结果
# ✅ 生成真实的仪表板
```

---

## 📝 注意

- **sandbox 环境**: 无法运行交互式 `gcloud auth login` 
- **解决方案**: 在你的本机运行认证，然后复制凭证文件

如果你需要在 sandbox 中自动化：
1. 在本机运行 `gcloud auth application-default login`
2. 复制 `~/.config/gcloud/application_default_credentials.json`
3. 上传到 sandbox 或设置 env var

---

## 优先级清单

- [ ] 配置 Google Sheets API 认证
- [ ] 设置 GOOGLE_APPLICATION_CREDENTIALS 或运行 gcloud auth login
- [ ] 验证认证工作
- [ ] 运行 `python3 run_pipeline.py` 测试完整流程
- [ ] 监控 Google Sheet 更新

