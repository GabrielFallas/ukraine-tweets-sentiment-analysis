#!/bin/bash

# OpenMetadata Initialization Script
# Configures data sources and lineage tracking

echo "Initializing OpenMetadata connectors..."

# Wait for OpenMetadata to be ready
sleep 30

# Set OpenMetadata URL
OM_URL="http://localhost:8585/api"

# Note: In production, you would use the OpenMetadata CLI or API to configure connectors
# For this demo, we'll document the manual steps

cat << EOF

==================================================================
OpenMetadata Configuration
==================================================================

To complete the OpenMetadata setup, please follow these steps:

1. Access OpenMetadata UI at: http://localhost:8585
   Default credentials: admin / admin

2. Add Service Connections:

   a) Add Airflow Pipeline Service:
      - Go to Settings > Services > Pipeline Services
      - Click "Add New Service"
      - Select "Airflow"
      - Name: ukraine_tweets_airflow
      - Host: http://airflow-webserver:8080
      - Save and run metadata ingestion

   b) Add Druid Database Service:
      - Go to Settings > Services > Database Services
      - Click "Add New Service"
      - Select "Druid"
      - Name: ukraine_tweets_druid
      - Host: druid-router:8888
      - Save and run metadata ingestion

   c) Add Superset Dashboard Service:
      - Go to Settings > Services > Dashboard Services
      - Click "Add New Service"
      - Select "Superset"
      - Name: ukraine_tweets_superset
      - Host: http://superset:8088
      - Username: admin
      - Password: admin
      - Save and run metadata ingestion

   d) Add PostgreSQL Database Service:
      - Go to Settings > Services > Database Services
      - Click "Add New Service"
      - Select "PostgreSQL"
      - Name: ukraine_tweets_postgres
      - Host: postgres
      - Port: 5432
      - Username: airflow
      - Password: airflow
      - Database: airflow
      - Save and run metadata ingestion

3. View Data Lineage:
   - Navigate to "Explore" > "Tables"
   - Select the ukraine_tweets_sentiment table
   - Click on the "Lineage" tab to view data flow

4. Set up Data Quality:
   - Go to any table
   - Click "Profiler & Data Quality"
   - Add quality tests as needed

==================================================================

EOF

echo "OpenMetadata initialization complete!"
echo "Please follow the manual steps above to complete the configuration."
