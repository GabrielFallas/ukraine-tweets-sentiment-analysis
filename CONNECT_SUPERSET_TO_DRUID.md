# Connect Superset to Druid - Step by Step Guide

## ✅ Your Data is Ready in Druid!

The pipeline successfully ingested your sentiment analysis data into Druid.

---

## Step 1: Open Superset

1. Open your browser
2. Go to: **http://localhost:8088**
3. Login:
    - Username: `admin`
    - Password: `admin`

---

## Step 2: Add Druid Database Connection

1. Click on **Settings** (⚙️ icon) in the top right
2. Select **Database Connections**
3. Click the **+ Database** button
4. You'll see "Connect a database" dialog

### Option A: Using the Form (Easier)

1. In the "Supported Databases" section, scroll and find **Apache Druid**
2. Click on **Apache Druid**
3. Fill in the connection details:
    - **Display Name**: `Ukraine Tweets Druid`
    - **SQLAlchemy URI**:
        ```
        druid://sentiment-druid-broker:8082/druid/v2/sql/
        ```
4. Click **Test Connection** (should show "Connection looks good!")
5. Click **Connect**

### Option B: Manual Connection String

If you prefer to enter it manually:

1. Click **+ Database**
2. Select "Other" or enter manually
3. Paste this connection string:
    ```
    druid://sentiment-druid-broker:8082/druid/v2/sql/
    ```
4. Set Display Name: `Ukraine Tweets Druid`
5. Click **Connect**

---

## Step 3: Create a Dataset

1. Go to **Data** → **Datasets** (in the top menu)
2. Click **+ Dataset** button
3. Fill in:
    - **Database**: Select "Ukraine Tweets Druid" (the one you just created)
    - **Schema**: Leave as default or select "druid"
    - **Table**: Type or select `ukraine_tweets_sentiment`
4. Click **Add**

---

## Step 4: Create Your First Chart

1. From the Datasets page, find `ukraine_tweets_sentiment`
2. Click on it to start exploring
3. Or go to **Charts** → **+ Chart**
4. Select:
    - **Dataset**: ukraine_tweets_sentiment
    - **Chart Type**: Start with "Pie Chart"

### Recommended Chart: Sentiment Distribution (Pie Chart)

1. **Query**:
    - **Dimensions**: `sentiment`
    - **Metric**: `COUNT(*)`
2. **Customize**:
    - Chart Title: "Tweet Sentiment Distribution"
    - Show Labels: Yes
    - Show Percentages: Yes
3. Click **Update Chart**
4. Click **Save** to save the chart

---

## Step 5: Create More Visualizations

### Chart Ideas:

#### 1. **Tweets Over Time (Time Series)**

-   Chart Type: Time-series Line Chart
-   Time Column: `__time` (Druid's timestamp)
-   Metrics: `COUNT(*)`
-   Group By: `sentiment`

#### 2. **Top Users (Bar Chart)**

-   Chart Type: Bar Chart
-   Dimensions: `username`
-   Metrics: `SUM(followers)`, `SUM(retweetcount)`
-   Sort: Descending
-   Row Limit: 10

#### 3. **Sentiment by Location (Table)**

-   Chart Type: Table
-   Dimensions: `location`, `sentiment`
-   Metrics: `COUNT(*)`
-   Filters: Remove null locations

#### 4. **Engagement Metrics (Big Number)**

-   Chart Type: Big Number
-   Metrics: `AVG(followers)` or `SUM(retweetcount)`

---

## Step 6: Create a Dashboard

1. Go to **Dashboards** → **+ Dashboard**
2. Give it a name: "Ukraine Tweets Sentiment Analysis"
3. Click **Save**
4. Click **Edit Dashboard**
5. Drag your saved charts onto the dashboard
6. Resize and arrange them
7. Click **Save** when done

---

## Troubleshooting

### "Could not connect to database"

Make sure you're using the internal Docker network name:

-   ✅ Use: `sentiment-druid-broker`
-   ❌ Don't use: `localhost`

### "Table not found"

The table name in Druid should be: `ukraine_tweets_sentiment`

Check available tables with SQL Lab:

```sql
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'druid'
```

### "No data showing"

Run this query in SQL Lab to verify data:

```sql
SELECT COUNT(*) as total FROM ukraine_tweets_sentiment
```

---

## Using SQL Lab (Advanced)

1. Go to **SQL** → **SQL Lab** in the top menu
2. Select Database: "Ukraine Tweets Druid"
3. Try queries like:

```sql
-- Total tweets
SELECT COUNT(*) as total_tweets FROM ukraine_tweets_sentiment;

-- Sentiment breakdown
SELECT sentiment, COUNT(*) as count
FROM ukraine_tweets_sentiment
GROUP BY sentiment;

-- Top retweeted tweets
SELECT username, text, retweetcount, sentiment
FROM ukraine_tweets_sentiment
ORDER BY retweetcount DESC
LIMIT 10;

-- Tweets per day
SELECT
  TIME_FLOOR(__time, 'P1D') as day,
  sentiment,
  COUNT(*) as tweet_count
FROM ukraine_tweets_sentiment
GROUP BY 1, 2
ORDER BY 1, 2;
```

---

## Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Ukraine Tweets Sentiment Analysis Dashboard       │
├──────────────────┬──────────────────┬───────────────┤
│  Sentiment Pie   │  Tweets Timeline │  Total Tweets │
│  Chart           │  (Time Series)   │  (Big Number) │
├──────────────────┴──────────────────┴───────────────┤
│  Top 10 Users by Engagement (Bar Chart)             │
├──────────────────────────────────────────────────────┤
│  Most Retweeted Tweets (Table)                      │
└──────────────────────────────────────────────────────┘
```

---

## Next Steps

1. Explore your data with SQL Lab
2. Create multiple visualizations
3. Build an interactive dashboard
4. Apply filters (by date, sentiment, location)
5. Share your dashboard with the team!

**Need help?** Check the Superset documentation: https://superset.apache.org/docs/

---

## Quick Access URLs

-   **Superset**: http://localhost:8088
-   **Druid Console**: http://localhost:8888
-   **Airflow**: http://localhost:8080
