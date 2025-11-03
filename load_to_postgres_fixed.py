"""
Load sentiment results into PostgreSQL after cleaning the CSV
"""
import pandas as pd
import subprocess
import sys

print("=" * 80)
print("LOADING DATA TO POSTGRESQL FOR SUPERSET")
print("=" * 80)

# Step 1: Clean the CSV
print("\n1. Cleaning CSV data...")
try:
    df = pd.read_csv('data/processed/sentiment_results.csv',
                     on_bad_lines='skip',
                     engine='python')

    # Remove newlines from text fields
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(
                '\n', ' ', regex=False).str.replace('\r', ' ', regex=False)

    # Save cleaned version
    cleaned_file = 'data/processed/sentiment_results_cleaned.csv'
    df.to_csv(cleaned_file, index=False)
    print(f"   ✓ Cleaned CSV: {len(df)} rows")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Step 2: Copy to container
print("\n2. Copying CSV to PostgreSQL container...")
cmd = [
    "docker", "cp",
    cleaned_file,
    "sentiment-postgres:/tmp/sentiment_results.csv"
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("   ✓ CSV copied to container")
else:
    print(f"   ✗ Error: {result.stderr}")
    sys.exit(1)

# Step 3: Create table and load data
print("\n3. Creating table and loading data...")

sql_commands = """
DROP TABLE IF EXISTS ukraine_tweets_sentiment;

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

COPY ukraine_tweets_sentiment
FROM '/tmp/sentiment_results.csv'
DELIMITER ','
CSV HEADER
QUOTE '"'
ESCAPE '"';

CREATE INDEX idx_sentiment ON ukraine_tweets_sentiment(sentiment);
CREATE INDEX idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts);

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
    "psql", "-U", "airflow", "-d", "airflow"
]

result = subprocess.run(cmd, input=sql_commands,
                        capture_output=True, text=True)
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
print("\n2. Go to: Settings → Database Connections → + Database")
print("\n3. Select: PostgreSQL")
print("\n4. Connection details:")
print("   Host: sentiment-postgres")
print("   Port: 5432")
print("   Database: airflow")
print("   User: airflow")
print("   Password: airflow")
print("\n5. Test connection, then save")
print("\n6. Go to: Datasets → + Dataset")
print("   Database: PostgreSQL (your connection)")
print("   Schema: public")
print("   Table: ukraine_tweets_sentiment")
print("\n7. Create charts and visualizations!")
