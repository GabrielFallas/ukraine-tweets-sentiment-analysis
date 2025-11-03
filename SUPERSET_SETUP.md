# Connecting Superset to Your Sentiment Analysis Data

## Access Superset

1. Open your browser and go to: **http://localhost:8088**
2. Login with default credentials:
    - Username: `admin`
    - Password: `admin`

## Option 1: Connect to PostgreSQL (Recommended - Has Metadata)

PostgreSQL stores the pipeline metadata and you can also load the CSV results there.

### Step 1: Add PostgreSQL Database Connection

1. Click **Settings** → **Database Connections** (or **Data** → **Databases**)
2. Click **+ Database** button
3. Select **PostgreSQL**
4. Fill in the connection details:

```
Host: sentiment-postgres
Port: 5432
Database: airflow
Username: airflow
Password: airflow
Display Name: Ukraine Tweets Sentiment DB
```

**Connection String (SQLAlchemy URI):**

```
postgresql://airflow:airflow@sentiment-postgres:5432/airflow
```

5. Click **Test Connection**
6. Click **Connect**

### Step 2: Load CSV Data into PostgreSQL

Run this script to load the sentiment results into PostgreSQL:

```python
python load_results_to_postgres.py
```

(I'll create this file for you below)

---

## Option 2: Connect to Druid (For Real-time Analytics)

The pipeline already sends data to Druid!

### Add Druid Database Connection

1. In Superset, go to **Settings** → **Database Connections**
2. Click **+ Database**
3. Select **Apache Druid**
4. Fill in:

```
Host: sentiment-druid-broker
Port: 8082
Database: druid/v2/sql
Display Name: Ukraine Tweets Druid
```

**Connection String (SQLAlchemy URI):**

```
druid://sentiment-druid-broker:8082/druid/v2/sql/
```

5. Click **Test Connection**
6. Click **Connect**

---

## Option 3: Upload CSV Directly to Superset

1. Go to **Data** → **Upload a CSV**
2. Browse to: `data/processed/sentiment_results.csv`
3. Set Table Name: `ukraine_tweets_sentiment`
4. Click **Save**

---

## Creating Your First Dashboard

### After connecting the database:

1. **Create a Dataset:**

    - Go to **Data** → **Datasets**
    - Click **+ Dataset**
    - Select your database
    - Select the table/datasource
    - Click **Add**

2. **Create Charts:**

    - Go to **Charts** → **+ Chart**
    - Select your dataset
    - Choose visualization type:
        - **Pie Chart** for sentiment distribution
        - **Time Series** for tweets over time
        - **Bar Chart** for top users
        - **Word Cloud** for hashtags

3. **Create Dashboard:**
    - Go to **Dashboards** → **+ Dashboard**
    - Add your charts
    - Arrange and style

---

## Recommended Visualizations

### 1. Sentiment Distribution (Pie Chart)

-   **Metrics**: COUNT(\*)
-   **Group By**: sentiment

### 2. Tweets Timeline (Time Series Line Chart)

-   **Metrics**: COUNT(\*)
-   **Time Column**: tweetcreatedts
-   **Group By**: sentiment

### 3. Top Users by Engagement (Bar Chart)

-   **Metrics**: SUM(followers), SUM(retweetcount)
-   **Group By**: username
-   **Sort**: Descending
-   **Limit**: 10

### 4. Sentiment by Location (Map or Table)

-   **Metrics**: COUNT(\*)
-   **Group By**: location, sentiment

### 5. Most Retweeted Tweets (Table)

-   **Columns**: username, text, retweetcount, sentiment
-   **Sort By**: retweetcount DESC
-   **Limit**: 20

---

## Troubleshooting

### Connection Issues:

1. **Can't connect to PostgreSQL?**

    - Make sure you're using the Docker internal network name: `sentiment-postgres`
    - Not `localhost` when running inside Docker

2. **Can't see the data?**

    - Run the script to load CSV into PostgreSQL first
    - Or check that Druid ingestion completed successfully

3. **Druid shows no data?**
    - Check if the ingestion task succeeded
    - Go to: http://localhost:8888 (Druid Console)
    - Check "Load Data" → "Supervisor" or "Task"

---

## Quick Start Commands

```bash
# Load results to PostgreSQL
python load_results_to_postgres.py

# Check Druid data
docker exec sentiment-druid-broker curl http://localhost:8082/druid/v2/sql -H "Content-Type: application/json" -d '{"query":"SELECT COUNT(*) as count FROM ukraine_tweets_sentiment"}'

# View Superset logs
docker logs sentiment-superset

# Restart Superset if needed
docker restart sentiment-superset
```

---

## Next Steps

After connecting:

1. Explore the data with SQL Lab (Superset's SQL editor)
2. Create visualizations
3. Build an interactive dashboard
4. Share with stakeholders!
