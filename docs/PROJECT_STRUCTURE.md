# Project File Structure

```
ukraine-tweets-sentiment-analysis/
│
├── README.md                           # Main documentation
├── ARCHITECTURE.md                     # System architecture details
├── TROUBLESHOOTING.md                  # Common issues and solutions
├── docker-compose.yml                  # Main Docker orchestration file
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore patterns
├── Makefile                           # Build and management commands
├── setup.sh                           # Setup script for Linux/Mac
├── setup.bat                          # Setup script for Windows
│
├── airflow/                           # Apache Airflow configuration
│   ├── Dockerfile                     # Airflow custom image
│   ├── requirements.txt               # Python dependencies
│   ├── dags/                          # Airflow DAGs
│   │   └── twitter_sentiment_dag.py   # Main pipeline DAG
│   ├── logs/                          # Airflow logs (generated)
│   │   └── .gitkeep
│   └── plugins/                       # Airflow plugins
│       └── .gitkeep
│
├── spark/                             # Apache Spark configuration
│   ├── Dockerfile                     # Spark custom image
│   ├── requirements.txt               # Python dependencies
│   └── sentiment_analysis.py          # Main Spark processing script
│
├── superset/                          # Apache Superset configuration
│   ├── Dockerfile                     # Superset custom image
│   ├── init_superset.sh              # Initialization script
│   ├── create_dashboard.py           # Dashboard automation script
│   └── dashboards/                    # Dashboard exports
│       └── .gitkeep
│
├── openmetadata/                      # OpenMetadata configuration
│   ├── config.py                      # Connector configurations
│   └── init_openmetadata.sh          # Initialization script
│
├── scripts/                           # Utility scripts
│   └── init-databases.sh             # PostgreSQL initialization
│
└── data/                              # Data directory (mounted)
    ├── raw/                           # Raw input data
    │   ├── .gitkeep
    │   └── ukraine_tweets.csv         # [Download from Kaggle]
    └── processed/                     # Processed output data
        └── .gitkeep

Docker Volumes (created automatically):
├── postgres-data/                     # PostgreSQL data
├── airflow-data/                      # Airflow data
├── spark-master-data/                 # Spark master data
├── spark-worker-data/                 # Spark worker data
├── druid-coordinator-data/            # Druid coordinator data
├── druid-broker-data/                 # Druid broker data
├── druid-historical-data/             # Druid historical data
├── druid-router-data/                 # Druid router data
├── zookeeper-data/                    # ZooKeeper data
├── zookeeper-datalog/                 # ZooKeeper logs
├── superset-data/                     # Superset data
├── openmetadata-data/                 # OpenMetadata data
└── elasticsearch-data/                # Elasticsearch data
```

## File Descriptions

### Root Files

-   **README.md**: Complete setup guide, usage instructions, and project overview
-   **ARCHITECTURE.md**: Detailed system architecture and component descriptions
-   **TROUBLESHOOTING.md**: Common issues and debugging solutions
-   **docker-compose.yml**: Docker Compose configuration for all services
-   **.env.example**: Template for environment variables
-   **.gitignore**: Files and directories to exclude from Git
-   **Makefile**: Convenient commands for managing the project
-   **setup.sh/bat**: Automated setup scripts

### Airflow Directory

-   **Dockerfile**: Custom Airflow image with Spark support
-   **requirements.txt**: Python packages for Airflow
-   **twitter_sentiment_dag.py**: Main DAG orchestrating the pipeline

### Spark Directory

-   **Dockerfile**: Custom Spark image with ML libraries
-   **requirements.txt**: Python packages including Transformers
-   **sentiment_analysis.py**: Data processing and sentiment analysis logic

### Superset Directory

-   **Dockerfile**: Custom Superset image with Druid support
-   **init_superset.sh**: Bash script for initial setup
-   **create_dashboard.py**: Python script to create dashboards automatically

### OpenMetadata Directory

-   **config.py**: Configuration for various data source connectors
-   **init_openmetadata.sh**: Setup script for metadata tracking

### Scripts Directory

-   **init-databases.sh**: Creates additional PostgreSQL databases

### Data Directory

-   **raw/**: Place downloaded CSV files here
-   **processed/**: Spark outputs results here

## Services and Ports

| Service           | Port | Purpose                 |
| ----------------- | ---- | ----------------------- |
| PostgreSQL        | 5432 | Metadata storage        |
| Airflow Webserver | 8080 | Workflow UI             |
| Spark Master UI   | 8081 | Spark monitoring        |
| Druid Coordinator | 8082 | Druid management        |
| Druid Broker      | 8083 | Druid queries           |
| Druid Historical  | 8084 | Historical data         |
| Superset          | 8088 | Visualization           |
| Druid Router      | 8888 | Druid API gateway       |
| Elasticsearch     | 9200 | Search for OpenMetadata |
| OpenMetadata      | 8585 | Governance UI           |
| ZooKeeper         | 2181 | Coordination            |

## Key Components

### 1. Orchestration (Airflow)

-   Schedules and monitors the pipeline
-   Manages task dependencies
-   Provides execution logs

### 2. Processing (Spark)

-   Loads and cleans tweet data
-   Performs sentiment analysis using Hugging Face models
-   Outputs processed results

### 3. Storage (PostgreSQL + Druid)

-   PostgreSQL: Stores pipeline metadata
-   Druid: Fast OLAP analytics on processed data

### 4. Visualization (Superset)

-   Creates interactive dashboards
-   Connects to Druid for fast queries
-   Pre-configured sentiment charts

### 5. Governance (OpenMetadata)

-   Tracks data lineage
-   Documents data assets
-   Monitors data quality

## Data Flow

1. **Input**: CSV file in `data/raw/`
2. **Trigger**: Airflow DAG runs (scheduled or manual)
3. **Process**: Spark analyzes sentiment
4. **Output**: Results saved to `data/processed/`
5. **Ingest**: Druid loads processed data
6. **Visualize**: Superset displays dashboards
7. **Track**: OpenMetadata records lineage

## Getting Started

1. Run setup script: `./setup.sh` or `setup.bat`
2. Download dataset to `data/raw/ukraine_tweets.csv`
3. Edit `.env` with required keys
4. Build images: `docker-compose build`
5. Start services: `docker-compose up -d`
6. Access Airflow: http://localhost:8080
7. Trigger the DAG
8. View results in Superset: http://localhost:8088

## Notes

-   All services run in Docker containers
-   Data is persisted in named volumes
-   Configuration is externalized via environment variables
-   Services communicate via Docker network
-   Logs are available via `docker-compose logs`

For detailed instructions, see README.md
For troubleshooting, see TROUBLESHOOTING.md
For architecture details, see ARCHITECTURE.md
