#!/bin/bash

# Setup cron job for daily competitive intelligence pipeline
# Runs at 18:00 EST (6 PM) every day

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRON_JOB="0 18 * * * cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/run_pipeline.py >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo "Setting up cron job for daily competitive intelligence pipeline..."
echo "Schedule: 18:00 EST (6 PM) every day"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_pipeline.py"; then
    echo "✅ Cron job already configured"
    crontab -l | grep "run_pipeline.py"
else
    echo "Creating cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job created successfully"
    echo ""
    crontab -l | grep "run_pipeline.py"
fi

echo ""
echo "📋 Cron job details:"
echo "  Schedule: 0 18 * * * (18:00 EST daily)"
echo "  Timezone: America/New_York"
echo "  Log file: $SCRIPT_DIR/logs/cron.log"
echo ""
echo "To view cron logs:"
echo "  tail -f $SCRIPT_DIR/logs/cron.log"
