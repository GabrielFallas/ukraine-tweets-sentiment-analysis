#!/bin/bash

# Initialize multiple databases in PostgreSQL
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE druid;
    CREATE DATABASE superset;
    CREATE DATABASE openmetadata;
    CREATE DATABASE sentiment;
    GRANT ALL PRIVILEGES ON DATABASE druid TO airflow;
    GRANT ALL PRIVILEGES ON DATABASE superset TO airflow;
    GRANT ALL PRIVILEGES ON DATABASE openmetadata TO airflow;
    GRANT ALL PRIVILEGES ON DATABASE sentiment TO airflow;
EOSQL

echo "Additional databases created successfully (druid, superset, openmetadata, sentiment)"
