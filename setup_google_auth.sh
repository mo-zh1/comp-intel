#!/bin/bash

# Google Sheets API Authentication Setup Script
# Run this on your local machine (not in sandbox)

set -e

echo "🔧 Google Sheets API Authentication Setup"
echo "=========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud not found. Install Google Cloud SDK first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud found"
echo ""

# Option 1: OAuth for personal account
echo "Configuring OAuth for application default credentials..."
echo ""
echo "This will open a browser to authenticate with your Google account."
echo "Please follow the prompts and select your Google account."
echo ""
read -p "Press Enter to continue..."

gcloud auth application-default login --scopes=https://www.googleapis.com/auth/spreadsheets

# Verify
if [ -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "✅ Application Default Credentials configured successfully"
    echo "📍 Location: ~/.config/gcloud/application_default_credentials.json"
else
    echo "❌ Authentication setup failed"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "You can now run the pipeline:"
echo "   cd ~/.openclaw/competitor-intel"
echo "   python3 run_pipeline.py"
