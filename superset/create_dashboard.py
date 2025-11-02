"""
Superset Dashboard Configuration for Ukraine Tweets Sentiment Analysis
Automatically creates charts and dashboards using Superset API
"""

import requests
import json
import time
import sys
from typing import Dict, Any

SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


class SupersetDashboardCreator:
    """Creates Superset dashboards programmatically"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.csrf_token = None

    def login(self) -> bool:
        """Authenticate with Superset"""
        login_url = f"{self.base_url}/api/v1/security/login"

        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True
        }

        try:
            response = requests.post(login_url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")

            print("✓ Successfully authenticated with Superset")
            return True

        except Exception as e:
            print(f"✗ Failed to authenticate: {str(e)}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_database_id(self, database_name: str = "Druid") -> int:
        """Get database ID by name"""
        url = f"{self.base_url}/api/v1/database/"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            databases = response.json().get("result", [])

            for db in databases:
                if db.get("database_name") == database_name:
                    print(
                        f"✓ Found database '{database_name}' with ID: {db.get('id')}")
                    return db.get("id")

            print(f"✗ Database '{database_name}' not found")
            return None

        except Exception as e:
            print(f"✗ Error getting database: {str(e)}")
            return None

    def create_dataset(self, database_id: int) -> int:
        """Create dataset from Druid datasource"""
        url = f"{self.base_url}/api/v1/dataset/"

        payload = {
            "database": database_id,
            "schema": "druid",
            "table_name": "ukraine_tweets_sentiment"
        }

        try:
            response = requests.post(
                url, headers=self.get_headers(), json=payload)

            if response.status_code == 201:
                dataset_id = response.json().get("id")
                print(f"✓ Created dataset with ID: {dataset_id}")
                return dataset_id
            elif response.status_code == 422:
                # Dataset might already exist, try to get it
                print("Dataset might already exist, fetching existing dataset...")
                return self.get_dataset_id("ukraine_tweets_sentiment")
            else:
                print(f"✗ Failed to create dataset: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating dataset: {str(e)}")
            return None

    def get_dataset_id(self, table_name: str) -> int:
        """Get existing dataset ID"""
        url = f"{self.base_url}/api/v1/dataset/"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            datasets = response.json().get("result", [])

            for ds in datasets:
                if ds.get("table_name") == table_name:
                    print(
                        f"✓ Found dataset '{table_name}' with ID: {ds.get('id')}")
                    return ds.get("id")

            return None

        except Exception as e:
            print(f"✗ Error getting dataset: {str(e)}")
            return None

    def create_chart(self, dataset_id: int, chart_config: Dict[str, Any]) -> int:
        """Create a chart"""
        url = f"{self.base_url}/api/v1/chart/"

        try:
            response = requests.post(
                url, headers=self.get_headers(), json=chart_config)

            if response.status_code == 201:
                chart_id = response.json().get("id")
                print(
                    f"✓ Created chart '{chart_config['slice_name']}' with ID: {chart_id}")
                return chart_id
            else:
                print(f"✗ Failed to create chart: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating chart: {str(e)}")
            return None

    def create_sentiment_over_time_chart(self, dataset_id: int) -> int:
        """Create sentiment over time line chart"""
        chart_config = {
            "slice_name": "Sentiment Over Time",
            "viz_type": "line",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "time_range": "No filter",
                "granularity_sqla": "tweetcreatedts",
                "metrics": ["count"],
                "groupby": ["sentiment"],
                "viz_type": "line",
                "color_scheme": "supersetColors",
                "show_legend": True,
                "show_markers": True,
                "line_interpolation": "linear",
                "x_axis_format": "smart_date",
                "y_axis_format": ",d"
            })
        }

        return self.create_chart(dataset_id, chart_config)

    def create_sentiment_distribution_chart(self, dataset_id: int) -> int:
        """Create sentiment distribution pie chart"""
        chart_config = {
            "slice_name": "Sentiment Distribution",
            "viz_type": "pie",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metric": "count",
                "groupby": ["sentiment"],
                "viz_type": "pie",
                "color_scheme": "supersetColors",
                "show_labels": True,
                "show_legend": True,
                "donut": False,
                "labels_outside": True
            })
        }

        return self.create_chart(dataset_id, chart_config)

    def create_top_locations_chart(self, dataset_id: int) -> int:
        """Create top locations by tweet count bar chart"""
        chart_config = {
            "slice_name": "Top Locations by Tweet Count",
            "viz_type": "bar",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metrics": ["count"],
                "groupby": ["location"],
                "viz_type": "bar",
                "color_scheme": "supersetColors",
                "show_legend": False,
                "x_axis_label": "Location",
                "y_axis_label": "Tweet Count",
                "row_limit": 10,
                "order_desc": True
            })
        }

        return self.create_chart(dataset_id, chart_config)

    def create_sentiment_by_location_chart(self, dataset_id: int) -> int:
        """Create sentiment by location heatmap"""
        chart_config = {
            "slice_name": "Sentiment by Location",
            "viz_type": "heatmap",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "metric": "count",
                "groupby": ["location"],
                "columns": ["sentiment"],
                "viz_type": "heatmap",
                "color_scheme": "supersetColors",
                "linear_color_scheme": "blue_white_yellow",
                "xscale_interval": 1,
                "yscale_interval": 1,
                "show_values": True,
                "row_limit": 10
            })
        }

        return self.create_chart(dataset_id, chart_config)

    def create_dashboard(self, chart_ids: list) -> int:
        """Create dashboard with charts"""
        url = f"{self.base_url}/api/v1/dashboard/"

        # Create position metadata for charts
        position_json = {}
        row = 0

        for i, chart_id in enumerate(chart_ids):
            col = (i % 2) * 6
            if i % 2 == 0 and i > 0:
                row += 4

            position_json[f"CHART-{chart_id}"] = {
                "type": "CHART",
                "id": chart_id,
                "children": [],
                "meta": {
                    "width": 6,
                    "height": 4,
                    "chartId": chart_id
                }
            }

        dashboard_config = {
            "dashboard_title": "Ukraine Tweets Sentiment Analysis",
            "slug": "ukraine-tweets-sentiment",
            "position_json": json.dumps(position_json),
            "published": True
        }

        try:
            response = requests.post(
                url, headers=self.get_headers(), json=dashboard_config)

            if response.status_code == 201:
                dashboard_id = response.json().get("id")
                print(f"✓ Created dashboard with ID: {dashboard_id}")
                return dashboard_id
            else:
                print(f"✗ Failed to create dashboard: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating dashboard: {str(e)}")
            return None

    def run(self):
        """Execute the complete dashboard creation workflow"""
        print("\n" + "="*60)
        print("Superset Dashboard Creation")
        print("="*60 + "\n")

        # Step 1: Login
        if not self.login():
            return False

        time.sleep(2)

        # Step 2: Get database ID
        database_id = self.get_database_id("Druid")
        if not database_id:
            print("Please ensure Druid is configured in Superset")
            return False

        time.sleep(2)

        # Step 3: Create or get dataset
        dataset_id = self.create_dataset(database_id)
        if not dataset_id:
            return False

        time.sleep(2)

        # Step 4: Create charts
        print("\nCreating charts...")
        chart_ids = []

        charts = [
            ("Sentiment Over Time", self.create_sentiment_over_time_chart),
            ("Sentiment Distribution", self.create_sentiment_distribution_chart),
            ("Top Locations", self.create_top_locations_chart),
            ("Sentiment by Location", self.create_sentiment_by_location_chart)
        ]

        for chart_name, chart_func in charts:
            chart_id = chart_func(dataset_id)
            if chart_id:
                chart_ids.append(chart_id)
            time.sleep(2)

        if not chart_ids:
            print("✗ No charts were created")
            return False

        # Step 5: Create dashboard
        print("\nCreating dashboard...")
        dashboard_id = self.create_dashboard(chart_ids)

        if dashboard_id:
            print("\n" + "="*60)
            print("✓ Dashboard created successfully!")
            print(
                f"View at: {self.base_url}/superset/dashboard/{dashboard_id}/")
            print("="*60 + "\n")
            return True

        return False


def main():
    """Main entry point"""
    creator = SupersetDashboardCreator(SUPERSET_URL, USERNAME, PASSWORD)

    success = creator.run()

    if success:
        print("Dashboard setup complete!")
        sys.exit(0)
    else:
        print("Dashboard setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
