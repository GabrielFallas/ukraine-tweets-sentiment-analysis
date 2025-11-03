# Quick Start Guide

Get the sentiment analysis pipeline running in under 10 minutes!

## Prerequisites Checklist

-   [ ] Docker Desktop installed and running
-   [ ] At least 16GB RAM available
-   [ ] 20GB free disk space
-   [ ] Internet connection (for downloading images and models)

## Step-by-Step Setup

### 1. Clone or Download (1 minute)

```bash
# If using Git
git clone https://github.com/yourusername/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis

# Or download and extract ZIP
```

### 2. Run Setup Script (1 minute)

**Windows:**

```cmd
setup.bat
```

**Linux/Mac:**

```bash
chmod +x setup.sh
./setup.sh
```

This creates necessary directories and the `.env` file.

### 3. Configure Environment (2 minutes)

Generate required keys:

**Fernet Key for Airflow:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Superset Secret Key:**

```bash
# Windows (PowerShell)
$bytes = New-Object Byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [Convert]::ToBase64String($bytes)

# Linux/Mac
openssl rand -base64 42
```

Edit `.env` file and paste the keys:

```env
AIRFLOW_FERNET_KEY=YOUR_GENERATED_FERNET_KEY
SUPERSET_SECRET_KEY=YOUR_GENERATED_SECRET_KEY
```

### 4. Download Dataset (3 minutes)

1. Go to [Kaggle Dataset](https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows)
2. Click "Download" (requires Kaggle account)
3. Extract the CSV file
4. Rename to `ukraine_tweets.csv`
5. Place in `data/raw/` directory

```bash
# Verify file is in the right place
ls data/raw/ukraine_tweets.csv  # Linux/Mac
dir data\raw\ukraine_tweets.csv  # Windows
```

### 5. Build Docker Images (5-10 minutes)

```bash
docker-compose build
```

☕ Grab a coffee while Docker builds the images!

### 6. Start All Services (2 minutes)

```bash
docker-compose up -d
```

Wait 2-3 minutes for all services to initialize.

### 7. Verify Services (1 minute)

Check all services are running:

```bash
docker-compose ps
```

You should see 14 containers running.

### 8. Access the Services

Open your browser and verify:

✅ **Airflow**: http://localhost:8080 (admin/admin)
✅ **Spark**: http://localhost:8081
✅ **Superset**: http://localhost:8088 (admin/admin)
✅ **Druid**: http://localhost:8888
✅ **OpenMetadata**: http://localhost:8585 (admin/admin)

### 9. Run the Pipeline (1-2 hours depending on dataset size)

1. Go to Airflow: http://localhost:8080
2. Find the DAG: `twitter_sentiment_pipeline`
3. Toggle it ON (click the switch)
4. Click the Play button (▶️) to trigger manually
5. Click the DAG name to view execution
6. Watch the progress in Graph view

The pipeline will:

-   Validate input data ✓
-   Run Spark sentiment analysis (longest step)
-   Validate output ✓
-   Prepare Druid ingestion spec ✓
-   Submit to Druid ✓
-   Log metadata ✓

### 10. View Results

**Option A: Superset Dashboards**

1. Go to http://localhost:8088
2. Login (admin/admin)
3. Click "Databases" → "+" → "Druid"
4. URI: `druid://druid-broker:8082/druid/v2/sql/`
5. Test connection and Save
6. Create charts from `ukraine_tweets_sentiment` dataset

**Option B: Direct Druid Queries**

```bash
curl -X POST 'http://localhost:8888/druid/v2/sql' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "SELECT sentiment, COUNT(*) as count FROM ukraine_tweets_sentiment GROUP BY sentiment"
  }'
```

**Option C: SQL Lab in Superset**

1. Go to Superset → SQL Lab
2. Select Druid database
3. Run queries:
    ```sql
    SELECT * FROM ukraine_tweets_sentiment LIMIT 10;
    SELECT sentiment, COUNT(*) FROM ukraine_tweets_sentiment GROUP BY sentiment;
    ```

## Troubleshooting Quick Fixes

### Services won't start

```bash
# Increase Docker memory to 8GB+
# Docker Desktop → Settings → Resources → Memory
```

### Airflow shows error

```bash
# Check .env has valid Fernet key
docker-compose restart airflow-webserver airflow-scheduler
```

### Spark job fails

```bash
# Check logs
docker-compose logs spark-master

# Verify data file exists
docker exec -it sentiment-airflow-webserver ls /opt/airflow/data/raw/
```

### Port already in use

```bash
# Windows - find process using port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8080 | xargs kill -9
```

### Complete reset

```bash
docker-compose down -v
docker system prune -a
# Then start from Step 5
```

## Next Steps

✅ **Explore Data**: Query Druid for insights
✅ **Create Dashboards**: Build visualizations in Superset
✅ **Schedule**: Set DAG to run daily
✅ **Customize**: Modify sentiment analysis model
✅ **Scale**: Add more Spark workers

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-webserver

# Check service status
docker-compose ps

# Stop all services
docker-compose down

# Restart a service
docker-compose restart <service-name>

# Access container shell
docker exec -it sentiment-airflow-webserver bash
```

## Performance Tips

🚀 **For faster processing:**

1. **Test with subset first:**

    - Edit `spark/sentiment_analysis.py`
    - Add `df = df.limit(10000)` after loading data

2. **Increase resources:**

    - Docker Desktop → Settings → Resources
    - Increase CPUs and Memory

3. **Add more workers:**
    - Edit `docker-compose.yml`
    - Duplicate `spark-worker` service

## Getting Help

📖 **Documentation:**

-   Full guide: `README.md`
-   Architecture: `ARCHITECTURE.md`
-   Issues: `TROUBLESHOOTING.md`

🐛 **Issues:**

-   Check logs: `docker-compose logs <service>`
-   Search GitHub issues
-   Open new issue with logs

## Success Metrics

After completing setup, you should have:

✅ All 14 containers running
✅ Airflow DAG executed successfully
✅ Processed data in `data/processed/`
✅ Data visible in Druid queries
✅ Dashboards displaying sentiment analysis

**Congratulations! Your sentiment analysis pipeline is running!** 🎉

---

**Estimated Total Time:** 15-30 minutes (excluding pipeline execution time)

**Dataset Processing Time:** 1-2 hours for full 1.2M rows (depends on hardware)

**Recommended:** Test with a subset first (10,000-100,000 rows) before processing the full dataset.
