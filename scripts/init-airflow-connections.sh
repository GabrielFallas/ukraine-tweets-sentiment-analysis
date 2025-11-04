#!/bin/bash

# Initialize Airflow connections
# This script runs after Airflow is ready to set up required connections

set -e

echo "Waiting for Airflow to be ready..."
sleep 10

echo "Creating Airflow connections..."

# Check if postgres_default connection exists
if airflow connections get postgres_default &>/dev/null; then
    echo "✓ postgres_default connection already exists"
else
    echo "Creating postgres_default connection..."
    airflow connections add 'postgres_default' \
        --conn-type 'postgres' \
        --conn-host 'postgres' \
        --conn-schema 'sentiment' \
        --conn-login 'airflow' \
        --conn-password 'airflow' \
        --conn-port 5432
    echo "✓ postgres_default connection created"
fi

# Check if spark_default connection exists
if airflow connections get spark_default &>/dev/null; then
    echo "✓ spark_default connection already exists"
else
    echo "Creating spark_default connection..."
    airflow connections add 'spark_default' \
        --conn-type 'spark' \
        --conn-host 'spark://spark-master' \
        --conn-port 7077
    echo "✓ spark_default connection created"
fi

echo "All Airflow connections configured successfully!"
