#!/bin/bash
# Setup Airflow Connections

echo "Setting up Airflow connections..."

# Add PostgreSQL connection
docker exec sentiment-airflow-webserver airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-port '5432' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-schema 'airflow'

echo "✓ PostgreSQL connection added"

# Add Spark connection
docker exec sentiment-airflow-webserver airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master' \
    --conn-port '7077'

echo "✓ Spark connection added"

echo ""
echo "All connections configured successfully!"
echo "You can now run the DAG in Airflow."
