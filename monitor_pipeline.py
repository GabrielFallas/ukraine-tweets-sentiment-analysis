"""
Monitor the Airflow pipeline progress
"""
import subprocess
import time
import sys


def run_command(cmd):
    """Run a docker command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout


def get_dag_status():
    """Get the current DAG run status"""
    cmd = 'docker exec sentiment-airflow-webserver airflow dags list-runs -d twitter_sentiment_pipeline --state running'
    output = run_command(cmd)
    return output


def get_task_states(run_id):
    """Get task states for a specific run"""
    cmd = f'docker exec sentiment-airflow-webserver airflow tasks states-for-dag-run twitter_sentiment_pipeline {run_id}'
    output = run_command(cmd)
    return output


def monitor_pipeline():
    """Monitor the pipeline continuously"""
    print("=" * 80)
    print("UKRAINE TWEETS SENTIMENT ANALYSIS PIPELINE MONITOR")
    print("=" * 80)
    print("\nMonitoring DAG: twitter_sentiment_pipeline")
    print("Dataset: 70,000 tweets (pre-sampled)")
    print("\nPress Ctrl+C to stop monitoring\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*80}")
            print(
                f"Update #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print('='*80)

            # Get running DAGs
            dag_status = get_dag_status()

            if "manual__2025-11-03T21:06:13+00:00" in dag_status:
                print("\n✓ Pipeline is running")

                # Get task states
                task_states = get_task_states(
                    "manual__2025-11-03T21:06:13+00:00")

                # Parse and display task states
                print("\nTask Status:")
                print("-" * 80)

                for line in task_states.split('\n'):
                    if 'twitter_sentiment_pipeline' in line and '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            task_id = parts[2]
                            state = parts[3]

                            # Format output with emojis
                            if state == 'success':
                                status = '✓ SUCCESS'
                            elif state == 'running':
                                status = '⏳ RUNNING'
                            elif state == 'failed':
                                status = '✗ FAILED'
                            elif state == 'None':
                                status = '○ PENDING'
                            else:
                                status = f'  {state.upper()}'

                            print(f"  {status:15} | {task_id}")

                print("\n" + "-" * 80)
                print("Refreshing in 30 seconds...")
                time.sleep(30)
            else:
                print("\n✓ Pipeline completed or not running")
                print("\nFinal status:")

                # Check for completed runs
                cmd_completed = 'docker exec sentiment-airflow-webserver airflow dags list-runs -d twitter_sentiment_pipeline --state success'
                completed = run_command(cmd_completed)

                if "manual__2025-11-03T21:06:13+00:00" in completed:
                    print("✓ Pipeline completed successfully!")
                else:
                    print("Pipeline may have failed. Check Airflow UI for details.")

                break

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print("Pipeline is still running in the background.")
        print("Access Airflow UI at: http://localhost:8080")


if __name__ == "__main__":
    monitor_pipeline()
