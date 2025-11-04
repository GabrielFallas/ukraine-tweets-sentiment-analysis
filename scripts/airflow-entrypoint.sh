#!/bin/bash

# Custom entrypoint for Airflow webserver
# Initializes connections after Airflow is ready

set -e

# Start Airflow webserver in background
echo "Starting Airflow webserver..."
airflow webserver &
WEBSERVER_PID=$!

# Wait for Airflow to be ready
echo "Waiting for Airflow webserver to be ready..."
timeout=60
counter=0
until curl -s http://localhost:8080/health | grep -q "healthy" || [ $counter -eq $timeout ]; do
    sleep 2
    counter=$((counter + 2))
    echo "Waiting... ($counter/$timeout seconds)"
done

if [ $counter -eq $timeout ]; then
    echo "WARNING: Airflow webserver did not become healthy within ${timeout} seconds"
else
    echo "✓ Airflow webserver is ready!"
    
    # Initialize connections
    if [ -f /opt/airflow/scripts/init-airflow-connections.sh ]; then
        echo "Running connection initialization script..."
        bash /opt/airflow/scripts/init-airflow-connections.sh
    fi
fi

# Wait for webserver process
wait $WEBSERVER_PID
