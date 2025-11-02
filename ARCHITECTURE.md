# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Pipeline Architecture                   │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  Kaggle Dataset  │
                    │ (Ukraine Tweets) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Data Storage   │
                    │  data/raw/*.csv  │
                    └────────┬─────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │      Apache Airflow            │
            │  (Workflow Orchestration)      │
            │                                │
            │  ┌──────────────────────────┐ │
            │  │ twitter_sentiment_dag.py │ │
            │  └──────────────────────────┘ │
            └────────┬───────────────────────┘
                     │
                     ▼
            ┌────────────────────────────────┐
            │      Apache Spark              │
            │  (Data Processing & ML)        │
            │                                │
            │  ┌──────────────────────────┐ │
            │  │  sentiment_analysis.py   │ │
            │  │  - Text Cleaning         │ │
            │  │  - Sentiment Analysis    │ │
            │  │  - HuggingFace Model     │ │
            │  └──────────────────────────┘ │
            └────────┬───────────────────────┘
                     │
                     ▼
            ┌────────────────────────────────┐
            │    Processed Results           │
            │  data/processed/*.csv          │
            └────────┬───────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌───────────┐        ┌──────────────┐
    │PostgreSQL │        │ Apache Druid │
    │ Metadata  │        │   (OLAP)     │
    └─────┬─────┘        └──────┬───────┘
          │                     │
          │                     ▼
          │              ┌──────────────┐
          │              │   Superset   │
          │              │(Visualization)│
          │              └──────────────┘
          │
          ▼
    ┌───────────────┐
    │ OpenMetadata  │
    │  (Governance) │
    └───────────────┘
```

## Component Details

### 1. Data Ingestion Layer

-   **Source**: Kaggle Ukraine-Russia Crisis Twitter Dataset
-   **Format**: CSV (1.2M rows)
-   **Storage**: Local filesystem mounted to containers

### 2. Orchestration Layer

-   **Apache Airflow**
    -   Webserver: Port 8080
    -   Scheduler: Background process
    -   Executor: LocalExecutor
    -   Backend: PostgreSQL

### 3. Processing Layer

-   **Apache Spark**
    -   Master Node: Port 8081
    -   Worker Node(s): Configurable
    -   Processing: Distributed sentiment analysis
    -   ML Model: Hugging Face Transformers

### 4. Storage Layer

-   **PostgreSQL**

    -   Port: 5432
    -   Databases: airflow, druid, superset, openmetadata
    -   Purpose: Metadata storage

-   **Apache Druid**
    -   Router: Port 8888
    -   Broker: Port 8083
    -   Coordinator: Port 8082
    -   Historical: Port 8084
    -   Purpose: Fast OLAP queries

### 5. Visualization Layer

-   **Apache Superset**
    -   Port: 8088
    -   Connected to: Druid, PostgreSQL
    -   Dashboards: Pre-configured sentiment charts

### 6. Governance Layer

-   **OpenMetadata**
    -   Port: 8585
    -   Elasticsearch: Port 9200
    -   Purpose: Data lineage, quality, governance

## Data Flow

1. **Ingestion**: CSV file placed in `data/raw/`
2. **Orchestration**: Airflow DAG triggers pipeline
3. **Processing**: Spark reads CSV, cleans text, analyzes sentiment
4. **Storage**: Results saved to `data/processed/`
5. **Analytics**: Druid ingests processed data
6. **Visualization**: Superset queries Druid for dashboards
7. **Governance**: OpenMetadata tracks lineage across all components

## Network Architecture

All services communicate via Docker bridge network: `sentiment-network`

```
sentiment-network (172.18.0.0/16)
├── postgres (172.18.0.2)
├── airflow-webserver (172.18.0.3)
├── airflow-scheduler (172.18.0.4)
├── spark-master (172.18.0.5)
├── spark-worker (172.18.0.6)
├── druid-zookeeper (172.18.0.7)
├── druid-coordinator (172.18.0.8)
├── druid-broker (172.18.0.9)
├── druid-historical (172.18.0.10)
├── druid-router (172.18.0.11)
├── superset (172.18.0.12)
├── openmetadata (172.18.0.13)
└── elasticsearch (172.18.0.14)
```

## Volume Mounts

-   `./data` → `/opt/airflow/data`, `/opt/spark-data`, `/opt/druid/data`
-   `./airflow/dags` → `/opt/airflow/dags`
-   `./spark` → `/opt/spark-apps`
-   Named volumes for persistent data

## Security Considerations

⚠️ **Note**: This is a local development setup. For production:

1. Change all default passwords
2. Enable SSL/TLS for all services
3. Implement proper authentication
4. Use secrets management (Vault, AWS Secrets Manager)
5. Enable network policies
6. Scan images for vulnerabilities
7. Implement RBAC
8. Enable audit logging

## Scalability

To scale horizontally:

1. Add more Spark workers in `docker-compose.yml`
2. Increase Druid historical nodes
3. Use external databases (RDS, Cloud SQL)
4. Deploy to Kubernetes with Helm charts
5. Use distributed filesystems (HDFS, S3)

## High Availability

For production HA:

1. Run multiple Airflow schedulers
2. Use CeleryExecutor with Redis
3. Deploy Druid with multiple replicas
4. Use managed databases
5. Implement load balancers
6. Set up monitoring with Prometheus/Grafana
