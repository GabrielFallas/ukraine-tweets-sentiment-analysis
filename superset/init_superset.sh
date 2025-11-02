#!/bin/bash

# Superset Initialization Script
# Creates Druid connection and dashboards

echo "Initializing Superset with Druid connection and dashboards..."

# Wait for Superset to be ready
sleep 10

# Set admin credentials
export SUPERSET_USERNAME="admin"
export SUPERSET_PASSWORD="admin"

# Login and get access token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${SUPERSET_USERNAME}\", \"password\": \"${SUPERSET_PASSWORD}\", \"provider\": \"db\", \"refresh\": true}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to get access token. Superset may not be fully initialized yet."
    exit 0
fi

echo "Successfully authenticated with Superset"

# Create Druid database connection
echo "Creating Druid database connection..."

DRUID_CONNECTION=$(curl -s -X POST http://localhost:8088/api/v1/database/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "database_name": "Druid",
    "sqlalchemy_uri": "druid://druid-broker:8082/druid/v2/sql/",
    "expose_in_sqllab": true,
    "allow_ctas": false,
    "allow_cvas": false,
    "allow_dml": false
  }')

echo "Druid connection created: $DRUID_CONNECTION"

# Create PostgreSQL database connection for metadata
echo "Creating PostgreSQL database connection..."

POSTGRES_CONNECTION=$(curl -s -X POST http://localhost:8088/api/v1/database/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "database_name": "PostgreSQL",
    "sqlalchemy_uri": "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
    "expose_in_sqllab": true,
    "allow_ctas": false,
    "allow_cvas": false,
    "allow_dml": false
  }')

echo "PostgreSQL connection created: $POSTGRES_CONNECTION"

echo "Superset initialization complete!"
