#!/usr/bin/env python3
"""
Main pipeline orchestrator for Mohan Competitive Intelligence
Runs: Skill 1 (discovery) → Skill 2 (research) → Skill 3 (dashboard)
"""

import subprocess
import time
import os
from datetime import datetime
from pathlib import Path
import yaml

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "pipeline.log"

def log_message(msg):
    """Log message to both stdout and file"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(log_file, "a") as f:
        f.write(log_entry + "\n")

def run_skill(skill_name, skill_dir):
    """Run a skill and log results"""
    log_message(f"🚀 Starting {skill_name}...")
    start_time = time.time()
    
    try:
        # Run the skill's main script
        result = subprocess.run(
            ["/usr/bin/python3", f"{skill_dir}/run.py"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=skill_dir
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            log_message(f"✅ {skill_name} completed in {elapsed:.1f}s")
            return True
        else:
            log_message(f"❌ {skill_name} failed")
            log_message(f"STDOUT: {result.stdout[:500]}")
            log_message(f"STDERR: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message(f"❌ {skill_name} timeout after 10 minutes")
        return False
    except Exception as e:
        log_message(f"❌ {skill_name} error: {e}")
        return False

def main():
    log_message("=" * 60)
    log_message("MOHAN COMPETITIVE INTELLIGENCE PIPELINE — Daily Run")
    log_message("=" * 60)
    
    # Get config
    config_file = Path(__file__).parent / "config.yaml"
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    sheet_id = config['google_sheets']['sheet_id']
    log_message(f"📊 Using Google Sheet: {sheet_id}")
    
    # Pipeline steps
    skills_dir = Path(__file__).parent / "skills"
    
    steps = [
        ("Skill 1: Competitor Discovery", skills_dir / "competitor-discovery"),
        ("Skill 2: Competitor Research", skills_dir / "competitor-research"),
        ("Skill 3: Competitor Dashboard", skills_dir / "competitor-dashboard"),
    ]
    
    results = {}
    start_time = time.time()
    
    for step_name, skill_dir in steps:
        if not skill_dir.exists():
            log_message(f"⚠️  Skipping {step_name} — directory not found")
            results[step_name] = "SKIPPED"
            continue
        
        success = run_skill(step_name, skill_dir)
        results[step_name] = "SUCCESS" if success else "FAILED"
        
        if not success:
            log_message(f"⚠️  Pipeline halted at {step_name}")
            break
    
    # Summary
    total_time = time.time() - start_time
    log_message("=" * 60)
    log_message(f"PIPELINE SUMMARY")
    for step, status in results.items():
        log_message(f"  {step}: {status}")
    log_message(f"Total time: {total_time:.1f}s")
    log_message("=" * 60)
    
    # Check if all passed
    all_passed = all(status == "SUCCESS" for status in results.values())
    if all_passed:
        log_message("✅ Daily pipeline completed successfully")
        return 0
    else:
        log_message("❌ Daily pipeline failed — check logs above")
        return 1

if __name__ == "__main__":
    exit(main())
