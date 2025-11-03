"""
Quick script to verify Druid has your data and get connection info for Superset
"""
import requests
import json

print("=" * 80)
print("CHECKING DRUID DATA FOR SUPERSET CONNECTION")
print("=" * 80)

# Druid broker endpoint
druid_url = "http://localhost:8083/druid/v2/sql"

# Check what datasources exist
print("\n1. Checking available datasources in Druid...")
query = {
    "query": "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'druid'"
}

try:
    response = requests.post(druid_url, json=query, timeout=10)
    if response.status_code == 200:
        tables = response.json()
        print(f"   ✓ Found {len(tables)} datasource(s):")
        for table in tables:
            print(f"   - {table.get('TABLE_NAME', 'unknown')}")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Could not connect: {e}")

# Check ukraine_tweets_sentiment data
print("\n2. Checking ukraine_tweets_sentiment data...")
check_query = {
    "query": "SELECT COUNT(*) as total_tweets FROM ukraine_tweets_sentiment"
}

try:
    response = requests.post(druid_url, json=check_query, timeout=10)
    if response.status_code == 200:
        result = response.json()
        if result:
            count = result[0].get('total_tweets', 0)
            print(f"   ✓ Found {count} tweets in Druid!")
        else:
            print("   ⚠ Datasource exists but no data found")
            print("   This is normal - the Druid ingestion may still be processing")
    else:
        print(f"   ⚠ Status: {response.status_code}")
        print("   The datasource may not exist yet or ingestion is pending")
except Exception as e:
    print(f"   ⚠ Could not query: {e}")

# Get sentiment distribution
print("\n3. Getting sentiment distribution...")
sentiment_query = {
    "query": """
    SELECT sentiment, COUNT(*) as count 
    FROM ukraine_tweets_sentiment 
    GROUP BY sentiment 
    ORDER BY count DESC
    """
}

try:
    response = requests.post(druid_url, json=sentiment_query, timeout=10)
    if response.status_code == 200:
        results = response.json()
        if results:
            print("   ✓ Sentiment breakdown:")
            for row in results:
                print(
                    f"   - {row.get('sentiment')}: {row.get('count')} tweets")
        else:
            print("   ⚠ No sentiment data available yet")
except Exception as e:
    print(f"   ⚠ Could not get distribution: {e}")

print("\n" + "=" * 80)
print("SUPERSET CONNECTION INFORMATION")
print("=" * 80)
print("\nTo connect Superset to Druid:")
print("\n1. Open Superset: http://localhost:8088")
print("   Login: admin / admin")
print("\n2. Go to: Settings → Database Connections")
print("\n3. Click: + Database")
print("\n4. Select: Apache Druid")
print("\n5. Enter connection details:")
print("   SQLAlchemy URI: druid://sentiment-druid-broker:8082/druid/v2/sql/")
print("   Display Name: Ukraine Tweets Druid")
print("\n6. Click: Test Connection")
print("\n7. Click: Connect")
print("\n8. Create a dataset:")
print("   - Go to: Data → Datasets")
print("   - Click: + Dataset")
print("   - Database: Ukraine Tweets Druid")
print("   - Table: ukraine_tweets_sentiment")
print("\n9. Create visualizations!")
print("=" * 80)
