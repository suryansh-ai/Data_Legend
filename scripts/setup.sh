#!/bin/bash
# Data Legend — One-time setup script
set -e

echo "=========================================="
echo "Data Legend — Setup"
echo "=========================================="

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create Lakebase schema via SQL Warehouse
if [ -n "$WAREHOUSE_ID" ]; then
    echo ""
    echo "Creating Lakebase schema..."
    databricks sql execute \
        --warehouse-id "$WAREHOUSE_ID" \
        --file scripts/create_tables.sql
    echo "Schema created."
else
    echo ""
    echo "Skipping Lakebase schema (set WAREHOUSE_ID to enable)"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Deploy: bash scripts/deploy.sh"
echo "2. Or run locally: python -m streamlit run app/main.py"
