"""
Load data to PostgreSQL using pandas to_sql (simplest method)
"""
import pandas as pd
from sqlalchemy import create_engine

print("=" * 80)
print("LOADING DATA TO POSTGRESQL FOR SUPERSET")
print("=" * 80)

# Step 1: Read CSV
print("\n1. Reading CSV file...")
try:
    df = pd.read_csv('data/processed/sentiment_results.csv',
                     on_bad_lines='skip')
    print(f"   ✓ Read {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 2: Connect to PostgreSQL
print("\n2. Connecting to PostgreSQL...")
try:
    engine = create_engine(
        'postgresql://airflow:airflow@localhost:5432/airflow')
    print("   ✓ Connected")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 3: Load data to PostgreSQL
print("\n3. Loading data to PostgreSQL...")
try:
    # Convert problematic columns to proper types
    df['userid'] = pd.to_numeric(
        df['userid'], errors='coerce').fillna(0).astype('int64')
    df['followers'] = pd.to_numeric(
        df['followers'], errors='coerce').fillna(0).astype('int64')
    df['following'] = pd.to_numeric(
        df['following'], errors='coerce').fillna(0).astype('int64')
    df['tweetid'] = pd.to_numeric(
        df['tweetid'], errors='coerce').fillna(0).astype('int64')
    df['retweetcount'] = pd.to_numeric(
        df['retweetcount'], errors='coerce').fillna(0).astype('int64')

    # Upload to PostgreSQL (replaces table if exists)
    df.to_sql('ukraine_tweets_sentiment', engine,
              if_exists='replace', index=False)
    print(f"   ✓ Loaded {len(df)} rows to table 'ukraine_tweets_sentiment'")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 4: Create indexes
print("\n4. Creating indexes...")
try:
    with engine.connect() as conn:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sentiment ON ukraine_tweets_sentiment(sentiment)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts)")
        conn.commit()
    print("   ✓ Indexes created")
except Exception as e:
    print(f"   ⚠ Warning: {e}")

# Step 5: Show summary
print("\n5. Data summary:")
try:
    with engine.connect() as conn:
        result = conn.execute("""
            SELECT sentiment, COUNT(*) as count
            FROM ukraine_tweets_sentiment
            GROUP BY sentiment
            ORDER BY sentiment
        """)
        for row in result:
            print(f"   {row[0]}: {row[1]} tweets")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("✓ SUCCESS! DATA READY IN POSTGRESQL")
print("=" * 80)

print("\n🎯 Next Steps - Connect Superset to PostgreSQL:")
print("\n1. Open Superset: http://localhost:8088")
print("   Login: admin / admin")
print("\n2. Click: Settings (gear icon) → Database Connections")
print("\n3. Click: + Database (blue button)")
print("\n4. Select: PostgreSQL")
print("\n5. Connection URI:")
print("   postgresql://airflow:airflow@sentiment-postgres:5432/airflow")
print("\n6. Click 'Test Connection' → Should see success message")
print("\n7. Click 'Connect'")
print("\n8. Go to Datasets → + Dataset")
print("   - Database: Select your PostgreSQL connection")
print("   - Schema: public")
print("   - Table: ukraine_tweets_sentiment")
print("\n9. Start creating visualizations!")
print("\nSuggested Charts:")
print("  - Pie Chart: Sentiment distribution")
print("  - Bar Chart: Top users by followers")
print("  - Time Series: Tweets over time")
print("  - Table: Most retweeted tweets")
