# 🚀 Quick Reference Card

## 📁 Project Structure at a Glance

```
ukraine-tweets-sentiment-analysis/
│
├── 📖 README.md                           ← Start here!
├── 🔧 docker-compose.yml                  ← Services config
├── ⚙️ .env                                ← Environment vars
│
├── 📚 docs/                               ← All documentation
│   ├── QUICKSTART.md                      ← Step-by-step tutorial
│   ├── SUPERSET_CONNECTION_GUIDE.md      ← ⭐ Visualization setup
│   ├── TROUBLESHOOTING.md                ← Common issues
│   ├── ARCHITECTURE.md                    ← System design
│   └── INDEX.md                           ← Doc navigation
│
├── 🛠️ tools/                              ← Utility scripts
│   ├── data_preparation/                  ← Data sampling
│   │   ├── create_sample_100.py          ← Quick test (100 rows)
│   │   └── download_dataset.py           ← Full dataset
│   │
│   ├── database_loaders/                  ← Load to DB
│   │   └── load_to_postgres_sqlalchemy.py ← ⭐ Use this!
│   │
│   └── diagnostics/                       ← Monitoring
│       ├── verify_postgres.py            ← Check data
│       └── view_results.py               ← View results
│
├── ⚙️ config/                             ← Configuration
├── 🔄 airflow/                            ← Airflow DAGs
├── ⚡ spark/                              ← Spark jobs
├── 📊 superset/                           ← Superset config
├── 📂 data/                               ← Data storage
└── 🔧 scripts/                            ← Setup scripts
```

## ⚡ Common Commands

### Quick Start (100-row test)

```bash
# 1. Create test sample
python tools/data_preparation/create_sample_100.py

# 2. Start services
docker-compose up -d

# 3. Run pipeline (Airflow UI: http://localhost:8080)
# Enable and trigger: twitter_sentiment_pipeline

# 4. Load results
python tools/database_loaders/load_to_postgres_sqlalchemy.py

# 5. Verify
python tools/diagnostics/verify_postgres.py

# 6. Visualize (Superset: http://localhost:8088)
# Follow: docs/SUPERSET_CONNECTION_GUIDE.md
```

### Docker Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]

# Check status
docker-compose ps
```

### Data Operations

```bash
# Create 100-row sample (testing)
python tools/data_preparation/create_sample_100.py

# Create custom sample
python tools/data_preparation/create_sample_dataset.py

# Download full dataset
python tools/data_preparation/download_dataset.py
```

### Database Operations

```bash
# Load to PostgreSQL (recommended)
python tools/database_loaders/load_to_postgres_sqlalchemy.py

# Verify data
python tools/diagnostics/verify_postgres.py

# View results
python tools/diagnostics/view_results.py
```

### Monitoring

```bash
# Monitor pipeline
python tools/diagnostics/monitor_pipeline.py

# Check Druid
python tools/diagnostics/check_druid_data.py
```

## 🌐 Service URLs

| Service      | URL                   | Login             |
| ------------ | --------------------- | ----------------- |
| **Airflow**  | http://localhost:8080 | airflow / airflow |
| **Spark**    | http://localhost:8081 | -                 |
| **Druid**    | http://localhost:8888 | -                 |
| **Superset** | http://localhost:8088 | admin / admin     |

## 🎯 Workflow Paths

### New User Path

```
README.md
  ↓
docs/QUICKSTART.md
  ↓
tools/data_preparation/create_sample_100.py
  ↓
Airflow UI (run pipeline)
  ↓
tools/database_loaders/load_to_postgres_sqlalchemy.py
  ↓
docs/SUPERSET_CONNECTION_GUIDE.md
  ↓
Superset (create dashboards)
```

### Troubleshooting Path

```
Issue occurs
  ↓
docs/TROUBLESHOOTING.md
  ↓
docker-compose logs -f [service]
  ↓
tools/diagnostics/ (verify data)
  ↓
Solution found
```

### Scaling to Production

```
Test with 100 rows (works)
  ↓
tools/data_preparation/download_dataset.py
  ↓
Update DAG (use full dataset)
  ↓
Increase Docker resources
  ↓
Run full pipeline
  ↓
Load to PostgreSQL
  ↓
Production dashboards
```

## 📚 Documentation Quick Links

| Need                        | Document                            |
| --------------------------- | ----------------------------------- |
| **Getting started**         | `README.md`                         |
| **Step-by-step tutorial**   | `docs/QUICKSTART.md`                |
| **Visualize data**          | `docs/SUPERSET_CONNECTION_GUIDE.md` |
| **Fix issues**              | `docs/TROUBLESHOOTING.md`           |
| **Understand architecture** | `docs/ARCHITECTURE.md`              |
| **Tool reference**          | `tools/README.md`                   |
| **Migration help**          | `MIGRATION_GUIDE.md`                |
| **Browse all docs**         | `docs/INDEX.md`                     |

## 🔑 Key Files

| File                                     | Purpose               |
| ---------------------------------------- | --------------------- |
| `docker-compose.yml`                     | Service definitions   |
| `.env`                                   | Environment variables |
| `airflow/dags/twitter_sentiment_dag.py`  | Pipeline definition   |
| `spark/sentiment_analysis.py`            | Analysis job          |
| `data/raw/ukraine_tweets_sample_100.csv` | Test data             |
| `data/processed/sentiment_results/*.csv` | Results               |

## 🚨 Emergency Commands

### Services won't start

```bash
docker-compose down -v    # Nuclear option (⚠️ deletes data!)
docker-compose up -d      # Fresh start
```

### Pipeline fails

```bash
# Check Airflow logs
docker-compose logs -f airflow-scheduler

# Check specific task in Airflow UI
# http://localhost:8080 → DAG → Task → Log
```

### Can't connect to database

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Verify it's running
docker-compose ps | grep postgres
```

### Out of memory

```bash
# Increase Docker memory (Docker Desktop → Settings → Resources)
# Minimum: 8GB RAM, 4 CPUs
```

## 💡 Pro Tips

1. **Start small**: Use 100-row sample first
2. **Check logs**: `docker-compose logs -f [service]`
3. **Use recommended tools**: Look for ⭐ markers
4. **Follow guides**: Docs are comprehensive
5. **Monitor progress**: Use Airflow UI
6. **Verify each step**: Use diagnostic tools

## 🎓 Learning Path

```
Day 1: Setup & 100-row test
  - Read README.md
  - Follow QUICKSTART.md
  - Run pipeline with sample

Day 2: Visualization
  - Load to PostgreSQL
  - Connect Superset
  - Create first chart

Day 3: Scale up
  - Larger sample (1K-10K rows)
  - Optimize performance
  - Create dashboard

Day 4+: Production
  - Full dataset
  - Advanced visualizations
  - Monitoring setup
```

---

**Quick Help**: Check `docs/TROUBLESHOOTING.md` or `docs/INDEX.md`
