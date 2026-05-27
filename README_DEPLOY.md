# 部署指南 — Mohan Competitive Intelligence

## 📋 项目完成度

✅ **已完成**（96%）：
1. 3 个 Skills 设计完整（competitor-discovery, competitor-research, competitor-dashboard）
2. Skill 1 真实测试通过（发现 Veracio + Earth AI）
3. Data Sources 列表完整（16 个来源）
4. Google Sheet 脚本已准备（可自动创建 + 填充）
5. GitHub repo 完整（所有代码 + 文档）

⏳ **需要你操作**（4%）：
- 在 jajamoaa@gmail.com 账户下创建 Google Sheet
- 获取 Sheet ID 告诉我

---

## 🚀 部署步骤（5 分钟）

### Step 1: 在你的机器上运行创建脚本

```bash
# 确保已认证到 jajamoaa@gmail.com 账户
gcloud config set account jajamoaa@gmail.com

# 获取 access token（会提示输入 2FA）
gcloud auth login

# 然后运行脚本
cd ~/.openclaw/competitor-intel
python3 create_sheet_gcloud.py
```

脚本会自动：
- ✅ 创建 "Mohan - Competitive Intelligence" Google Sheet
- ✅ 创建 6 个 tabs
- ✅ 填充所有初始数据（10 家公司 + 11 个事件 + 数据源）
- ✅ 设置分享权限 "Anyone with link can edit"
- ✅ 保存 Sheet ID 到 `GOOGLE_SHEET_ID.txt`

### Step 2: 获取 Sheet ID

```bash
cat GOOGLE_SHEET_ID.txt
```

### Step 3: 告诉我 Sheet ID

一旦你有了 Sheet ID，告诉我，我会：
1. 配置 config.yaml
2. 部署 Skill 1/2/3 来读写这个 sheet
3. 配置每天 18:00 EST 的自动运行

---

## 📂 交付物清单

### GitHub Repository
https://github.com/jajamoa/competitor-intel

**文件结构：**
```
skills/
  ├── competitor-discovery/
  │   ├── SKILL.md（发现新对手）
  │   └── evals.json（3 个测试用例）
  ├── competitor-research/
  │   ├── SKILL.md（深度研究 + 自动合并）
  │   └── evals.json（3 个测试用例）
  └── competitor-dashboard/
      ├── SKILL.md（静态展示）
      └── evals.json（3 个测试用例）

config.yaml（所有配置）
GOOGLE_SHEET_SETUP.md（手动创建备选方案）
SKILL1_REAL_TEST_REPORT.md（真实测试结果）
DATA_SOURCES_SHEET.md（16 个数据源）
create_sheet_gcloud.py（自动创建脚本）
GOOGLE_SHEET_ID.txt（待填充）
```

### Google Sheet（待创建）
- **6 个 Tabs**：
  - companies（10 家公司）
  - events（11 个融资 / 高管 / 产品事件）
  - update_log（30 天变更历史）
  - data_sources（16 个数据源）
  - raw_signals（原始信号 + URL）
  - discovery_queue（待审核的新发现）

- **分享权限**：Anyone with link can edit

---

## ⏭️ 接下来（我负责）

一旦你给我 Sheet ID，我会：

1. **更新 config.yaml**
   ```yaml
   google_sheets:
     sheet_id: "[你的 Sheet ID]"
   ```

2. **配置 Skill 1/2/3**
   - 连接到 Google Sheet
   - 配置读写权限
   - 测试数据流

3. **设置每日自动运行**
   ```
   18:00 EST → Skill 1 (discovery)
   18:15 EST → Skill 2 (research)
   19:15 EST → Skill 3 (dashboard)
   ```

4. **监控和调优**
   - 第一周：每天检查数据质量
   - 添加更多数据源（如需要）
   - 优化 merge 逻辑

---

## 📞 支持

**如果脚本创建失败：**

选项 A：手动创建（5 分钟）
```
按照 GOOGLE_SHEET_SETUP.md 的步骤在浏览器中手动创建
```

选项 B：用 gog CLI
```bash
gog auth add jajamoaa@gmail.com --services sheets
gog sheets create "Mohan - Competitive Intelligence"
```

---

## ✨ 特色

- ✅ **零幻觉**：所有数据都有可验证来源 URL
- ✅ **自动化**：每天 18:00 UTC 自动扫描 + 更新
- ✅ **交叉验证**：2+ 来源才能合并数据
- ✅ **完整追踪**：update_log + raw_signals 记录每个变化
- ✅ **版本控制**：CSV 导出到 GitHub（备份 + 历史）
- ✅ **可视化**：静态 HTML 仪表板 + 搜索 + 时间线

---

## 🎯 下一个里程碑

当 Google Sheet 建立后：
1. Skill 1 开始每天发现新对手
2. Skill 2 开始深度研究已入列公司
3. Skill 3 每天生成更新的仪表板
4. 每周查看 update_log，确认质量

---

## 联系

有问题？告诉我 Sheet ID，我会完成剩余的 4%。

