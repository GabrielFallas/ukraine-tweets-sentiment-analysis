# 📚 Documentation Index

Quick navigation for the Ukraine Tweets Sentiment Analysis Pipeline.

## Getting Started

| Document                       | Description                        |
| ------------------------------ | ---------------------------------- |
| [README.md](../README.md)      | Project overview, setup, and usage |
| [QUICKSTART.md](QUICKSTART.md) | 10-minute setup guide              |

## Reference

| Document                                   | Description                       |
| ------------------------------------------ | --------------------------------- |
| [ARCHITECTURE.md](ARCHITECTURE.md)         | System architecture and data flow |
| [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) | Pipeline automation details       |
| [SUPERSET.md](SUPERSET.md)                 | Visualization setup guide         |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md)   | Common issues and solutions       |

## Tools

See [tools/README.md](../tools/README.md) for utility scripts:

-   **Data Preparation**: Sample creation, dataset download
-   **Database Loaders**: Load results to PostgreSQL
-   **Diagnostics**: Pipeline monitoring and verification

## Quick Links

### Web Interfaces

| Service  | URL                   | Credentials       |
| -------- | --------------------- | ----------------- |
| Airflow  | http://localhost:8080 | airflow / airflow |
| Spark UI | http://localhost:8081 | -                 |
| Superset | http://localhost:8088 | admin / admin     |
| Druid    | http://localhost:8888 | -                 |

### Common Commands

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Stop services
docker-compose down
```

## External Resources

-   [Apache Airflow](https://airflow.apache.org/docs/)
-   [Apache Spark](https://spark.apache.org/docs/latest/)
-   [Apache Superset](https://superset.apache.org/docs/intro)
-   [Apache Druid](https://druid.apache.org/docs/latest/)
