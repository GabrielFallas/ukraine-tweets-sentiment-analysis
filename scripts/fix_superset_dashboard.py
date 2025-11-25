import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_superset_dashboard():
    """
    Fix Superset dashboard charts without re-running the entire pipeline
    """
    logger.info("Starting Superset dashboard fix...")

    superset_url = "http://localhost:8088"
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

    # Get dataset ID
    logger.info("Getting dataset ID...")
    dataset_url = f"{superset_url}/api/v1/dataset/"

    try:
        response = session.get(dataset_url, headers=headers, timeout=30)
        response.raise_for_status()
        datasets = response.json().get("result", [])
        dataset_id = None
        for ds in datasets:
            if ds.get("table_name") == "ukraine_tweets_sentiment":
                dataset_id = ds.get("id")
                logger.info(f"✓ Found existing dataset with ID: {dataset_id}")
                break

        if not dataset_id:
            raise ValueError(
                "Could not find dataset 'ukraine_tweets_sentiment'")

    except Exception as e:
        logger.error(f"Error getting dataset: {str(e)}")
        raise

    # Define FIXED chart configurations
    charts_config = [
        # 1. Sentiment Trends Over Time (Line Chart) - FIXED
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
                "y_axis_title": "Number of Tweets",
                "zoomable": True
            })
        },
        # 2. Overall Sentiment Distribution (Donut Chart) - FIXED
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
        # 3. Top Hashtags (Table instead of Word Cloud for stability) - FIXED
        {
            "slice_name": "☁️ Trending Topics (Hashtags)",
            "viz_type": "table",
            "params": json.dumps({
                "groupby": ["hashtags"],
                "metrics": ["count"],
                "row_limit": 50,
                "order_desc": True,
                "percent_metrics": [],
                "timeseries_limit_metric": "count",
                "include_time": False
            })
        },
        # 4. Most Viral Tweets (Table) - FIXED
        {
            "slice_name": "🔥 Most Viral Tweets (Top Retweeted)",
            "viz_type": "table",
            "params": json.dumps({
                "adhoc_filters": [],
                "groupby": ["text", "username", "sentiment"],
                "metrics": [{
                    "expressionType": "SIMPLE",
                    "column": {
                        "column_name": "retweetcount",
                        "type": "BIGINT"
                    },
                    "aggregate": "SUM",
                    "label": "Total Retweets"
                }],
                "all_columns": [],
                "percent_metrics": [],
                "order_by_cols": ["[\"Total Retweets\", false]"],
                "order_desc": True,
                "row_limit": 50,
                "include_time": False,
                "table_timestamp_format": "smart_date",
                "page_length": 10,
                "align_pn": False,
                "color_pn": False
            })
        },
        # 5. Geographic Sentiment (Stacked Bar Chart) - FIXED
        {
            "slice_name": "🗺️ Geographic Sentiment Distribution",
            "viz_type": "dist_bar",
            "params": json.dumps({
                "groupby": ["location"],
                "columns": ["sentiment"],
                "metrics": ["count"],
                "adhoc_filters": [
                    {
                        "expressionType": "SIMPLE",
                        "subject": "location",
                        "operator": "!=",
                        "comparator": "",
                        "clause": "WHERE"
                    },
                    {
                        "expressionType": "SIMPLE",
                        "subject": "location",
                        "operator": "IS NOT NULL",
                        "clause": "WHERE"
                    }
                ],
                "row_limit": 20,
                "bar_stacked": True,
                "order_desc": True,
                "color_scheme": "supersetColors",
                "show_legend": True,
                "y_axis_format": ",.0f",
                "x_axis_label": "Location",
                "y_axis_label": "Number of Tweets",
                "show_bar_value": False
            })
        },
        # 6. Engagement by Sentiment (Bar Chart) - FIXED
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
        # 7. Total Reach (Big Number) - FIXED
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
        # 8. Total Tweets (Big Number) - FIXED
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

    # Get existing charts
    chart_url = f"{superset_url}/api/v1/chart/"
    try:
        response = session.get(chart_url, headers=headers, timeout=30)
        response.raise_for_status()
        existing_charts = response.json().get("result", [])
        logger.info(f"Found {len(existing_charts)} existing charts")
    except Exception as e:
        logger.warning(f"Could not fetch existing charts: {str(e)}")
        existing_charts = []

    chart_ids = []

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

                # UPDATE existing chart
                logger.info(
                    f"Updating existing chart '{chart_name}' (ID: {chart_id})...")
                try:
                    update_url = f"{chart_url}{chart_id}"
                    response = session.put(
                        update_url, headers=headers, json=chart_config, timeout=30)
                    if response.status_code == 200:
                        logger.info(f"✓ Updated chart '{chart_name}'")
                        chart_ids.append(chart_id)
                    else:
                        logger.warning(
                            f"Failed to update chart '{chart_name}': {response.text}")
                except Exception as e:
                    logger.warning(
                        f"Error updating chart '{chart_name}': {str(e)}")

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

    logger.info(f"Processed {len(chart_ids)} charts")
    logger.info("Dashboard fix completed!")


if __name__ == "__main__":
    fix_superset_dashboard()
