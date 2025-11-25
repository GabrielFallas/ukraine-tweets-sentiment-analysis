"""
Airflow DAG for Ukraine Twitter Sentiment Analysis Pipeline
Orchestrates data ingestion, Spark processing, and Druid loading
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import logging
import os
import json
import requests
import pandas as pd
from sqlalchemy import create_engine, text
import sqlalchemy
import time

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Paths
DATA_DIR = '/opt/airflow/data'
RAW_DATA_PATH = f'{DATA_DIR}/raw/ukraine_tweets_sample_100000.csv'
PROCESSED_DATA_PATH = f'{DATA_DIR}/processed/sentiment_results'
SPARK_APP_PATH = '/opt/airflow/spark/sentiment_analysis.py'


def check_data_exists(**context):
    """Check if the raw data file exists"""
    if not os.path.exists(RAW_DATA_PATH):
        logger.error(f"Data file not found at {RAW_DATA_PATH}")
        raise FileNotFoundError(
            f"Please download the Ukraine tweets dataset from Kaggle and place it at {RAW_DATA_PATH}"
        )

    # Get file size
    file_size = os.path.getsize(RAW_DATA_PATH)
    logger.info(
        f"Data file found: {RAW_DATA_PATH} ({file_size / (1024*1024):.2f} MB)")

    # Push file info to XCom
    context['task_instance'].xcom_push(key='file_size', value=file_size)
    context['task_instance'].xcom_push(key='file_path', value=RAW_DATA_PATH)


def validate_spark_output(**context):
    """Validate that Spark job produced output"""
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(
            f"Spark output not found at {PROCESSED_DATA_PATH}")

    # Check for CSV files in the output directory
    csv_files = [f for f in os.listdir(
        PROCESSED_DATA_PATH) if f.endswith('.csv')]

    if not csv_files:
        raise ValueError("No CSV files found in Spark output directory")

    logger.info(f"Found {len(csv_files)} CSV file(s) in output directory")

    # Push output info to XCom
    context['task_instance'].xcom_push(
        key='output_path', value=PROCESSED_DATA_PATH)
    context['task_instance'].xcom_push(key='csv_files', value=csv_files)


def prepare_druid_ingestion_spec(**context):
    """
    Create Druid ingestion specification for the processed data
    """
    # Get output path from previous task
    output_path = context['task_instance'].xcom_pull(
        task_ids='validate_output',
        key='output_path'
    )

    # Find the actual CSV file (Spark writes part files)
    csv_files = [f for f in os.listdir(output_path) if f.endswith(
        '.csv') and not f.startswith('.')]

    if not csv_files:
        raise ValueError("No CSV files found for Druid ingestion")

    csv_file_path = os.path.join(output_path, csv_files[0])

    # Create Druid ingestion spec
    ingestion_spec = {
        "type": "index_parallel",
        "spec": {
            "ioConfig": {
                "type": "index_parallel",
                "inputSource": {
                    "type": "local",
                    "baseDir": "/opt/druid/data/processed/sentiment_results/",
                    "filter": "*.csv"
                },
                "inputFormat": {
                    "type": "csv",
                    "findColumnsFromHeader": True,
                    "skipHeaderRows": 0
                }
            },
            "tuningConfig": {
                "type": "index_parallel",
                "partitionsSpec": {
                    "type": "dynamic"
                }
            },
            "dataSchema": {
                "dataSource": "ukraine_tweets_sentiment",
                "timestampSpec": {
                    "column": "tweetcreatedts",
                    "format": "auto"
                },
                "dimensionsSpec": {
                    "dimensions": [
                        "userid",
                        "username",
                        "location",
                        "text",
                        "cleaned_text",
                        "hashtags",
                        "sentiment"
                    ]
                },
                "metricsSpec": [
                    {
                        "type": "count",
                        "name": "count"
                    },
                    {
                        "type": "longSum",
                        "name": "total_followers",
                        "fieldName": "followers"
                    },
                    {
                        "type": "longSum",
                        "name": "total_retweets",
                        "fieldName": "retweetcount"
                    }
                ],
                "granularitySpec": {
                    "type": "uniform",
                    "segmentGranularity": "DAY",
                    "queryGranularity": "HOUR",
                    "rollup": False
                }
            }
        }
    }

    # Save spec to file
    spec_path = f'{DATA_DIR}/druid_ingestion_spec.json'
    with open(spec_path, 'w') as f:
        json.dump(ingestion_spec, f, indent=2)

    logger.info(f"Druid ingestion spec saved to {spec_path}")

    context['task_instance'].xcom_push(
        key='ingestion_spec_path', value=spec_path)
    context['task_instance'].xcom_push(
        key='ingestion_spec', value=ingestion_spec)


def submit_to_druid(**context):
    """
    Submit ingestion task to Druid
    """
    ingestion_spec = context['task_instance'].xcom_pull(
        task_ids='prepare_druid_spec',
        key='ingestion_spec'
    )

    # Druid Overlord API endpoint
    druid_url = "http://druid-coordinator:8081/druid/indexer/v1/task"

    try:
        response = requests.post(
            druid_url,
            json=ingestion_spec,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        response.raise_for_status()

        task_id = response.json().get('task')
        logger.info(f"Druid ingestion task submitted successfully: {task_id}")

        context['task_instance'].xcom_push(key='druid_task_id', value=task_id)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to submit Druid ingestion task: {str(e)}")
        raise


def log_pipeline_metadata(**context):
    """
    Log pipeline execution metadata to PostgreSQL
    """
    hook = PostgresHook(postgres_conn_id='postgres_default')

    execution_date = context['execution_date']
    file_size = context['task_instance'].xcom_pull(
        task_ids='check_data', key='file_size')
    druid_task_id = context['task_instance'].xcom_pull(
        task_ids='submit_to_druid', key='druid_task_id')

    insert_query = """
    INSERT INTO pipeline_metadata (execution_date, file_size, druid_task_id, status, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    """

    try:
        hook.run(
            insert_query,
            parameters=(execution_date, file_size, druid_task_id, 'SUCCESS')
        )
        logger.info("Pipeline metadata logged successfully")
    except Exception as e:
        logger.warning(f"Failed to log metadata: {str(e)}")


def load_results_to_postgres(**context):
    """
    Load sentiment analysis results from CSV to PostgreSQL
    """
    logger.info("Loading results to PostgreSQL...")

    csv_path = os.path.join(PROCESSED_DATA_PATH, 'sentiment_results.csv')

    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Results file not found: {csv_path}")

    # Read CSV with more robust settings
    logger.info(f"Reading CSV from {csv_path}")
    try:
        df = pd.read_csv(
            csv_path,
            on_bad_lines='skip',
            encoding='utf-8',
            escapechar='\\'
        )
        logger.info(f"Read {len(df)} rows from CSV")
    except Exception as e:
        logger.error(f"Failed to read CSV: {str(e)}")
        # Try with Python engine
        logger.info("Trying alternative CSV reading method...")
        df = pd.read_csv(
            csv_path,
            on_bad_lines='skip',
            engine='python',
            encoding='utf-8',
            escapechar='\\'
        )
        logger.info(
            f"Successfully read {len(df)} rows with alternative method")

    # Get PostgreSQL connection details from Airflow connection
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_connection('postgres_default')

    # Create SQLAlchemy engine
    engine = create_engine(
        f'postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}'
    )

    # Convert columns to proper types
    logger.info("Converting data types...")
    numeric_columns = ['userid', 'followers',
                       'following', 'tweetid', 'retweetcount', 'favorite_count']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors='coerce').fillna(0).astype('int64')

    # Convert timestamp columns
    logger.info("Converting timestamp columns...")
    timestamp_columns = ['tweetcreatedts', 'usercreatedts']
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Load to PostgreSQL
    logger.info("Loading data to PostgreSQL table 'ukraine_tweets_sentiment'...")
    df.to_sql('ukraine_tweets_sentiment', engine,
              if_exists='replace', index=False,
              dtype={
                  'tweetcreatedts': sqlalchemy.types.DateTime(),
                  'usercreatedts': sqlalchemy.types.DateTime()
              })

    # Create indexes
    logger.info("Creating indexes...")
    with engine.begin() as conn:  # Use begin() for auto-commit
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_sentiment ON ukraine_tweets_sentiment(sentiment)"))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_tweetcreatedts ON ukraine_tweets_sentiment(tweetcreatedts)"))

    # Get summary
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT sentiment, COUNT(*) as count
            FROM ukraine_tweets_sentiment
            GROUP BY sentiment
            ORDER BY sentiment
        """))
        summary = {row[0]: row[1] for row in result}

    logger.info(f"✓ Successfully loaded {len(df)} rows to PostgreSQL")
    logger.info(f"Sentiment distribution: {summary}")

    # Store summary in XCom
    context['task_instance'].xcom_push(key='postgres_row_count', value=len(df))
    context['task_instance'].xcom_push(
        key='sentiment_distribution', value=summary)


def setup_superset_connection(**context):
    """
    Configure PostgreSQL database connection in Superset
    """
    logger.info("Setting up Superset database connection...")

    superset_url = "http://superset:8088"
    username = "admin"
    password = "admin"

    # Create session to maintain cookies
    session = requests.Session()

    # Login to Superset
    logger.info("Authenticating with Superset...")
    login_url = f"{superset_url}/api/v1/security/login"
    login_payload = {
        "username": username,
        "password": password,
        "provider": "db",
        "refresh": True
    }

    try:
        response = session.post(login_url, json=login_payload, timeout=30)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("✓ Successfully authenticated with Superset")
    except Exception as e:
        logger.error(f"Failed to authenticate with Superset: {str(e)}")
        raise

    # Get CSRF token
    logger.info("Fetching CSRF token...")
    csrf_url = f"{superset_url}/api/v1/security/csrf_token/"
    csrf_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = session.get(csrf_url, headers=csrf_headers, timeout=30)
        response.raise_for_status()
        csrf_token = response.json().get("result")
        logger.info("✓ Successfully obtained CSRF token")
    except Exception as e:
        logger.error(f"Failed to get CSRF token: {str(e)}")
        raise

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
        "Referer": superset_url
    }

    # Check if PostgreSQL database already exists
    logger.info("Checking for existing PostgreSQL connection...")
    db_url = f"{superset_url}/api/v1/database/"

    try:
        response = session.get(db_url, headers=headers, timeout=30)
        response.raise_for_status()
        databases = response.json().get("result", [])

        postgres_db = None
        for db in databases:
            if db.get("database_name") == "PostgreSQL - Ukraine Tweets":
                postgres_db = db
                logger.info(
                    f"✓ Found existing PostgreSQL connection with ID: {db.get('id')}")
                break

        if not postgres_db:
            # Create new database connection
            logger.info("Creating new PostgreSQL database connection...")
            db_config = {
                "database_name": "PostgreSQL - Ukraine Tweets",
                "sqlalchemy_uri": "postgresql://airflow:airflow@sentiment-postgres:5432/sentiment",
                "expose_in_sqllab": True,
                "allow_ctas": False,
                "allow_cvas": False,
                "allow_dml": True,
                "allow_file_upload": False,
                "extra": "{}"
            }

            response = session.post(
                db_url, headers=headers, json=db_config, timeout=30)

            if response.status_code != 201:
                logger.error(
                    f"Failed to create database. Status: {response.status_code}, Response: {response.text}")

            response.raise_for_status()
            db_id = response.json().get("id")
            logger.info(f"✓ Created PostgreSQL connection with ID: {db_id}")
        else:
            db_id = postgres_db.get("id")

        # Store database ID in XCom
        context['task_instance'].xcom_push(key='superset_db_id', value=db_id)

        logger.info("✓ Superset database connection configured successfully")

    except Exception as e:
        logger.error(f"Failed to configure Superset database: {str(e)}")
        raise


def create_superset_dashboard(**context):
    """
    Create Superset dashboard with charts using API
    """
    logger.info("Creating Superset dashboard...")

    superset_url = "http://superset:8088"
    username = "admin"
    password = "admin"

    # Create session to maintain cookies
    session = requests.Session()

    # Login to Superset
    logger.info("Authenticating with Superset...")
    login_url = f"{superset_url}/api/v1/security/login"
    login_payload = {
        "username": username,
        "password": password,
        "provider": "db",
        "refresh": True
    }

    try:
        response = session.post(login_url, json=login_payload, timeout=30)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("✓ Successfully authenticated with Superset")
    except Exception as e:
        logger.error(f"Failed to authenticate with Superset: {str(e)}")
        raise

    # Get CSRF token
    logger.info("Fetching CSRF token...")
    csrf_url = f"{superset_url}/api/v1/security/csrf_token/"
    csrf_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = session.get(csrf_url, headers=csrf_headers, timeout=30)
        response.raise_for_status()
        csrf_token = response.json().get("result")
        logger.info("✓ Successfully obtained CSRF token")
    except Exception as e:
        logger.error(f"Failed to get CSRF token: {str(e)}")
        raise

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
        "Referer": superset_url
    }

    # Get database ID from previous task
    db_id = context['task_instance'].xcom_pull(
        task_ids='setup_superset_connection', key='superset_db_id')

    if not db_id:
        logger.error("Database ID not found from previous task")
        raise ValueError("Database ID not available")

    logger.info(f"Using database ID: {db_id}")

    # Create or get dataset
    logger.info("Creating/getting dataset...")
    dataset_url = f"{superset_url}/api/v1/dataset/"
    dataset_payload = {
        "database": db_id,
        "schema": "public",
        "table_name": "ukraine_tweets_sentiment"
    }

    try:
        response = session.post(
            dataset_url, headers=headers, json=dataset_payload, timeout=30)

        if response.status_code == 201:
            dataset_id = response.json().get("id")
            logger.info(f"✓ Created dataset with ID: {dataset_id}")

            # Update dataset to set main datetime column
            update_url = f"{dataset_url}{dataset_id}"
            update_payload = {
                "main_dttm_col": "tweetcreatedts"
            }
            try:
                update_response = session.put(
                    update_url, headers=headers, json=update_payload, timeout=30)
                if update_response.status_code == 200:
                    logger.info("✓ Set datetime column for dataset")
                else:
                    logger.warning(
                        f"Could not set datetime column: {update_response.text}")
            except Exception as update_error:
                logger.warning(
                    f"Could not update dataset datetime: {str(update_error)}")

        elif response.status_code == 422:
            # Dataset exists, find it
            logger.info("Dataset already exists, fetching...")
            response = session.get(dataset_url, headers=headers, timeout=30)
            response.raise_for_status()
            datasets = response.json().get("result", [])
            dataset_id = None
            for ds in datasets:
                if ds.get("table_name") == "ukraine_tweets_sentiment":
                    dataset_id = ds.get("id")
                    logger.info(
                        f"✓ Found existing dataset with ID: {dataset_id}")

                    # Update dataset to set main_dttm_col
                    update_url = f"{dataset_url}{dataset_id}"
                    update_payload = {
                        "main_dttm_col": "tweetcreatedts"
                    }
                    try:
                        update_response = session.put(
                            update_url, headers=headers, json=update_payload, timeout=30)
                        if update_response.status_code == 200:
                            logger.info(
                                "✓ Updated dataset with datetime column")
                        else:
                            logger.warning(
                                f"Could not set datetime column: {update_response.text}")
                    except Exception as update_error:
                        logger.warning(
                            f"Could not update dataset datetime: {str(update_error)}")

                    break
            if not dataset_id:
                raise ValueError("Could not find or create dataset")
        else:
            logger.error(f"Failed to create dataset: {response.text}")
            raise ValueError(
                f"Dataset creation failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Error with dataset: {str(e)}")
        raise

    time.sleep(2)  # Allow Superset to process

    # Get or create charts
    logger.info("Getting/creating charts...")
    chart_url = f"{superset_url}/api/v1/chart/"
    chart_ids = []

    charts_config = [
        # 1. Sentiment Trends Over Time (Line Chart) - INSIGHTFUL
        {
            "slice_name": "📈 Sentiment Evolution Over Time",
            "viz_type": "echarts_timeseries_line",
            "params": json.dumps({
                "metrics": ["count"],
                "groupby": ["sentiment"],
                "time_grain_sqla": "P1D",
                "granularity_sqla": "tweetcreatedts",
                "time_range": "No filter",
                "color_scheme": "supersetColors",
                "show_legend": True,
                "rich_tooltip": True,
                "y_axis_format": ",.0f",
                "x_axis_time_format": "smart_date",
                "logAxis": False,
                "y_axis_title": "Number of Tweets"
            })
        },
        # 2. Overall Sentiment Distribution (Donut Chart) - INSIGHTFUL
        {
            "slice_name": "📊 Overall Sentiment Balance",
            "viz_type": "pie",
            "params": json.dumps({
                "adhoc_filters": [],
                "groupby": ["sentiment"],
                "metric": "count",
                "row_limit": 10000,
                "sort_by_metric": True,
                "color_scheme": "supersetColors",
                "show_labels": True,
                "show_legend": True,
                "donut": True,
                "show_labels_threshold": 5,
                "number_format": ",.0f",
                "label_type": "key_percent"
            })
        },
        # 3. Top Hashtags (Word Cloud) - INSIGHTFUL
        {
            "slice_name": "☁️ Trending Topics (Hashtags)",
            "viz_type": "word_cloud",
            "params": json.dumps({
                "series": "hashtags",
                "metric": "count",
                "row_limit": 50,
                "size_from": "10",
                "size_to": "70",
                "rotation": "square",
                "color_scheme": "supersetColors"
            })
        },
        # 4. Most Viral Tweets (Table) - INSIGHTFUL
        {
            "slice_name": "🔥 Most Viral Tweets (Top Retweeted)",
            "viz_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "groupby": ["text", "username", "sentiment"],
                "metrics": ["sum__retweetcount"],
                "all_columns": [],
                "percent_metrics": [],
                "timeseries_limit_metric": "sum__retweetcount",
                "order_by_cols": ["[\"sum__retweetcount\", false]"],
                "order_desc": True,
                "row_limit": 50,
                "include_time": False,
                "table_timestamp_format": "smart_date",
                "page_length": 10,
                "align_pn": False,
                "color_pn": False
            })
        },
        # 5. Geographic Sentiment (Treemap) - INSIGHTFUL
        {
            "slice_name": "🗺️ Geographic Sentiment Distribution",
            "viz_type": "treemap",
            "params": json.dumps({
                "groupby": ["location"],
                "metrics": ["count"],
                "color_scheme": "bnbColors",
                "treemap_ratio": 1.618,
                "number_format": ",.0f",
                "row_limit": 50
            })
        },
        # 6. Engagement by Sentiment (Bar Chart) - INSIGHTFUL
        {
            "slice_name": "👍 Engagement by Sentiment",
            "viz_type": "dist_bar",
            "params": json.dumps({
                "adhoc_filters": [],
                "groupby": ["sentiment"],
                "columns": [],
                "metrics": [
                    {
                        "expressionType": "SIMPLE",
                        "column": {
                            "column_name": "retweetcount",
                            "type": "BIGINT"
                        },
                        "aggregate": "SUM",
                        "label": "Total Retweets"
                    }
                ],
                "row_limit": 10,
                "order_desc": True,
                "contribution": False,
                "color_scheme": "supersetColors",
                "show_legend": False,
                "y_axis_format": ",.0f",
                "show_bar_value": True,
                "y_axis_title": "Total Retweets"
            })
        },
        # 7. Total Reach (Big Number) - INSIGHTFUL
        {
            "slice_name": "📢 Total Potential Reach (Followers)",
            "viz_type": "big_number_total",
            "params": json.dumps({
                "metric": {
                    "expressionType": "SIMPLE",
                    "column": {
                        "column_name": "followers",
                        "type": "BIGINT"
                    },
                    "aggregate": "SUM",
                    "label": "Total Followers"
                },
                "header_font_size": 0.4,
                "subheader_font_size": 0.15
            })
        },
        # 8. Total Tweets (Big Number) - BASIC
        {
            "slice_name": "💬 Total Tweets Analyzed",
            "viz_type": "big_number_total",
            "params": json.dumps({
                "metric": "count",
                "header_font_size": 0.4,
                "subheader_font_size": 0.15
            })
        }
    ]

    # First, get existing charts
    try:
        response = session.get(chart_url, headers=headers, timeout=30)
        response.raise_for_status()
        existing_charts = response.json().get("result", [])
        logger.info(f"Found {len(existing_charts)} existing charts")
    except Exception as e:
        logger.warning(f"Could not fetch existing charts: {str(e)}")
        existing_charts = []

    for chart_config in charts_config:
        chart_config["datasource_id"] = dataset_id
        chart_config["datasource_type"] = "table"
        chart_name = chart_config["slice_name"]

        # Check if chart already exists
        existing_chart = None
        for chart in existing_charts:
            if chart.get("slice_name") == chart_name:
                existing_chart = chart
                chart_id = chart.get("id")
                chart_ids.append(chart_id)
                logger.info(
                    f"✓ Found existing chart '{chart_name}' with ID: {chart_id}")
                break

        if not existing_chart:
            # Create new chart
            try:
                response = session.post(
                    chart_url, headers=headers, json=chart_config, timeout=30)
                if response.status_code == 201:
                    chart_id = response.json().get("id")
                    chart_ids.append(chart_id)
                    logger.info(
                        f"✓ Created chart '{chart_name}' with ID: {chart_id}")
                else:
                    logger.warning(
                        f"Failed to create chart '{chart_name}': {response.text}")
            except Exception as e:
                logger.warning(
                    f"Error creating chart '{chart_name}': {str(e)}")

        time.sleep(0.5)

    if not chart_ids:
        logger.error("No charts were created or found")
        raise ValueError("Chart creation/retrieval failed")

    logger.info(f"Using {len(chart_ids)} charts: {chart_ids}")

    # Create dashboard
    logger.info("Creating/updating dashboard...")
    dashboard_api_url = f"{superset_url}/api/v1/dashboard/"
    dashboard_slug = "ukraine-tweets-sentiment"

    # Check if dashboard already exists
    logger.info("Checking for existing dashboard...")
    try:
        response = session.get(dashboard_api_url, headers=headers, timeout=30)
        response.raise_for_status()
        dashboards = response.json().get("result", [])

        existing_dashboard = None
        for dash in dashboards:
            if dash.get("slug") == dashboard_slug:
                existing_dashboard = dash
                logger.info(
                    f"✓ Found existing dashboard with ID: {dash.get('id')}")
                break
    except Exception as e:
        logger.warning(f"Could not check for existing dashboard: {str(e)}")
        existing_dashboard = None

    # Create dashboard config without position_json (Superset will auto-generate)
    dashboard_config = {
        "dashboard_title": "Ukraine Tweets Sentiment Analysis",
        "slug": dashboard_slug,
        "published": True
    }

    try:
        if existing_dashboard:
            # Use existing dashboard
            dashboard_id = existing_dashboard.get("id")
            logger.info(f"Using existing dashboard (ID: {dashboard_id})")
        else:
            # Create new dashboard
            logger.info("Creating new dashboard...")
            response = session.post(
                dashboard_api_url, headers=headers, json=dashboard_config, timeout=30)

            if response.status_code == 201:
                dashboard_id = response.json().get("id")
                logger.info(f"✓ Created dashboard with ID: {dashboard_id}")
            elif response.status_code == 422:
                # Dashboard exists but we couldn't find it, try to get it
                logger.info("Dashboard may already exist, fetching...")
                response = session.get(
                    dashboard_api_url, headers=headers, timeout=30)
                response.raise_for_status()
                dashboards = response.json().get("result", [])
                dashboard_id = None
                for dash in dashboards:
                    if dash.get("slug") == dashboard_slug:
                        dashboard_id = dash.get("id")
                        logger.info(
                            f"✓ Found existing dashboard with ID: {dashboard_id}")
                        break
                if not dashboard_id:
                    raise ValueError("Dashboard exists but could not be found")
            else:
                logger.error(f"Failed to create dashboard: {response.text}")
                raise ValueError(
                    f"Dashboard creation failed: {response.status_code}")

        # Now add charts to the dashboard using PUT endpoint
        logger.info(f"Adding {len(chart_ids)} charts to dashboard...")
        update_url = f"{dashboard_api_url}{dashboard_id}"
        update_payload = {
            "charts": chart_ids
        }

        response = session.put(
            update_url, headers=headers, json=update_payload, timeout=30)

        if response.status_code == 200:
            logger.info(f"✓ Successfully added charts to dashboard")
        else:
            logger.warning(
                f"Chart addition via API not supported, will link charts directly")

            # Link charts to dashboard via direct database connection
            try:
                # Connect to Superset database
                hook = PostgresHook(postgres_conn_id='postgres_default')
                conn_info = hook.get_connection('postgres_default')

                # Create connection to superset database
                engine = create_engine(
                    f'postgresql://{conn_info.login}:{conn_info.password}@{conn_info.host}:{conn_info.port}/superset'
                )

                with engine.begin() as db_conn:
                    # First, remove existing chart associations
                    db_conn.execute(text(
                        "DELETE FROM dashboard_slices WHERE dashboard_id = :dashboard_id"
                    ), {"dashboard_id": dashboard_id})

                    # Add new chart associations
                    for chart_id in chart_ids:
                        db_conn.execute(text(
                            "INSERT INTO dashboard_slices (dashboard_id, slice_id) VALUES (:dashboard_id, :slice_id)"
                        ), {"dashboard_id": dashboard_id, "slice_id": chart_id})

                    logger.info(
                        f"✓ Successfully linked {len(chart_ids)} charts to dashboard via database")

            except Exception as db_error:
                # Generate dashboard URL
                logger.warning(
                    f"Could not link charts via database: {str(db_error)}")
        final_dashboard_url = f"{superset_url}/superset/dashboard/{dashboard_id}/"
        logger.info(f"✓ Dashboard URL: {final_dashboard_url}")

        # Store in XCom
        context['task_instance'].xcom_push(
            key='dashboard_id', value=dashboard_id)
        context['task_instance'].xcom_push(
            key='dashboard_url', value=final_dashboard_url)

    except Exception as e:
        logger.error(f"Error with dashboard: {str(e)}")
        raise

    logger.info("✓ Superset dashboard configured successfully!")


def log_pipeline_metadata(**context):
    """
    Log pipeline execution metadata to PostgreSQL
    """
    hook = PostgresHook(postgres_conn_id='postgres_default')

    execution_date = context['execution_date']
    file_size = context['task_instance'].xcom_pull(
        task_ids='check_data', key='file_size')
    druid_task_id = context['task_instance'].xcom_pull(
        task_ids='submit_to_druid', key='druid_task_id')

    insert_query = """
    INSERT INTO pipeline_metadata (execution_date, file_size, druid_task_id, status, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    """

    try:
        hook.run(
            insert_query,
            parameters=(execution_date, file_size, druid_task_id, 'SUCCESS')
        )
        logger.info("Pipeline metadata logged successfully")
    except Exception as e:
        logger.warning(f"Failed to log metadata: {str(e)}")


# Define the DAG
with DAG(
    'twitter_sentiment_pipeline',
    default_args=default_args,
    description='Process Ukraine tweets and perform sentiment analysis',
    schedule_interval=None,  # Manual trigger only - no automatic scheduling
    catchup=False,
    tags=['sentiment-analysis', 'twitter', 'spark', 'druid'],
) as dag:

    # Task 1: Check if data exists
    check_data_task = PythonOperator(
        task_id='check_data',
        python_callable=check_data_exists,
        provide_context=True,
    )

    # Task 2: Create output directory
    create_output_dir_task = BashOperator(
        task_id='create_output_dir',
        bash_command=f'mkdir -p {PROCESSED_DATA_PATH}',
    )

    # Task 3: Create PostgreSQL metadata table
    create_metadata_table_task = PostgresOperator(
        task_id='create_metadata_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS pipeline_metadata (
            id SERIAL PRIMARY KEY,
            execution_date TIMESTAMP NOT NULL,
            file_size BIGINT,
            druid_task_id VARCHAR(255),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
    )

    # Task 4: Run Spark sentiment analysis job with 0.1% sample (~70K tweets)
    spark_job_task = SparkSubmitOperator(
        task_id='run_spark_sentiment_analysis',
        application=SPARK_APP_PATH,
        name='ukraine-twitter-sentiment-analysis',
        conn_id='spark_default',
        verbose=True,
        application_args=[RAW_DATA_PATH, PROCESSED_DATA_PATH],
        conf={
            'spark.driver.memory': '2g',
            'spark.executor.memory': '3g',
            'spark.executor.cores': '2',
            'spark.memory.fraction': '0.8',
            'spark.memory.storageFraction': '0.3',
        },
        execution_timeout=timedelta(hours=4),
    )

    # Task 5: Validate Spark output
    validate_output_task = PythonOperator(
        task_id='validate_output',
        python_callable=validate_spark_output,
        provide_context=True,
    )

    # Task 6: Load results to PostgreSQL
    load_postgres_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_results_to_postgres,
        provide_context=True,
    )

    # Task 7: Prepare Druid ingestion specification
    prepare_druid_spec_task = PythonOperator(
        task_id='prepare_druid_spec',
        python_callable=prepare_druid_ingestion_spec,
        provide_context=True,
    )

    # Task 8: Submit ingestion task to Druid
    submit_druid_task = PythonOperator(
        task_id='submit_to_druid',
        python_callable=submit_to_druid,
        provide_context=True,
    )

    # Task 9: Setup Superset database connection
    setup_superset_task = PythonOperator(
        task_id='setup_superset_connection',
        python_callable=setup_superset_connection,
        provide_context=True,
    )

    # Task 10: Create Superset dashboard
    create_dashboard_task = PythonOperator(
        task_id='create_superset_dashboard',
        python_callable=create_superset_dashboard,
        provide_context=True,
    )

    # Task 11: Log pipeline metadata
    log_metadata_task = PythonOperator(
        task_id='log_metadata',
        python_callable=log_pipeline_metadata,
        provide_context=True,
    )

    # Task 12: Send success notification
    success_notification_task = BashOperator(
        task_id='success_notification',
        bash_command='echo "Pipeline completed successfully at $(date)"',
    )

    # Define task dependencies
    check_data_task >> create_output_dir_task >> create_metadata_table_task
    create_metadata_table_task >> spark_job_task >> validate_output_task

    # After validation, split into two parallel paths:
    # Path 1: Load to PostgreSQL -> Setup Superset -> Create Dashboard
    # Path 2: Load to Druid
    validate_output_task >> load_postgres_task >> setup_superset_task >> create_dashboard_task
    validate_output_task >> prepare_druid_spec_task >> submit_druid_task

    # Both paths converge at metadata logging
    [create_dashboard_task,
        submit_druid_task] >> log_metadata_task >> success_notification_task
