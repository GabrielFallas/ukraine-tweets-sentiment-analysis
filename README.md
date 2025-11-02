# Ukraine Tweets Sentiment Analysis Pipeline

A complete, containerized data pipeline for sentiment analysis of the Ukraine-Russia crisis Twitter dataset using modern data engineering tools.

## 🏗️ Architecture

This project implements a production-grade data pipeline with the following components:

-   **Docker** - Containerization platform
-   **Apache Airflow** - Workflow orchestration
-   **Apache Spark** - Distributed data processing and sentiment analysis
-   **PostgreSQL** - Metadata and results storage
-   **Apache Druid** - Fast OLAP analytics
-   **Apache Superset** - Data visualization and dashboards
-   **OpenMetadata** - Data governance and lineage tracking

## 📊 Dataset

**Ukraine-Russia Crisis Twitter Dataset (1.2M rows)**

-   Source: [Kaggle Dataset](https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows)
-   Contains tweets related to the Ukraine-Russia crisis
-   Fields: userid, username, location, tweet text, hashtags, timestamps, retweet counts, etc.

## 🚀 Quick Start

### Prerequisites

-   Docker Desktop (Windows/Mac) or Docker Engine (Linux)
-   At least 16GB RAM
-   20GB free disk space
-   Python 3.11+ (for dataset download)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis
```

### Step 2: Download Dataset

1. Go to [Kaggle Dataset Page](https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows)
2. Download the CSV file
3. Place it in `data/raw/ukraine_tweets.csv`

```bash
# Create data directories
mkdir -p data/raw data/processed
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and generate required keys:

```bash
# Generate Fernet key for Airflow
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate Superset secret key (requires openssl)
openssl rand -base64 42
```

Update `.env` with the generated keys:

```env
AIRFLOW_FERNET_KEY=<your_fernet_key>
SUPERSET_SECRET_KEY=<your_secret_key>
```

### Step 4: Build and Start Services

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d
```

This will start:

-   PostgreSQL (port 5432)
-   Airflow Webserver (port 8080)
-   Spark Master UI (port 8081)
-   Druid Router (port 8888)
-   Superset (port 8088)
-   OpenMetadata (port 8585)
-   Elasticsearch (port 9200)
-   ZooKeeper (port 2181)

### Step 5: Access Services

Wait 2-3 minutes for all services to initialize, then access:

| Service      | URL                   | Username | Password |
| ------------ | --------------------- | -------- | -------- |
| Airflow      | http://localhost:8080 | admin    | admin    |
| Spark Master | http://localhost:8081 | -        | -        |
| Druid        | http://localhost:8888 | -        | -        |
| Superset     | http://localhost:8088 | admin    | admin    |
| OpenMetadata | http://localhost:8585 | admin    | admin    |

### Step 6: Run the Pipeline

1. **Access Airflow UI**: http://localhost:8080
2. **Enable the DAG**: Find `twitter_sentiment_pipeline` and toggle it on
3. **Trigger the DAG**: Click the play button to run manually
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
