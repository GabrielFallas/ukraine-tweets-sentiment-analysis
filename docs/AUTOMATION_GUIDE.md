# Pipeline Automation Guide

## 🎯 Overview

The Ukraine Tweets Sentiment Analysis pipeline is now **fully automated** from data ingestion to visualization. Once triggered, the pipeline requires no manual intervention.

## ✅ Automated Components

### 1. **Data Processing Pipeline** (Tasks 1-5)

-   ✅ Data validation
-   ✅ Directory creation
-   ✅ Database schema setup
-   ✅ Spark sentiment analysis
-   ✅ Output validation

### 2. **PostgreSQL Loading** (Task 6) 🆕

-   ✅ Automatic CSV to PostgreSQL loading
-   ✅ Data type conversion
-   ✅ Index creation
-   ✅ Sentiment distribution summary

### 3. **Druid Ingestion** (Tasks 7-8)

-   ✅ Automatic ingestion spec generation
-   ✅ Task submission to Druid
-   ✅ Real-time analytics data loading

### 4. **Superset Setup** (Tasks 9-10) 🆕

-   ✅ Automatic database connection configuration
-   ✅ Dataset creation
-   ✅ Chart generation (3 charts):
    -   Sentiment Distribution (Pie Chart)
    -   Sentiment Over Time (Line Chart)
    -   Top Locations (Bar Chart)
-   ✅ Dashboard assembly

### 5. **Metadata & Notifications** (Tasks 11-12)

-   ✅ Pipeline execution logging
-   ✅ Success notifications

---

## 📊 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AIRFLOW ORCHESTRATION                       │
│                         (12 Tasks)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼───────┐       ┌──────▼──────┐
            │  DATA CHECK   │       │   SETUP     │
            │  & VALIDATION │       │  METADATA   │
            └───────┬───────┘       └──────┬──────┘
                    └───────────┬───────────┘
                                │
                    ┌───────────▼────────────┐
                    │  SPARK PROCESSING      │
                    │  (Sentiment Analysis)  │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  OUTPUT VALIDATION     │
                    └───────────┬────────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
        ┌───────▼────────┐            ┌─────────▼────────┐
        │   POSTGRESQL   │            │   DRUID SETUP    │
        │   DATA LOAD    │            │   & INGESTION    │
        └───────┬────────┘            └─────────┬────────┘
                │                               │
        ┌───────▼────────┐                     │
        │  SUPERSET DB   │                     │
        │  CONNECTION    │                     │
        └───────┬────────┘                     │
                │                               │
        ┌───────▼────────┐                     │
        │  DASHBOARD     │                     │
        │  CREATION      │                     │
        └───────┬────────┘                     │
                └───────────────┬───────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  METADATA LOGGING      │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  SUCCESS NOTIFICATION  │
                    └────────────────────────┘
```

---

## 🚀 Running the Pipeline

### Option 1: Manual Trigger (Current Setup)

```bash
# Access Airflow UI
http://localhost:8080

# Login: admin / admin
# Find DAG: twitter_sentiment_pipeline
# Click: Trigger DAG (play button)
```

### Option 2: Enable Automatic Scheduling

Edit `airflow/dags/twitter_sentiment_dag.py` line 240:

```python
# Change from:
schedule_interval=None,  # Manual trigger only

# To (for daily runs):
schedule_interval='@daily',  # Runs every day at midnight

# Or (for hourly):
schedule_interval='@hourly',  # Runs every hour
```

---

## 📋 Task Execution Order

| Task # | Task Name                      | Duration (approx) | Description                          |
| ------ | ------------------------------ | ----------------- | ------------------------------------ |
| 1      | `check_data`                   | 2s                | Validates CSV file exists            |
| 2      | `create_output_dir`            | 1s                | Creates output directories           |
| 3      | `create_metadata_table`        | 2s                | Sets up PostgreSQL metadata table    |
| 4      | `run_spark_sentiment_analysis` | 20-30s            | Runs DistilBERT sentiment analysis   |
| 5      | `validate_output`              | 2s                | Verifies output files exist          |
| 6      | `load_to_postgres`             | 5-10s             | **NEW** Loads results to PostgreSQL  |
| 7      | `prepare_druid_spec`           | 1s                | Generates Druid ingestion spec       |
| 8      | `submit_to_druid`              | 3-5s              | Submits ingestion task to Druid      |
| 9      | `setup_superset_connection`    | 5s                | **NEW** Configures Superset database |
| 10     | `create_superset_dashboard`    | 10-15s            | **NEW** Creates charts & dashboard   |
| 11     | `log_metadata`                 | 2s                | Logs execution metadata              |
| 12     | `success_notification`         | 1s                | Logs completion                      |

**Total Execution Time**: ~60-90 seconds for 100-row sample

---

## 🔍 Monitoring Pipeline Execution

### 1. Airflow UI

```
URL: http://localhost:8080
Login: admin / admin

Features:
- Real-time task status
- Logs for each task
- Execution history
- DAG graph visualization
```

### 2. Task Logs

Each task generates detailed logs accessible via:

-   Airflow UI → DAG Runs → Click task → View Log
-   Container logs: `docker logs sentiment-airflow-scheduler`

### 3. XCom Variables

Tasks share data through XCom:

-   `postgres_row_count`: Number of rows loaded
-   `sentiment_distribution`: Sentiment breakdown
-   `superset_db_id`: Database ID in Superset
-   `dashboard_id`: Created dashboard ID
-   `dashboard_url`: Direct dashboard link

---

## 📈 Accessing Results

### PostgreSQL Data

```bash
# Connect to database
docker exec -it sentiment-postgres psql -U airflow

# Query results
SELECT sentiment, COUNT(*)
FROM ukraine_tweets_sentiment
GROUP BY sentiment;
```

### Druid Data

```bash
# Query via API
curl -X POST http://localhost:8083/druid/v2/sql \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT COUNT(*) FROM ukraine_tweets_sentiment"}'
```

### Superset Dashboard

```
URL: http://localhost:8088
Login: admin / admin

Navigate to: Dashboards → "Ukraine Tweets Sentiment Analysis"
```

---

## 🛠️ Customization Options

### Modify Charts

Edit `twitter_sentiment_dag.py` function `create_superset_dashboard()`:

```python
charts_config = [
    {
        "slice_name": "Your Chart Name",
        "viz_type": "pie",  # pie, bar, line, table, etc.
        "params": json.dumps({
            # Chart-specific parameters
        })
    }
]
```

### Add More Tasks

Insert new tasks before DAG dependencies section:

```python
custom_task = PythonOperator(
    task_id='custom_task_name',
    python_callable=your_function,
    provide_context=True,
)

# Add to dependency chain
validate_output_task >> custom_task >> load_postgres_task
```

### Change Processing Frequency

```python
# In DAG definition (line 240)
schedule_interval='@daily',     # Daily at midnight
schedule_interval='@hourly',    # Every hour
schedule_interval='0 */4 * * *', # Every 4 hours
schedule_interval='@weekly',    # Every Monday
```

---

## ⚠️ Troubleshooting

### Task Failure: `load_to_postgres`

**Symptom**: Task fails with "File not found"
**Solution**: Ensure Spark task completed successfully and CSV exists

```bash
# Check if file exists
docker exec sentiment-airflow-scheduler ls -la /opt/airflow/data/processed/sentiment_results/
```

### Task Failure: `setup_superset_connection`

**Symptom**: "Failed to authenticate with Superset"
**Solution**: Verify Superset is running and accessible

```bash
# Check Superset status
docker ps | grep superset

# Test Superset API
curl http://localhost:8088/api/v1/security/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin","provider":"db","refresh":true}'
```

### Task Failure: `create_superset_dashboard`

**Symptom**: "Dataset creation failed"
**Solution**: Verify PostgreSQL data was loaded

```bash
# Verify PostgreSQL table exists
docker exec -it sentiment-postgres psql -U airflow -c "\dt"
docker exec -it sentiment-postgres psql -U airflow -c "SELECT COUNT(*) FROM ukraine_tweets_sentiment;"
```

### Dashboard Not Appearing

**Symptom**: Dashboard created but not visible in Superset
**Solution**: Check dashboard URL in task logs

```python
# Get dashboard URL from XCom
Airflow UI → twitter_sentiment_pipeline → create_superset_dashboard → XCom → dashboard_url
```

---

## 📊 Success Indicators

### ✅ All Tasks Green

All 12 tasks show green "success" status in Airflow UI

### ✅ Data Loaded

```sql
-- Should return row count matching CSV
SELECT COUNT(*) FROM ukraine_tweets_sentiment;

-- Should show sentiment distribution
SELECT sentiment, COUNT(*)
FROM ukraine_tweets_sentiment
GROUP BY sentiment;
```

### ✅ Dashboard Visible

Navigate to Superset → Dashboards → "Ukraine Tweets Sentiment Analysis"

-   3 charts displayed
-   Data populating charts
-   No error messages

### ✅ Logs Show Success

```
airflow-scheduler logs:
✓ Successfully loaded {N} rows to PostgreSQL
✓ Superset database connection configured successfully
✓ Created dataset with ID: {id}
✓ Created chart 'Sentiment Distribution' with ID: {id}
✓ Created dashboard with ID: {id}
✓ Dashboard URL: http://superset:8088/superset/dashboard/{id}/
```

---

## 🎓 Key Improvements

### Before Automation

❌ Run `load_to_postgres_sqlalchemy.py` manually
❌ Open Superset UI, configure database connection
❌ Manually create dataset
❌ Manually create 3+ charts
❌ Manually create dashboard
❌ Manually arrange charts
⏱️ **Total manual effort**: ~15-20 minutes

### After Automation

✅ Trigger DAG once
✅ Wait ~60-90 seconds
✅ View complete dashboard
⏱️ **Total manual effort**: ~10 seconds (click trigger button)

**Time Saved**: 98% reduction in manual work!

---

## 🔐 Security Notes

### Default Credentials

**⚠️ Change these in production!**

```python
# Superset (in DAG)
username = "admin"
password = "admin"

# PostgreSQL (from Airflow connection)
postgres_conn_id='postgres_default'
# Connection: postgresql://airflow:airflow@sentiment-postgres:5432/airflow
```

### Production Recommendations

1. Use Airflow Variables for credentials
2. Enable SSL/TLS for database connections
3. Use secrets backend (AWS Secrets Manager, HashiCorp Vault)
4. Implement authentication/authorization

```python
# Example: Use Airflow Variables
from airflow.models import Variable

superset_user = Variable.get("SUPERSET_USERNAME")
superset_pass = Variable.get("SUPERSET_PASSWORD")
```

---

## 📝 Summary

The pipeline is now **100% automated**:

-   ✅ **Data Processing**: Spark sentiment analysis
-   ✅ **PostgreSQL**: Automatic data loading with indexes
-   ✅ **Druid**: Automatic ingestion for real-time analytics
-   ✅ **Superset**: Automatic database setup, dataset creation, chart building, and dashboard assembly

**No manual steps required after triggering the DAG!** 🎉

---

## 📚 Related Documentation

-   [QUICKSTART.md](QUICKSTART.md) - Getting started guide
-   [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
-   [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
-   [SUPERSET_CONNECTION_GUIDE.md](SUPERSET_CONNECTION_GUIDE.md) - Superset details
