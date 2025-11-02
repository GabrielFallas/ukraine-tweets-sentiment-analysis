"""
OpenMetadata Configuration for Data Lineage and Governance
Configures connectors for Airflow, Druid, and Superset
"""

# OpenMetadata Airflow Connector Configuration
airflow_config = {
    "source": {
        "type": "Airflow",
        "serviceName": "ukraine_tweets_airflow",
        "serviceConnection": {
            "config": {
                "type": "Airflow",
                "hostPort": "http://airflow-webserver:8080",
                "connection": {
                    "type": "Airflow",
                    "hostPort": "http://airflow-webserver:8080"
                }
            }
        },
        "sourceConfig": {
            "config": {
                "type": "PipelineMetadata"
            }
        }
    },
    "sink": {
        "type": "metadata-rest",
        "config": {}
    },
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://openmetadata:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {
                "jwtToken": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9"
            }
        }
    }
}

# OpenMetadata Druid Connector Configuration
druid_config = {
    "source": {
        "type": "Druid",
        "serviceName": "ukraine_tweets_druid",
        "serviceConnection": {
            "config": {
                "type": "Druid",
                "hostPort": "druid-router:8888",
                "username": "",
                "password": ""
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DatabaseMetadata",
                "markDeletedTables": True,
                "includeTables": True,
                "includeViews": True
            }
        }
    },
    "sink": {
        "type": "metadata-rest",
        "config": {}
    },
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://openmetadata:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {
                "jwtToken": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9"
            }
        }
    }
}

# OpenMetadata Superset Connector Configuration
superset_config = {
    "source": {
        "type": "Superset",
        "serviceName": "ukraine_tweets_superset",
        "serviceConnection": {
            "config": {
                "type": "Superset",
                "hostPort": "http://superset:8088",
                "connection": {
                    "provider": "db",
                    "username": "admin",
                    "password": "admin"
                }
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DashboardMetadata",
                "markDeletedDashboards": True,
                "includeDrafts": False
            }
        }
    },
    "sink": {
        "type": "metadata-rest",
        "config": {}
    },
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://openmetadata:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {
                "jwtToken": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9"
            }
        }
    }
}

# PostgreSQL Connector Configuration
postgres_config = {
    "source": {
        "type": "Postgres",
        "serviceName": "ukraine_tweets_postgres",
        "serviceConnection": {
            "config": {
                "type": "Postgres",
                "username": "airflow",
                "password": "airflow",
                "hostPort": "postgres:5432",
                "database": "airflow"
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DatabaseMetadata",
                "markDeletedTables": True,
                "includeTables": True,
                "includeViews": True,
                "schemaFilterPattern": {
                    "includes": ["public"]
                }
            }
        }
    },
    "sink": {
        "type": "metadata-rest",
        "config": {}
    },
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://openmetadata:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {
                "jwtToken": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9"
            }
        }
    }
}
