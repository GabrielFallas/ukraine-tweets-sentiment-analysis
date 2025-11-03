"""
Test Druid ingestion and verify data loaded successfully
"""
import requests
import json
import time

print("=" * 80)
print("DRUID INGESTION TEST & VERIFICATION")
print("=" * 80)

COORDINATOR_URL = "http://localhost:8082"
BROKER_URL = "http://localhost:8083"

# Step 1: Check if Druid services are running
print("\n1. Checking Druid services...")
try:
    coord_response = requests.get(f"{COORDINATOR_URL}/status")
    print(f"   ✓ Coordinator: {coord_response.status_code}")

    broker_response = requests.get(f"{BROKER_URL}/status")
    print(f"   ✓ Broker: {broker_response.status_code}")
except Exception as e:
    print(f"   ✗ Error connecting to Druid: {e}")
    print("\n   Make sure Druid services are running:")
    print("   docker-compose ps | grep druid")
    exit(1)

# Step 2: Load and submit ingestion spec
print("\n2. Submitting ingestion task...")
try:
    with open('data/druid_ingestion_spec.json', 'r') as f:
        ingestion_spec = json.load(f)

    response = requests.post(
        f"{COORDINATOR_URL}/druid/indexer/v1/task",
        json=ingestion_spec,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        task_id = response.json().get('task')
        print(f"   ✓ Task submitted: {task_id}")
    else:
        print(f"   ✗ Failed to submit task: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Step 3: Monitor task status
print("\n3. Monitoring task status...")
max_wait = 60  # seconds
start_time = time.time()

while time.time() - start_time < max_wait:
    try:
        status_response = requests.get(
            f"{COORDINATOR_URL}/druid/indexer/v1/task/{task_id}/status"
        )

        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get('status', {}).get('status', 'UNKNOWN')

            print(f"   Status: {status}", end='\r')

            if status == 'SUCCESS':
                print(f"\n   ✓ Task completed successfully!")
                break
            elif status == 'FAILED':
                print(f"\n   ✗ Task failed!")
                print(
                    f"   Error: {status_data.get('status', {}).get('errorMsg', 'Unknown error')}")
                exit(1)

        time.sleep(2)
    except Exception as e:
        print(f"\n   ✗ Error checking status: {e}")
        break

if time.time() - start_time >= max_wait:
    print(f"\n   ⚠ Task still running after {max_wait} seconds")

# Step 4: Check datasources
print("\n4. Checking datasources...")
try:
    response = requests.get(
        f"{COORDINATOR_URL}/druid/coordinator/v1/datasources")
    datasources = response.json()
    print(f"   Found {len(datasources)} datasource(s):")
    for ds in datasources:
        print(f"   - {ds}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 5: Check segments
print("\n5. Checking data segments...")
try:
    response = requests.get(
        f"{COORDINATOR_URL}/druid/coordinator/v1/datasources/ukraine_tweets_sentiment/segments"
    )

    if response.status_code == 200:
        segments = response.json()
        print(f"   ✓ Found {len(segments)} segment(s)")

        if len(segments) > 0:
            print(f"   First segment: {segments[0]['identifier']}")
    elif response.status_code == 204:
        print(f"   ⚠ No segments found (204 - No Content)")
        print(f"   This means the datasource exists but has no data")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 6: Query the data
print("\n6. Querying data...")
try:
    query = {
        "query": "SELECT sentiment, COUNT(*) as count FROM ukraine_tweets_sentiment GROUP BY sentiment",
        "context": {
            "sqlTimeZone": "UTC"
        }
    }

    response = requests.post(
        f"{BROKER_URL}/druid/v2/sql",
        json=query,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        results = response.json()
        if results:
            print(f"   ✓ Data query successful!")
            print(f"\n   Sentiment Distribution:")
            for row in results:
                print(f"   - {row['sentiment']}: {row['count']} tweets")
        else:
            print(f"   ⚠ Query returned no results")
    else:
        print(f"   ✗ Query failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 7: Get total count
print("\n7. Getting total record count...")
try:
    query = {
        "query": "SELECT COUNT(*) as total FROM ukraine_tweets_sentiment"
    }

    response = requests.post(
        f"{BROKER_URL}/druid/v2/sql",
        json=query,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        results = response.json()
        if results:
            total = results[0]['total']
            print(f"   ✓ Total records in Druid: {total}")
        else:
            print(f"   ⚠ No data found")
    else:
        print(f"   ✗ Failed: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("DRUID INGESTION TEST COMPLETE")
print("=" * 80)
print("\n📝 Next Steps:")
print("1. If successful, data is now in Druid!")
print("2. Connect Superset to Druid:")
print("   - URI: druid://sentiment-druid-broker:8082/druid/v2/sql/")
print("3. Check docs/CONNECT_SUPERSET_TO_DRUID.md for details")
