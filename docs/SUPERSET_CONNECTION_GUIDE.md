# Connect Superset to PostgreSQL - Step by Step Guide

## ✅ Data Status

-   **101 tweets** loaded into PostgreSQL
-   **Table**: `ukraine_tweets_sentiment`
-   **Database**: `airflow` (PostgreSQL)
-   **Sentiment Distribution**:
    -   NEGATIVE: 74 tweets (73%)
    -   POSITIVE: 19 tweets (19%)
    -   NULL: 8 tweets (8%)

---

## 🔧 Step 1: Access Superset

1. Open your browser and go to: **http://localhost:8088**
2. Login with:
    - **Username**: `admin`
    - **Password**: `admin`

---

## 🔌 Step 2: Add Database Connection

1. Click the **Settings** icon (⚙️) in the top right
2. Select **Database Connections**
3. Click the **+ Database** button (blue button, top right)
4. In the modal that appears:

    - Select **PostgreSQL** from the database type dropdown
    - Click **Connect this database with a SQLAlchemy URI string instead**

5. Enter this connection string:

    ```
    postgresql://airflow:airflow@sentiment-postgres:5432/airflow
    ```

6. Click **Test Connection** button

    - You should see: ✅ "Connection looks good!"

7. Click **Connect** to save the connection

---

## 📊 Step 3: Create Dataset

1. From the top menu, go to: **Data** → **Datasets**
2. Click **+ Dataset** (blue button, top right)
3. Fill in the form:
    - **Database**: Select the PostgreSQL connection you just created
    - **Schema**: `public`
    - **Table**: `ukraine_tweets_sentiment`
4. Click **Add** button

---

## 📈 Step 4: Create Your First Chart

### Option A: Sentiment Distribution (Pie Chart)

1. From the Datasets page, find `ukraine_tweets_sentiment` and click on it
2. This opens the Explore view
3. Configure:
    - **Visualization Type**: Pie Chart
    - **Dimensions**: `sentiment`
    - **Metric**: `COUNT(*)`
4. Click **Update Chart** (or **Run**)
5. Once satisfied, click **Save** and give it a name like "Sentiment Distribution"

### Option B: Tweets Timeline (Line Chart)

1. From the dataset, choose **Line Chart**
2. Configure:
    - **X-Axis**: `tweetcreatedts` (temporal column)
    - **Metrics**: `COUNT(*)`
    - **Group By**: `sentiment`
3. Click **Update Chart**
4. Save as "Tweets Timeline"

### Option C: Top Users (Bar Chart)

1. Choose **Bar Chart**
2. Configure:
    - **Dimensions**: `username`
    - **Metrics**: `SUM(followers)`
    - **Row Limit**: 10
    - **Sort**: Descending
3. Click **Update Chart**
4. Save as "Top Users by Followers"

### Option D: Most Retweeted (Table)

1. Choose **Table**
2. Configure:
    - **Columns**: `username`, `text`, `retweetcount`, `sentiment`
    - **Metrics**: (leave empty to show raw data)
    - **Row Limit**: 20
    - **Sort By**: `retweetcount` (descending)
3. Click **Update Chart**
4. Save as "Most Retweeted Tweets"

---

## 🎨 Step 5: Create Dashboard

1. Go to **Dashboards** from the top menu
2. Click **+ Dashboard** (blue button)
3. Give it a name: "Ukraine Tweets Sentiment Analysis"
4. Click **Save**
5. Click **Edit Dashboard**
6. From the right panel, drag your saved charts onto the canvas
7. Arrange and resize as desired
8. Click **Save** when done

---

## 🐛 Troubleshooting

### Connection Test Fails

-   Make sure Docker containers are running: `docker ps`
-   Check that `sentiment-postgres` container is up
-   Verify you're using the container name `sentiment-postgres` not `localhost`

### Table Not Found

-   Verify table exists in PostgreSQL:
    ```powershell
    docker exec sentiment-postgres psql -U airflow -d airflow -c "\dt"
    ```
-   Look for `ukraine_tweets_sentiment` in the list

### No Data in Charts

-   Check data in database:
    ```powershell
    docker exec sentiment-postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM ukraine_tweets_sentiment;"
    ```
-   Should show: `101`

---

## 🚀 Next Steps

### Scale Up

Once your visualizations are working with the 100-row sample:

1. Update `twitter_sentiment_dag.py` line 35 to use larger dataset
2. Run the full pipeline
3. Re-run `load_to_postgres_sqlalchemy.py` to load new data
4. Your Superset charts will automatically show the new data!

### Advanced Analytics

-   Add filters by date range, username, or location
-   Calculate sentiment percentages with custom SQL metrics
-   Create word clouds from hashtags
-   Analyze trends over time with moving averages

---

## ✨ Your Data Is Ready!

All 101 tweets are now in PostgreSQL and ready to visualize. Follow the steps above to create your first dashboard! 🎉
