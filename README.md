# 🇺🇦 Ukraine Tweets Sentiment Analysis Pipeline

A complete end-to-end data pipeline for sentiment analysis of Ukraine-related tweets using Apache Airflow, Spark, PostgreSQL, Druid, and Superset.

## 📁 Project Structure

```
ukraine-tweets-sentiment-analysis/
├── 📂 airflow/                    # Airflow configuration and DAGs
│   ├── dags/                      # DAG definitions
│   ├── logs/                      # Airflow execution logs
│   ├── plugins/                   # Custom Airflow plugins
│   ├── Dockerfile                 # Airflow container image
│   └── requirements.txt           # Python dependencies
│
├── 📂 spark/                      # Spark job definitions
│   ├── sentiment_analysis.py     # Main sentiment analysis job
│   ├── Dockerfile                 # Spark container image
│   └── requirements.txt           # Spark dependencies
│
├── 📂 superset/                   # Apache Superset configuration
│   ├── dashboards/                # Dashboard definitions
│   ├── create_dashboard.py       # Dashboard setup script
│   ├── init_superset.sh          # Initialization script
│   └── Dockerfile                 # Superset container image
│
├── 📂 openmetadata/               # OpenMetadata integration
│   ├── config.py                  # Configuration
│   └── init_openmetadata.sh      # Setup script
│
├── 📂 scripts/                    # Setup and utility scripts
│   ├── init-databases.sh         # Database initialization
│   ├── setup_airflow_connections.sh   # Airflow connections
│   ├── setup_airflow_connections.bat  # Windows setup
│   └── query_druid.sh            # Druid query utility
│
├── 📂 data/                       # Data storage
│   ├── raw/                       # Raw tweet data
│   │   ├── ukraine_tweets.csv    # Full dataset
│   │   └── ukraine_tweets_sample_100.csv  # Test sample
│   ├── processed/                 # Processed results
│   │   └── sentiment_results/    # Analysis output
│   └── druid_ingestion_spec.json # Druid ingestion config
│
├── 📂 tools/                      # Utility tools
│   ├── 📂 data_preparation/       # Data sampling and preparation
│   │   ├── create_sample_100.py   # Create 100-row sample
│   │   ├── create_sample_dataset.py # Create larger samples
│   │   ├── create_mock_data.py    # Generate mock data
│   │   └── download_dataset.py    # Download from source
│   │
│   ├── 📂 database_loaders/       # Database loading scripts
│   │   ├── load_to_postgres_sqlalchemy.py  # ✅ Main loader (recommended)
│   │   ├── load_to_postgres_direct.py      # Direct psycopg2 method
│   │   ├── load_to_postgres_fixed.py       # Alternative method
│   │   ├── load_to_postgres_simple.py      # Simple COPY method
│   │   └── load_results_to_postgres.py     # Legacy loader
│   │
│   └── 📂 diagnostics/            # Monitoring and debugging
│       ├── verify_postgres.py     # Check PostgreSQL data
│       ├── check_druid_data.py    # Check Druid data
│       ├── diagnose_druid_connection.py  # Druid diagnostics
│       ├── view_results.py        # View analysis results
│       └── monitor_pipeline.py    # Pipeline monitoring
│
├── 📂 docs/                       # Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── PROJECT_STRUCTURE.md       # Project organization
│   ├── QUICKSTART.md             # Quick start guide
│   ├── TROUBLESHOOTING.md        # Common issues and fixes
│   ├── SUPERSET_CONNECTION_GUIDE.md  # Superset setup (⭐ Start here!)
│   ├── SUPERSET_SETUP.md         # Detailed Superset guide
│   ├── CONNECT_SUPERSET_TO_DRUID.md  # Druid connection
│   ├── VISUAL_OVERVIEW.md        # Visual diagrams
│   ├── INDEX.md                  # Documentation index
│   ├── SUMMARY.md                # Project summary
│   └── CHECKLIST.md              # Implementation checklist
│
├── 📂 config/                     # Configuration files
│   └── generate_keys.py          # Generate encryption keys
│
├── 📄 docker-compose.yml          # Docker services definition
├── 📄 Makefile                    # Build and run commands
├── 📄 .env.example                # Example environment config
├── 📄 setup.sh                    # Linux/Mac setup script
├── 📄 SETUP.bat                   # Windows setup script
└── 📄 README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

-   Docker Desktop (Windows/Mac) or Docker Engine (Linux)
-   8GB+ RAM available for Docker
-   10GB+ disk space
-   Python 3.11+ (optional, for data preparation)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis

# Copy environment template
cp .env.example .env
```

### Step 2: Download Dataset

**Option A: Full Dataset (1.2M rows, 44GB)**

1. Go to [Kaggle Dataset](https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows)
2. Download CSV and place in `data/raw/ukraine_tweets.csv`

**Option B: Quick Test (100 rows) - Recommended for first run**

```bash
python tools/data_preparation/create_sample_100.py
```

### Step 3: Start Services

**Linux/Mac:**

```bash
./setup.sh
docker-compose up -d
```

**Windows:**

```powershell
.\SETUP.bat
docker-compose up -d
```

Wait 2-3 minutes for all services to initialize.

### Step 4: Run the Pipeline

1. **Access Airflow UI**: http://localhost:8080

    - Username: `airflow`, Password: `airflow`

2. **Enable the DAG**: Find `twitter_sentiment_pipeline` and toggle it on

3. **Trigger the DAG**: Click the play button (▶️) to run manually

4. **Monitor progress**: Pipeline completes in ~30 seconds for 100 rows

### Step 5: Load Results to Database

```bash
# Load results to PostgreSQL
python tools/database_loaders/load_to_postgres_sqlalchemy.py

# Verify data loaded successfully
python tools/diagnostics/verify_postgres.py
```

### Step 6: Visualize in Superset

1. **Open Superset**: http://localhost:8088

    - Username: `admin`, Password: `admin`

2. **Follow the detailed guide**: [`docs/SUPERSET_CONNECTION_GUIDE.md`](docs/SUPERSET_CONNECTION_GUIDE.md)

3. **Quick setup**:

    - Go to: Settings → Database Connections → + Database
    - Select: PostgreSQL
    - URI: `postgresql://airflow:airflow@sentiment-postgres:5432/airflow`
    - Test → Connect

4. Create dataset from table: `ukraine_tweets_sentiment` and build dashboards!

## 🔧 Service URLs

| Service           | URL                   | Credentials       |
| ----------------- | --------------------- | ----------------- |
| **Airflow**       | http://localhost:8080 | airflow / airflow |
| **Spark Master**  | http://localhost:8081 | -                 |
| **Druid Console** | http://localhost:8888 | -                 |
| **Superset**      | http://localhost:8088 | admin / admin     |
| **PostgreSQL**    | localhost:5432        | airflow / airflow |

## 📊 Pipeline Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Raw CSV   │────▶│   Airflow    │────▶│    Spark    │────▶│  PostgreSQL  │
│  (Tweets)   │     │ Orchestrator │     │  Sentiment  │     │   (Results)  │
└─────────────┘     └──────────────┘     │  Analysis   │     └──────────────┘
                                          └─────────────┘             │
                                                                      ▼
                                                              ┌──────────────┐
                                                              │   Superset   │
                                                              │ (Dashboards) │
                                                              └──────────────┘
```

### Pipeline Steps:

1. **Data Ingestion**: Load raw tweet CSV
2. **Preprocessing**: Clean text, remove special characters
3. **Sentiment Analysis**: Spark + DistilBERT model (Hugging Face)
4. **Storage**: Save to PostgreSQL
5. **Visualization**: Create dashboards in Superset

### Tech Stack:

-   **Orchestration**: Apache Airflow 2.x
-   **Processing**: Apache Spark 3.x (Standalone cluster)
-   **ML Model**: DistilBERT (transformers library)
-   **Storage**: PostgreSQL 14, Apache Druid 28
-   **Visualization**: Apache Superset 3.x
-   **Containerization**: Docker Compose

4. **Monitor Progress**: Watch the DAG execution in the Graph view

The pipeline will:

-   ✅ Validate the input dataset
-   ✅ Run Spark sentiment analysis (using Hugging Face Transformers)
-   ✅ Save processed results
-   ✅ Ingest data into Druid
-   ✅ Log metadata to PostgreSQL

### Step 7: Create Superset Dashboards

Once data is in Druid, create visualizations:

```bash
# Run dashboard creation script
docker exec -it sentiment-superset python /app/dashboards/create_dashboard.py
```

Or create manually:

1. Go to http://localhost:8088
2. Login with admin/admin
3. Navigate to Databases → Add Database
4. Select Druid and configure: `druid://druid-broker:8082/druid/v2/sql/`
5. Create charts and dashboards from the `ukraine_tweets_sentiment` datasource

### Step 8: Configure OpenMetadata (Optional)

1. Access OpenMetadata: http://localhost:8585
2. Login with admin/admin
3. Add services (Settings → Services):
    - Airflow Pipeline Service
    - Druid Database Service
    - Superset Dashboard Service
    - PostgreSQL Database Service
4. Run metadata ingestion to track data lineage

## 📁 Project Structure

```
ukraine-tweets-sentiment-analysis/
├── airflow/
│   ├── dags/
│   │   └── twitter_sentiment_dag.py    # Main orchestration DAG
│   ├── Dockerfile
│   └── requirements.txt
├── spark/
│   ├── sentiment_analysis.py           # Spark processing script
│   ├── Dockerfile
│   └── requirements.txt
├── superset/
│   ├── create_dashboard.py             # Dashboard automation
│   ├── init_superset.sh               # Initialization script
│   └── Dockerfile
├── openmetadata/
│   ├── config.py                       # OpenMetadata connectors
│   └── init_openmetadata.sh
├── scripts/
│   └── init-databases.sh              # PostgreSQL setup
├── data/
│   ├── raw/                           # Input CSV files
│   └── processed/                     # Spark output
├── docker-compose.yml                 # Main orchestration file
├── .env.example                       # Environment template
├── .gitignore
└── README.md
```

## 🔧 Pipeline Details

### Spark Sentiment Analysis

The `spark/sentiment_analysis.py` script:

1. **Data Loading**: Reads CSV from Kaggle dataset
2. **Text Cleaning**:
    - Removes URLs, mentions (@user)
    - Strips hashtags (keeps text)
    - Removes special characters
    - Normalizes whitespace
3. **Sentiment Analysis**:
    - Uses Hugging Face `distilbert-base-uncased-finetuned-sst-2-english` model
    - Classifies tweets as POSITIVE, NEGATIVE, or NEUTRAL
    - Processes in batches for efficiency
4. **Output**: Saves CSV with sentiment column

### Airflow DAG

The pipeline DAG (`airflow/dags/twitter_sentiment_dag.py`) includes:

```
check_data → create_output_dir → create_metadata_table
    ↓
spark_sentiment_analysis
    ↓
validate_output
    ↓
prepare_druid_spec
    ↓
submit_to_druid
    ↓
log_metadata
    ↓
success_notification
```

**Schedule**: Daily (`@daily`)

### Druid Ingestion

Data is ingested into Druid with:

-   **Datasource**: `ukraine_tweets_sentiment`
-   **Timestamp**: `tweetcreatedts`
-   **Dimensions**: userid, username, location, text, sentiment, hashtags
-   **Metrics**: count, total_followers, total_retweets
-   **Granularity**: DAY (segments), HOUR (queries)

### Superset Dashboards

Pre-configured visualizations:

1. **Sentiment Over Time** - Line chart showing sentiment trends
2. **Sentiment Distribution** - Pie chart of POSITIVE/NEGATIVE/NEUTRAL
3. **Top Locations** - Bar chart of most active locations
4. **Sentiment by Location** - Heatmap of location vs sentiment

## 🛠️ Development

### Rebuild Services

```bash
# Rebuild specific service
docker-compose build spark-master

# Rebuild all services
docker-compose build
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-webserver
docker-compose logs -f spark-master
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Execute Commands in Containers

```bash
# Spark submit manually
docker exec -it sentiment-spark-master spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark-apps/sentiment_analysis.py \
  /opt/spark-data/raw/ukraine_tweets.csv \
  /opt/spark-data/processed/sentiment_results

# Access PostgreSQL
docker exec -it sentiment-postgres psql -U airflow -d airflow

# Access Airflow CLI
docker exec -it sentiment-airflow-webserver airflow dags list
```

## 🔍 Monitoring

### Check Service Health

```bash
# Check running containers
docker ps

# Check resource usage
docker stats

# Check Airflow scheduler health
curl http://localhost:8080/health

# Check Spark master status
curl http://localhost:8081
```

### Common Issues

**Issue**: Airflow webserver won't start

-   **Solution**: Check Fernet key is set in `.env`

**Issue**: Spark job fails with memory error

-   **Solution**: Increase Docker Desktop memory limit to 8GB+

**Issue**: Druid ingestion fails

-   **Solution**: Ensure data directory is mounted correctly in docker-compose

**Issue**: Services can't communicate

-   **Solution**: Verify all services are on `sentiment-network`

## 📈 Scaling

### Process Larger Datasets

1. **Add Spark Workers**:

```yaml
# In docker-compose.yml, duplicate spark-worker service
spark-worker-2:
    # ... same config as spark-worker
```

2. **Increase Resources**:

```yaml
spark-worker:
    environment:
        SPARK_WORKER_MEMORY: 8G
        SPARK_WORKER_CORES: 4
```

3. **Partition Data**:

```python
# In sentiment_analysis.py
df.repartition(10).write.csv(output_path)
```

## 🧪 Testing

### Test Spark Script Locally

```bash
docker exec -it sentiment-spark-master bash
cd /opt/spark-apps
python sentiment_analysis.py /opt/spark-data/raw/sample.csv /opt/spark-data/test
```

### Test Druid Query

```bash
curl -X POST 'http://localhost:8888/druid/v2/sql' \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT sentiment, COUNT(*) as count FROM ukraine_tweets_sentiment GROUP BY sentiment"}'
```

## 📚 Additional Resources

-   [Apache Airflow Documentation](https://airflow.apache.org/docs/)
-   [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
-   [Apache Druid Documentation](https://druid.apache.org/docs/latest/design/)
-   [Apache Superset Documentation](https://superset.apache.org/docs/intro)
-   [OpenMetadata Documentation](https://docs.open-metadata.org/)
-   [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

-   Kaggle for the Ukraine-Russia crisis Twitter dataset
-   Hugging Face for sentiment analysis models
-   Apache Software Foundation for open-source tools
-   OpenMetadata community

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Note**: This pipeline processes real Twitter data about a sensitive geopolitical event. Please use responsibly and consider ethical implications when analyzing and sharing sentiment results.
