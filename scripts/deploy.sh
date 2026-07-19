#!/bin/bash
# Data Legend — Deploy to Databricks
set -e

echo "=========================================="
echo "Data Legend — Deploy to Databricks"
echo "=========================================="

# Check login
if ! databricks workspace list > /dev/null 2>&1; then
    echo "Error: Not logged in. Run: databricks configure"
    exit 1
fi

echo "Logged in to Databricks."

# Deploy
echo ""
echo "Deploying Data Legend..."
databricks apps deploy data-legend \
    --source . \
    --overwrite

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Note: App may take a few minutes to start."
echo "Auto-stops after 24 hours of inactivity."
