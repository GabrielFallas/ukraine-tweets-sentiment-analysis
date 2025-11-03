# Project Deployment Checklist

Use this checklist to ensure successful deployment of the sentiment analysis pipeline.

## Pre-Deployment Checklist

### System Requirements

-   [ ] Docker Desktop installed (Windows/Mac) or Docker Engine (Linux)
-   [ ] Docker version 20.10+ verified (`docker --version`)
-   [ ] docker-compose version 2.0+ verified (`docker-compose --version`)
-   [ ] At least 16GB RAM available
-   [ ] At least 20GB free disk space
-   [ ] Python 3.8+ installed (for key generation)
-   [ ] Internet connection available

### Initial Setup

-   [ ] Repository cloned or downloaded
-   [ ] Working directory is project root
-   [ ] All files present (27 files total)
-   [ ] Setup script executed (`./setup.sh` or `setup.bat`)
-   [ ] Data directories created (`data/raw/`, `data/processed/`)

### Configuration

-   [ ] `.env` file created from `.env.example`
-   [ ] Fernet key generated and added to `.env`
-   [ ] Superset secret key generated and added to `.env`
-   [ ] Keys validated (non-empty, correct format)

### Dataset

-   [ ] Kaggle account created
-   [ ] Dataset downloaded from Kaggle
-   [ ] CSV file renamed to `ukraine_tweets.csv`
-   [ ] File placed in `data/raw/` directory
-   [ ] File size verified (~500MB+)
-   [ ] File accessible (check permissions)

## Build Checklist

### Docker Images

-   [ ] All Dockerfiles present
-   [ ] Build command executed (`docker-compose build`)
-   [ ] All images built successfully
-   [ ] No build errors in logs
-   [ ] Image sizes reasonable (<2GB each)

### Verification

-   [ ] `docker images` shows all images
-   [ ] No dangling images
-   [ ] Sufficient disk space remaining

## Deployment Checklist

### Service Startup

-   [ ] `docker-compose up -d` executed
-   [ ] All 14 containers started
-   [ ] `docker-compose ps` shows all services running
-   [ ] No containers in "Restarting" or "Exited" state

### Container Health

-   [ ] PostgreSQL healthy (check with `docker-compose ps postgres`)
-   [ ] Airflow webserver healthy
-   [ ] Spark master running
-   [ ] Druid services started
-   [ ] Superset accessible
-   [ ] OpenMetadata running

### Network Connectivity

-   [ ] All containers on `sentiment-network`
-   [ ] Services can ping each other
-   [ ] No port conflicts

## Service Access Checklist

### Web Interfaces

-   [ ] Airflow UI accessible (http://localhost:8080)
-   [ ] Airflow login successful (admin/admin)
-   [ ] Spark Master UI accessible (http://localhost:8081)
-   [ ] Druid router responding (http://localhost:8888)
-   [ ] Superset accessible (http://localhost:8088)
-   [ ] Superset login successful (admin/admin)
-   [ ] OpenMetadata accessible (http://localhost:8585)
-   [ ] OpenMetadata login successful (admin/admin)

### Service Health Endpoints

-   [ ] Airflow health: `curl http://localhost:8080/health`
-   [ ] Spark status: `curl http://localhost:8081`
-   [ ] Druid status: `curl http://localhost:8888/status`
-   [ ] Superset health: `curl http://localhost:8088/health`

## Pipeline Execution Checklist

### Airflow DAG

-   [ ] DAG `twitter_sentiment_pipeline` visible in UI
-   [ ] DAG has no import errors
-   [ ] DAG toggled ON
-   [ ] DAG structure shows all 9 tasks
-   [ ] Task dependencies correct

### Manual Trigger

-   [ ] DAG triggered manually
-   [ ] First task (check_data) succeeds
-   [ ] Spark job starts
-   [ ] Spark job completes without errors
-   [ ] Output validation passes
-   [ ] Druid ingestion succeeds
-   [ ] All tasks turn green

### Pipeline Validation

-   [ ] Check Airflow logs (no errors)
-   [ ] Check Spark logs (no exceptions)
-   [ ] Check Druid logs (ingestion successful)
-   [ ] Processed data in `data/processed/`
-   [ ] Metadata logged to PostgreSQL

## Data Verification Checklist

### Processed Data

-   [ ] CSV files in `data/processed/sentiment_results/`
-   [ ] Files contain sentiment column
-   [ ] Data has expected structure
-   [ ] Row count matches input (approximately)

### Druid Ingestion

-   [ ] Datasource `ukraine_tweets_sentiment` exists
-   [ ] Segments loaded
-   [ ] Data queryable via SQL
-   [ ] Test query returns results:
    ```sql
    SELECT COUNT(*) FROM ukraine_tweets_sentiment
    ```

### PostgreSQL Metadata

-   [ ] `pipeline_metadata` table exists
-   [ ] Table has execution records
-   [ ] Status is SUCCESS

## Visualization Checklist

### Superset Configuration

-   [ ] Druid database connection configured
-   [ ] Connection test successful
-   [ ] Dataset `ukraine_tweets_sentiment` accessible
-   [ ] Columns visible in dataset

### Dashboard Creation

-   [ ] Manual dashboard created OR
-   [ ] Automated script executed (`create_dashboard.py`)
-   [ ] Charts display data
-   [ ] No errors in chart rendering
-   [ ] Filters working

### Example Queries

-   [ ] Sentiment distribution query works
-   [ ] Time series query works
-   [ ] Location-based query works
-   [ ] Aggregations return correct results

## Governance Checklist (Optional)

### OpenMetadata Setup

-   [ ] UI accessible
-   [ ] Admin login successful
-   [ ] Services menu accessible

### Service Connections

-   [ ] Airflow service added
-   [ ] Druid service added
-   [ ] Superset service added
-   [ ] PostgreSQL service added

### Metadata Ingestion

-   [ ] Ingestion workflows created
-   [ ] Metadata successfully ingested
-   [ ] Lineage visible
-   [ ] Assets searchable

## Monitoring Checklist

### Resource Usage

-   [ ] CPU usage acceptable (<80%)
-   [ ] Memory usage acceptable (<80%)
-   [ ] Disk space sufficient (>5GB free)
-   [ ] No container OOM errors

### Logs Review

-   [ ] No ERROR messages in Airflow logs
-   [ ] No exceptions in Spark logs
-   [ ] Druid ingestion logs clean
-   [ ] PostgreSQL logs normal

### Performance

-   [ ] Spark job completes in reasonable time
-   [ ] Druid queries respond quickly (<2s)
-   [ ] Superset dashboards load fast (<5s)
-   [ ] No timeout errors

## Troubleshooting Checklist

If issues arise:

-   [ ] Check service logs (`docker-compose logs <service>`)
-   [ ] Verify .env file has correct keys
-   [ ] Ensure data file is in correct location
-   [ ] Check Docker resource limits
-   [ ] Verify no port conflicts
-   [ ] Restart problematic services
-   [ ] Review TROUBLESHOOTING.md
-   [ ] Check GitHub issues

## Post-Deployment Checklist

### Documentation

-   [ ] README.md reviewed
-   [ ] Team members can access services
-   [ ] Credentials documented (securely)
-   [ ] Architecture understood

### Backup

-   [ ] Important data backed up
-   [ ] Docker volumes identified
-   [ ] Backup strategy defined

### Maintenance

-   [ ] Log rotation configured
-   [ ] Disk space monitoring set up
-   [ ] Update schedule defined
-   [ ] Incident response plan created

## Production Readiness Checklist

For production deployment:

-   [ ] Change all default passwords
-   [ ] Enable SSL/TLS
-   [ ] Configure authentication
-   [ ] Set up monitoring (Prometheus/Grafana)
-   [ ] Implement alerting
-   [ ] Configure backup/recovery
-   [ ] Set resource limits
-   [ ] Enable audit logging
-   [ ] Implement RBAC
-   [ ] Security scan containers
-   [ ] Load testing completed
-   [ ] Disaster recovery tested

## Success Criteria

✅ **Deployment Successful If:**

1. All 14 containers running
2. All web UIs accessible
3. Airflow DAG executes successfully
4. Druid contains processed data
5. Superset displays dashboards
6. No critical errors in logs
7. Pipeline can be re-run
8. Data is queryable

## Next Steps After Deployment

1. **Schedule Pipeline**

    - Set DAG to run daily
    - Configure email alerts
    - Monitor execution

2. **Create More Dashboards**

    - Build custom visualizations
    - Share with stakeholders
    - Iterate based on feedback

3. **Extend Pipeline**

    - Add more data sources
    - Implement additional ML models
    - Create new metrics

4. **Optimize Performance**

    - Tune Spark parameters
    - Optimize Druid segments
    - Cache frequent queries

5. **Scale Infrastructure**
    - Add Spark workers
    - Increase Druid capacity
    - Deploy to cloud/K8s

---

## Checklist Summary

```
□ Pre-Deployment (10 items)
□ Build (5 items)
□ Deployment (10 items)
□ Service Access (10 items)
□ Pipeline Execution (10 items)
□ Data Verification (8 items)
□ Visualization (8 items)
□ Governance (8 items)
□ Monitoring (8 items)
□ Troubleshooting (8 items)
□ Post-Deployment (8 items)
□ Production Readiness (14 items)
```

**Total: 107 checkpoint items**

---

**Use this checklist to ensure nothing is missed during deployment!**

Print this file or keep it open while deploying the pipeline.
