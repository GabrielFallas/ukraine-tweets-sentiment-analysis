"""
Load sentiment results directly into PostgreSQL for Superset
This is simpler and more reliable than Druid for this use case
"""
import subprocess
import sys

print("=" * 80)
print("LOADING DATA TO POSTGRESQL FOR SUPERSET")
print("=" * 80)

# Step 1: Copy CSV into PostgreSQL container
print("\n1. Copying CSV file to PostgreSQL container...")
cmd = [
    "docker", "cp",
    "data/processed/sentiment_results.csv",
    "sentiment-postgres:/tmp/sentiment_results.csv"
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("   ✓ CSV copied to container")
else:
    print(f"   ✗ Error: {result.stderr}")
    sys.exit(1)

# Step 2: Create table and load data using psql
print("\n2. Creating table and loading data...")

sql_commands = """
-- Drop existing table if it exists
DROP TABLE IF EXISTS ukraine_tweets_sentiment;

-- Create table
CREATE TABLE ukraine_tweets_sentiment (
    userid BIGINT,
    username VARCHAR(255),
    location TEXT,
    followers BIGINT,
    following BIGINT,
    tweetid BIGINT,
    tweetcreatedts TIMESTAMP,
    text TEXT,
    cleaned_text TEXT,
    hashtags TEXT,
    retweetcount INTEGER,
    sentiment VARCHAR(20)
);

-- Load data from CSV
COPY ukraine_tweets_sentiment(userid, username, location, followers, following, tweetid, tweetcreatedts, text, cleaned_text, hashtags, retweetcount, sentiment)
FROM '/tmp/sentiment_results.csv'
DELIMITER ','
CSV HEADER
ENCODING 'UTF8';

-- Create indexes for better query performance
CREATE INDEX idx_sentiment ON ukraine_tweets_sentiment(sentiment);
CREATE INDEX idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts);
CREATE INDEX idx_username ON ukraine_tweets_sentiment(username);

-- Show summary
SELECT 
    'Total Tweets' as metric,
    COUNT(*)::text as value
FROM ukraine_tweets_sentiment
UNION ALL
SELECT 
    'Sentiment: ' || sentiment as metric,
    COUNT(*)::text as value
FROM ukraine_tweets_sentiment
GROUP BY sentiment
ORDER BY metric;
"""

cmd = [
    "docker", "exec", "-i", "sentiment-postgres",
    "psql", "-U", "airflow", "-d", "airflow", "-c", sql_commands
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("   ✓ Table created and data loaded!")
    print("\n" + result.stdout)
else:
    print(f"   ✗ Error: {result.stderr}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ SUCCESS! DATA READY IN POSTGRESQL")
print("=" * 80)

print("\n🎯 Next Steps - Connect Superset to PostgreSQL:")
print("\n1. Open Superset: http://localhost:8088")
print("   Login: admin / admin")
print("\n2. Go to: Settings → Database Connections")
print("\n3. Click: + Database")
print("\n4. Select: PostgreSQL")
print("\n5. Enter connection:")
print("   Host: sentiment-postgres")
print("   Port: 5432")
print("   Database: airflow")
print("   Username: airflow")
print("   Password: airflow")
print("\n   OR use this SQLAlchemy URI:")
print("   postgresql://airflow:airflow@sentiment-postgres:5432/airflow")
print("\n6. Test Connection → Connect")
print("\n7. Create Dataset:")
print("   Data → Datasets → + Dataset")
print("   Database: (your PostgreSQL connection)")
print("   Schema: public")
print("   Table: ukraine_tweets_sentiment")
print("\n8. Start creating visualizations!")
print("=" * 80)
