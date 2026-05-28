# Deployment Checklist — Mohan Competitive Intelligence

## ✅ Pre-Deployment Status

- ✅ 3 Skills designed + tested (competitor-discovery, competitor-research, competitor-dashboard)
- ✅ Google Sheet created: `1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU`
- ✅ config.yaml updated with Sheet ID
- ✅ Pipeline orchestrator created (run_pipeline.py)
- ✅ Cron setup script prepared (setup_cron.sh)
- ✅ All skills tested individually (Skill 1 real web search validation passed)

---

## 🚀 Deployment Steps (5 minutes)

### Step 1: Verify Directory Structure

```bash
cd ~/.openclaw/competitor-intel
ls -la skills/
# Should show: competitor-discovery, competitor-research, competitor-dashboard
```

### Step 2: Test Pipeline Orchestrator

```bash
# Run once manually to verify everything works
python3 run_pipeline.py
```

Expected output:
```
[...] MOHAN COMPETITIVE INTELLIGENCE PIPELINE — Daily Run
[...] 🚀 Starting Skill 1: Competitor Discovery...
[...] ✅ Skill 1 completed in X.Xs
[...] 🚀 Starting Skill 2: Competitor Research...
[...] ✅ Skill 2 completed in X.Xs
[...] 🚀 Starting Skill 3: Competitor Dashboard...
[...] ✅ Skill 3 completed in X.Xs
[...] ✅ Daily pipeline completed successfully
```

### Step 3: Create Logs Directory

```bash
mkdir -p ~/.openclaw/competitor-intel/logs
chmod 755 logs
```

### Step 4: Setup Cron Job

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

This will:
- ✅ Create cron job for 18:00 EST (6 PM) daily
- ✅ Set up logging to `logs/cron.log`

Verify:
```bash
crontab -l | grep run_pipeline
```

### Step 5: Monitor First Run

The cron job will run automatically at 18:00 EST today. Monitor progress:

```bash
# Watch logs in real-time
tail -f logs/cron.log

# Or check Google Sheet directly
# Link: https://docs.google.com/spreadsheets/d/1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU
```

---

## 📊 What Happens Daily (18:00 EST)

1. **Skill 1: Discovery** (~15 min)
   - Scans 16 data sources
   - Finds new competitors
   - Adds to `discovery_queue` tab

2. **Skill 2: Research** (~45 min)
   - Deep research on all companies
   - Cross-validates data from 2+ sources
   - Auto-merges field updates
   - Logs changes to `update_log` tab

3. **Skill 3: Dashboard** (~10 min)
   - Generates static HTML dashboard
   - Exports CSVs to GitHub
   - Archives old data
   - Pushes to `/data/` and `/dashboard/` directories

---

## 🔍 Post-Deployment Verification

### Check 1: Google Sheet Updated

Go to: https://docs.google.com/spreadsheets/d/1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU

Look for:
- ✅ `update_log` tab has new entries
- ✅ `discovery_queue` tab shows newly discovered competitors
- ✅ `companies` tab has updated team sizes / funding info

### Check 2: GitHub Auto-Push

Go to: https://github.com/jajamoa/competitor-intel

Look for:
- ✅ New commits in `/data/` (CSV exports)
- ✅ New commits in `/dashboard/` (HTML)
- ✅ Commit messages with `[auto]` prefix

### Check 3: Logs

```bash
cat logs/cron.log
# Should show successful skill execution
```

---

## ⚠️ Troubleshooting

### Cron Not Running

```bash
# Check if cron service is running
crontab -l

# If missing, re-run
./setup_cron.sh

# Check system logs
log stream --predicate 'eventMessage contains[cd] "cron"'
```

### Google Sheet Not Updating

```bash
# Check if sheet ID is correct
cat config.yaml | grep sheet_id

# Verify credentials
gcloud auth list

# Check logs
tail -f logs/cron.log
```

### Skills Failing

Run manually to debug:
```bash
cd skills/competitor-discovery
python3 run.py
```

---

## 📞 Support Contacts

- **Sheet ID Issue**: Check `config.yaml` line for `sheet_id`
- **Cron Issue**: Check `crontab -l` and `logs/cron.log`
- **Skill Issue**: Run skill manually and check error output

---

## 🎯 Success Criteria

✅ All checks passed when:
1. Cron job shows in `crontab -l`
2. `logs/cron.log` shows successful runs
3. Google Sheet auto-updates daily
4. New competitors found in `discovery_queue`
5. GitHub shows auto-push commits

---

## 📅 First Run Timeline

- **18:00 EST**: Cron triggers pipeline
- **18:15 EST**: Skill 1 finishes (discovery)
- **19:00 EST**: Skill 2 finishes (research + merge)
- **19:10 EST**: Skill 3 finishes (dashboard export)
- **19:10 EST**: GitHub auto-push completes

Check logs after 19:15 EST to verify success.

