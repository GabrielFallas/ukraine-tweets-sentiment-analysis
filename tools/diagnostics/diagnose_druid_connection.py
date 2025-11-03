"""
Test Druid connectivity from different perspectives to troubleshoot Superset connection
"""
import requests
import json

print("=" * 80)
print("DRUID CONNECTIVITY DIAGNOSTIC")
print("=" * 80)

# Test 1: Check Druid Broker HTTP endpoint
print("\n1. Testing Druid Broker HTTP endpoint...")
try:
    response = requests.get("http://localhost:8083/status", timeout=5)
    print(f"   ✓ Broker is UP - Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot reach broker: {e}")

# Test 2: Check Druid SQL endpoint
print("\n2. Testing Druid SQL endpoint...")
druid_sql_url = "http://localhost:8083/druid/v2/sql"
test_query = {"query": "SELECT 1 as test"}

try:
    response = requests.post(druid_sql_url, json=test_query, timeout=5)
    if response.status_code == 200:
        print(f"   ✓ SQL endpoint working")
    else:
        print(f"   ✗ SQL endpoint returned: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ✗ SQL endpoint error: {e}")

# Test 3: List datasources
print("\n3. Checking available datasources...")
try:
    response = requests.get(
        "http://localhost:8082/druid/coordinator/v1/datasources", timeout=5)
    if response.status_code == 200:
        datasources = response.json()
        print(f"   ✓ Found {len(datasources)} datasource(s):")
        for ds in datasources:
            print(f"   - {ds}")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot list datasources: {e}")

# Test 4: Query the sentiment data
print("\n4. Querying ukraine_tweets_sentiment...")
sentiment_query = {
    "query": "SELECT COUNT(*) as count FROM \"ukraine_tweets_sentiment\""
}

try:
    response = requests.post(druid_sql_url, json=sentiment_query, timeout=5)
    if response.status_code == 200:
        result = response.json()
        if result:
            print(
                f"   ✓ Query successful - Found {result[0]['count']} records")
        else:
            print(f"   ⚠ Query returned no results")
    else:
        print(f"   ✗ Query failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ✗ Query error: {e}")

# Test 5: Get table schema
print("\n5. Checking table schema...")
schema_query = {
    "query": """
    SELECT COLUMN_NAME, DATA_TYPE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'ukraine_tweets_sentiment'
    LIMIT 20
    """
}

try:
    response = requests.post(druid_sql_url, json=schema_query, timeout=5)
    if response.status_code == 200:
        columns = response.json()
        if columns:
            print(f"   ✓ Found {len(columns)} columns:")
            for col in columns[:10]:  # Show first 10
                print(f"   - {col['COLUMN_NAME']}: {col['DATA_TYPE']}")
        else:
            print(f"   ⚠ No schema information available")
    else:
        print(f"   ✗ Schema query failed: {response.status_code}")
except Exception as e:
    print(f"   ✗ Schema error: {e}")

print("\n" + "=" * 80)
print("SUPERSET CONNECTION RECOMMENDATIONS")
print("=" * 80)

print("\nBased on the tests above, try these connection strings in Superset:")
print("\n✅ RECOMMENDED (use port 8083 - broker's SQL port):")
print("   druid://sentiment-druid-broker:8082/druid/v2/sql/")
print("\nAlternative formats to try:")
print("   1. druid://druid-broker:8082/druid/v2/sql/")
print("   2. druid://sentiment-druid-broker:8082/druid/v2/sql")
print("   3. druid://sentiment-druid-broker:8082/druid/v2/sql/?header=true")

print("\n📝 If still having issues:")
print("   1. Check Superset logs: docker logs sentiment-superset --tail 100")
print("   2. Verify network connectivity from Superset container:")
print("      docker exec sentiment-superset ping sentiment-druid-broker")
print("   3. Try using PostgreSQL instead (data is in CSV, can load there)")
print("   4. Check if Druid needs authentication (usually no for local setup)")

print("\n🔧 Quick fixes to try:")
print("   1. Restart Superset: docker restart sentiment-superset")
print("   2. Clear Superset cache: Settings → Database Connections → Edit → Refresh")
print("   3. Use 'druid' as schema name when creating dataset")
print("=" * 80)
