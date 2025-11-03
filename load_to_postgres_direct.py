"""
Simple direct insertion to PostgreSQL using psycopg2
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

print("=" * 80)
print("LOADING DATA TO POSTGRESQL FOR SUPERSET")
print("=" * 80)

# Step 1: Read CSV
print("\n1. Reading CSV file...")
try:
    df = pd.read_csv('data/processed/sentiment_results.csv',
                     on_bad_lines='skip',
                     engine='python')
    print(f"   ✓ Read {len(df)} rows")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 2: Connect to PostgreSQL
print("\n2. Connecting to PostgreSQL...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()
    print("   ✓ Connected")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 3: Create table
print("\n3. Creating table...")
try:
    cur.execute("DROP TABLE IF EXISTS ukraine_tweets_sentiment")
    cur.execute("""
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
        )
    """)
    conn.commit()
    print("   ✓ Table created")
except Exception as e:
    print(f"   ✗ Error: {e}")
    conn.rollback()
    exit(1)

# Step 4: Insert data
print("\n4. Inserting data...")
try:
    # Replace NaN with None
    df = df.fillna('')

    # Helper function to safely convert to int
    def safe_int(val):
        try:
            if val == '' or val == 'nan':
                return 0
            return int(float(val))
        except:
            return 0

    # Convert DataFrame to list of tuples
    data = []
    for _, row in df.iterrows():
        data.append((
            safe_int(row['userid']),
            str(row['username'])[:255] if row['username'] != '' else '',
            str(row['location']) if row['location'] != '' else '',
            safe_int(row['followers']),
            safe_int(row['following']),
            safe_int(row['tweetid']),
            str(row['tweetcreatedts']) if row['tweetcreatedts'] != '' else None,
            str(row['text']) if row['text'] != '' else '',
            str(row['cleaned_text']) if row['cleaned_text'] != '' else '',
            str(row['hashtags']) if row['hashtags'] != '' else '',
            safe_int(row['retweetcount']),
            str(row['sentiment']) if row['sentiment'] != '' else ''
        ))

    # Batch insert
    execute_values(
        cur,
        """
        INSERT INTO ukraine_tweets_sentiment 
        (userid, username, location, followers, following, tweetid, tweetcreatedts, 
         text, cleaned_text, hashtags, retweetcount, sentiment)
        VALUES %s
        """,
        data
    )
    conn.commit()
    print(f"   ✓ Inserted {len(data)} rows")
except Exception as e:
    print(f"   ✗ Error: {e}")
    conn.rollback()
    exit(1)

# Step 5: Create indexes
print("\n5. Creating indexes...")
try:
    cur.execute(
        "CREATE INDEX idx_sentiment ON ukraine_tweets_sentiment(sentiment)")
    cur.execute(
        "CREATE INDEX idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts)")
    conn.commit()
    print("   ✓ Indexes created")
except Exception as e:
    print(f"   ⚠ Warning: {e}")

# Step 6: Show summary
print("\n6. Data summary:")
try:
    cur.execute("""
        SELECT sentiment, COUNT(*) as count
        FROM ukraine_tweets_sentiment
        GROUP BY sentiment
        ORDER BY sentiment
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]} tweets")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Cleanup
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✓ SUCCESS! DATA READY IN POSTGRESQL")
print("=" * 80)

print("\n🎯 Next Steps - Connect Superset to PostgreSQL:")
print("\n1. Open Superset: http://localhost:8088")
print("   Login: admin / admin")
print("\n2. Go to: Settings → Database Connections → + Database")
print("\n3. Select: PostgreSQL")
print("\n4. Use this connection string:")
print("   postgresql://airflow:airflow@sentiment-postgres:5432/airflow")
print("\n   OR enter manually:")
print("   Host: sentiment-postgres")
print("   Port: 5432")
print("   Database: airflow")
print("   User: airflow")
print("   Password: airflow")
print("\n5. Test connection and save")
print("\n6. Create dataset from table: ukraine_tweets_sentiment")
