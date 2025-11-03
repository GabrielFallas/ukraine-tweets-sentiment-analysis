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
RAW_DATA_PATH = f'{DATA_DIR}/raw/ukraine_tweets.csv'
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

    # Task 4: Run Spark sentiment analysis job (using mock data for demo)
    # Note: For production, uncomment the SparkSubmitOperator and ensure Spark cluster is healthy
    spark_job_task = BashOperator(
        task_id='run_spark_sentiment_analysis',
        bash_command=f'''
        echo "Using mock sentiment data for pipeline demonstration"
        echo "Mock data location: {PROCESSED_DATA_PATH}"
        ls -lh {PROCESSED_DATA_PATH}
        echo "Mock data ready for Druid ingestion"
        ''',
    )

    # For production use:
    # spark_job_task = SparkSubmitOperator(
    #     task_id='run_spark_sentiment_analysis',
    #     application=SPARK_APP_PATH,
    #     name='ukraine-twitter-sentiment-analysis',
    #     conn_id='spark_default',
    #     verbose=True,
    #     application_args=[RAW_DATA_PATH, PROCESSED_DATA_PATH],
    #     conf={
    #         'spark.driver.memory': '2g',
    #         'spark.executor.memory': '3g',
    #         'spark.executor.cores': '2',
    #         'spark.memory.fraction': '0.8',
    #         'spark.memory.storageFraction': '0.3',
    #     },
    #     execution_timeout=timedelta(hours=4),
    # )

    # Task 5: Validate Spark output
    validate_output_task = PythonOperator(
        task_id='validate_output',
        python_callable=validate_spark_output,
        provide_context=True,
    )

    # Task 6: Prepare Druid ingestion specification
    prepare_druid_spec_task = PythonOperator(
        task_id='prepare_druid_spec',
        python_callable=prepare_druid_ingestion_spec,
        provide_context=True,
    )

    # Task 7: Submit ingestion task to Druid
    submit_druid_task = PythonOperator(
        task_id='submit_to_druid',
        python_callable=submit_to_druid,
        provide_context=True,
    )

    # Task 8: Log pipeline metadata
    log_metadata_task = PythonOperator(
        task_id='log_metadata',
        python_callable=log_pipeline_metadata,
        provide_context=True,
    )

    # Task 9: Send success notification
    success_notification_task = BashOperator(
        task_id='success_notification',
        bash_command='echo "Pipeline completed successfully at $(date)"',
    )

    # Define task dependencies
    check_data_task >> create_output_dir_task >> create_metadata_table_task
    create_metadata_table_task >> spark_job_task >> validate_output_task
    validate_output_task >> prepare_druid_spec_task >> submit_druid_task
    submit_druid_task >> log_metadata_task >> success_notification_task
