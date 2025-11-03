"""
Load sentiment analysis results into PostgreSQL for Superset visualization
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime


def load_results_to_postgres():
    """Load CSV results into PostgreSQL"""

    print("=" * 80)
    print("LOADING SENTIMENT RESULTS TO POSTGRESQL")
    print("=" * 80)

    # Connection parameters
    conn_params = {
        'host': 'localhost',  # Use localhost since we're running outside Docker
        'port': 5432,
        'database': 'airflow',
        'user': 'airflow',
        'password': 'airflow'
    }

    try:
        # Load CSV
        print("\n1. Loading CSV file...")
        df = pd.read_csv('data/processed/sentiment_results.csv',
                         on_bad_lines='skip',
                         engine='python',
                         encoding='utf-8')
        print(f"   ✓ Loaded {len(df)} rows")

        # Connect to PostgreSQL
        print("\n2. Connecting to PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        print("   ✓ Connected")

        # Create table
        print("\n3. Creating table...")
        create_table_sql = """
        DROP TABLE IF EXISTS ukraine_tweets_sentiment;
        
        CREATE TABLE ukraine_tweets_sentiment (
            id SERIAL PRIMARY KEY,
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
            sentiment VARCHAR(20),
            loaded_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX idx_sentiment ON ukraine_tweets_sentiment(sentiment);
        CREATE INDEX idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts);
        CREATE INDEX idx_username ON ukraine_tweets_sentiment(username);
        """

        cursor.execute(create_table_sql)
        conn.commit()
        print("   ✓ Table created")

        # Prepare data
        print("\n4. Preparing data for insertion...")
        # Convert timestamp column
        df['tweetcreatedts'] = pd.to_datetime(
            df['tweetcreatedts'], errors='coerce')

        # Prepare records
        columns = ['userid', 'username', 'location', 'followers', 'following',
                   'tweetid', 'tweetcreatedts', 'text', 'cleaned_text',
                   'hashtags', 'retweetcount', 'sentiment']

        records = []
        for _, row in df.iterrows():
            record = tuple(row[col] if pd.notna(row[col])
                           else None for col in columns)
            records.append(record)

        print(f"   ✓ Prepared {len(records)} records")

        # Insert data
        print("\n5. Inserting data into PostgreSQL...")
        insert_sql = """
        INSERT INTO ukraine_tweets_sentiment 
        (userid, username, location, followers, following, tweetid, 
         tweetcreatedts, text, cleaned_text, hashtags, retweetcount, sentiment)
        VALUES %s
        """

        execute_values(cursor, insert_sql, records)
        conn.commit()
        print(f"   ✓ Inserted {len(records)} rows")

        # Verify
        print("\n6. Verifying data...")
        cursor.execute("SELECT COUNT(*) FROM ukraine_tweets_sentiment")
        count = cursor.fetchone()[0]
        print(f"   ✓ Total rows in database: {count}")

        cursor.execute("""
            SELECT sentiment, COUNT(*) as count 
            FROM ukraine_tweets_sentiment 
            GROUP BY sentiment
            ORDER BY count DESC
        """)

        print("\n   Sentiment Distribution:")
        for row in cursor.fetchall():
            print(f"   - {row[0]}: {row[1]} tweets")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 80)
        print("✓ SUCCESS! Data loaded to PostgreSQL")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Open Superset: http://localhost:8088")
        print("2. Login with admin/admin")
        print("3. Add database connection:")
        print("   postgresql://airflow:airflow@sentiment-postgres:5432/airflow")
        print("4. Create dataset from 'ukraine_tweets_sentiment' table")
        print("5. Build your dashboard!")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    load_results_to_postgres()
