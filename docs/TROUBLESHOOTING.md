# Troubleshooting Guide

## Common Issues and Solutions

### 1. Services Won't Start

#### Problem: Docker containers fail to start

```bash
Error: Cannot start service ...
```

**Solutions:**

1. Check Docker is running:

    ```bash
    docker ps
    ```

2. Check available resources:

    - Windows: Docker Desktop → Settings → Resources
    - Increase memory to at least 8GB
    - Increase CPUs to at least 4

3. Check port conflicts:

    ```bash
    # Windows
    netstat -ano | findstr :8080

    # Linux/Mac
    lsof -i :8080
    ```

4. Clean up and restart:
    ```bash
    docker-compose down -v
    docker system prune -a
    docker-compose up -d
    ```

### 2. Airflow Issues

#### Problem: Airflow webserver returns 500 error

**Solution:**

```bash
# Check Fernet key is set in .env
# Recreate Airflow database
docker-compose down
docker volume rm ukraine-tweets-sentiment-analysis_airflow-data
docker-compose up -d
```

#### Problem: DAG not appearing in Airflow UI

**Solution:**

```bash
# Check DAG syntax
docker exec -it sentiment-airflow-webserver airflow dags list

# Check for errors
docker exec -it sentiment-airflow-webserver airflow dags list-import-errors

# Restart scheduler
docker-compose restart airflow-scheduler
```

#### Problem: Task stuck in "running" state

**Solution:**

```bash
# Clear task state
docker exec -it sentiment-airflow-webserver \
  airflow tasks clear twitter_sentiment_pipeline -t <task_id>

# Or restart scheduler
docker-compose restart airflow-scheduler
```

### 3. Spark Issues

#### Problem: Spark submit fails with "Connection refused"

**Solution:**

```bash
# Check Spark master is running
curl http://localhost:8081

# Check Spark master URL in Airflow
docker exec -it sentiment-airflow-webserver env | grep SPARK

# Verify network connectivity
docker exec -it sentiment-airflow-webserver ping spark-master
```

#### Problem: Spark job fails with OutOfMemoryError

**Solution:**

1. Increase Spark memory in `docker-compose.yml`:

    ```yaml
    spark-worker:
        environment:
            SPARK_WORKER_MEMORY: 8G
    ```

2. Modify Spark config in DAG:

    ```python
    conf={
        'spark.driver.memory': '8g',
        'spark.executor.memory': '8g',
    }
    ```

3. Process data in smaller chunks:
    ```python
    # In sentiment_analysis.py
    df.limit(100000)  # Process subset first
    ```

#### Problem: Hugging Face model download fails

**Solution:**

```bash
# Pre-download model
docker exec -it sentiment-spark-master bash
python -c "from transformers import pipeline; pipeline('sentiment-analysis')"

# Or use cached model
# Mount model cache directory in docker-compose.yml
```

### 4. Druid Issues

#### Problem: Druid services not communicating

**Solution:**

```bash
# Check ZooKeeper is running
docker exec -it sentiment-druid-zookeeper zkServer.sh status

# Restart Druid services in order
docker-compose restart druid-zookeeper
docker-compose restart druid-coordinator
docker-compose restart druid-broker
docker-compose restart druid-historical
docker-compose restart druid-router
```

#### Problem: Data ingestion fails

**Solution:**

1. Check ingestion spec:

    ```bash
    # Verify spec file exists
    docker exec -it sentiment-airflow-webserver \
      cat /opt/airflow/data/druid_ingestion_spec.json
    ```

2. Check Druid coordinator logs:

    ```bash
    docker-compose logs druid-coordinator
    ```

3. Verify data path:

    ```bash
    # Check processed data exists
    docker exec -it druid-coordinator \
      ls -la /opt/druid/data/processed/sentiment_results/
    ```

4. Manual ingestion test:
    ```bash
    curl -X POST http://localhost:8081/druid/indexer/v1/task \
      -H 'Content-Type: application/json' \
      -d @data/druid_ingestion_spec.json
    ```

#### Problem: Druid queries return no data

**Solution:**

```bash
# Check datasource exists
curl http://localhost:8888/druid/v2/datasources

# Query manually
curl -X POST 'http://localhost:8888/druid/v2/sql' \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT * FROM ukraine_tweets_sentiment LIMIT 10"}'
```

### 5. Superset Issues

#### Problem: Cannot connect to Druid

**Solution:**

1. Check Druid connection string:

    ```
    druid://druid-broker:8082/druid/v2/sql/
    ```

2. Test from Superset container:

    ```bash
    docker exec -it sentiment-superset bash
    curl http://druid-broker:8082/status
    ```

3. Recreate database connection in Superset UI

#### Problem: Charts not loading

**Solution:**

```bash
# Check Superset logs
docker-compose logs superset

# Clear Superset cache
docker exec -it sentiment-superset superset cache-clear

# Restart Superset
docker-compose restart superset
```

#### Problem: Login fails

**Solution:**

```bash
# Reset admin password
docker exec -it sentiment-superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@superset.com \
  --password admin
```

### 6. OpenMetadata Issues

#### Problem: OpenMetadata UI not loading

**Solution:**

```bash
# Check Elasticsearch is running
curl http://localhost:9200/_cluster/health

# Check OpenMetadata logs
docker-compose logs openmetadata

# Restart services
docker-compose restart openmetadata-elasticsearch
docker-compose restart openmetadata
```

#### Problem: Cannot add service connections

**Solution:**

1. Wait 2-3 minutes for full initialization
2. Verify services are accessible from OpenMetadata:
    ```bash
    docker exec -it sentiment-openmetadata curl http://airflow-webserver:8080/health
    ```

### 7. PostgreSQL Issues

#### Problem: Database connection refused

**Solution:**

```bash
# Check PostgreSQL is running
docker exec -it sentiment-postgres pg_isready -U airflow

# Check databases exist
docker exec -it sentiment-postgres psql -U airflow -c "\l"

# Create missing databases
docker exec -it sentiment-postgres psql -U airflow -c "CREATE DATABASE druid;"
```

#### Problem: Too many connections

**Solution:**

```bash
# Check active connections
docker exec -it sentiment-postgres psql -U airflow -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Restart services that connect to PostgreSQL
docker-compose restart airflow-webserver airflow-scheduler
```

### 8. Data Issues

#### Problem: Input CSV not found

**Solution:**

```bash
# Verify file exists
ls -la data/raw/ukraine_tweets.csv

# Check file is accessible in container
docker exec -it sentiment-airflow-webserver \
  ls -la /opt/airflow/data/raw/

# Verify mount in docker-compose.yml
```

#### Problem: Sentiment analysis produces all NEUTRAL

**Solution:**

1. Check model is loaded:

    ```python
    # In sentiment_analysis.py
    logger.info(f"Model: {self.model_name}")
    ```

2. Verify text cleaning isn't too aggressive
3. Check for non-English tweets (model is English-only)

#### Problem: Processing is very slow

**Solution:**

1. Reduce dataset size for testing:

    ```python
    df = df.limit(10000)  # Test with subset
    ```

2. Increase batch size:

    ```python
    batch_size = 500  # from 100
    ```

3. Add more Spark workers

### 9. Network Issues

#### Problem: Services can't communicate

**Solution:**

```bash
# Check network exists
docker network ls | grep sentiment

# Inspect network
docker network inspect ukraine-tweets-sentiment-analysis_sentiment-network

# Reconnect service to network
docker network connect sentiment-network sentiment-airflow-webserver
```

### 10. Volume Issues

#### Problem: Changes not reflected in container

**Solution:**

```bash
# Restart container
docker-compose restart <service-name>

# Force recreate
docker-compose up -d --force-recreate <service-name>

# Check mount
docker inspect sentiment-airflow-webserver | grep Mounts -A 20
```

## Debugging Commands

### Check Service Health

```bash
# All services status
docker-compose ps

# Resource usage
docker stats

# Service logs
docker-compose logs -f <service-name>

# Last 100 lines of logs
docker-compose logs --tail=100 <service-name>
```

### Access Containers

```bash
# Airflow
docker exec -it sentiment-airflow-webserver bash

# Spark
docker exec -it sentiment-spark-master bash

# PostgreSQL
docker exec -it sentiment-postgres psql -U airflow -d airflow

# Druid
docker exec -it druid-broker bash
```

### Check Connectivity

```bash
# From Airflow to Spark
docker exec -it sentiment-airflow-webserver curl http://spark-master:8080

# From Airflow to Druid
docker exec -it sentiment-airflow-webserver curl http://druid-router:8888/status

# From Superset to Druid
docker exec -it sentiment-superset curl http://druid-broker:8082/status
```

### Reset Everything

```bash
# Nuclear option - complete reset
docker-compose down -v
docker system prune -a -f
rm -rf airflow/logs/*
rm -rf data/processed/*

# Restart from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Performance Optimization

### Speed up Spark Processing

1. Increase parallelism:

    ```python
    df.repartition(20)
    ```

2. Cache frequently used DataFrames:

    ```python
    df_cleaned.cache()
    ```

3. Use more efficient serialization:
    ```python
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    ```

### Optimize Druid Queries

1. Tune segment granularity
2. Add indexes on frequently queried columns
3. Use aggregations at ingestion time

### Speed up Airflow

1. Increase parallelism:

    ```python
    default_args = {
        'max_active_runs': 3,
        'max_active_tasks': 5
    }
    ```

2. Use connection pooling
3. Optimize task scheduling

## Getting Help

1. Check logs first: `docker-compose logs <service>`
2. Search GitHub issues
3. Consult official documentation
4. Open a new issue with:
    - Error message
    - Relevant logs
    - Steps to reproduce
    - Environment details (OS, Docker version)

## Useful Links

-   [Docker Documentation](https://docs.docker.com/)
-   [Airflow Documentation](https://airflow.apache.org/docs/)
-   [Spark Documentation](https://spark.apache.org/docs/latest/)
-   [Druid Documentation](https://druid.apache.org/docs/latest/)
-   [Superset Documentation](https://superset.apache.org/docs/intro)
