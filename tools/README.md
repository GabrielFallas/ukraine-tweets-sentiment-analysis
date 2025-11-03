# 🛠️ Tools Directory

This directory contains utility scripts organized by function.

## 📂 Directory Structure

```
tools/
├── data_preparation/      # Data sampling and preparation
├── database_loaders/      # Load results to databases
└── diagnostics/           # Monitoring and debugging
```

## 📊 Data Preparation

Location: `tools/data_preparation/`

### create_sample_100.py

**Purpose**: Create a 100-row sample for quick testing

```bash
python tools/data_preparation/create_sample_100.py
```

**Output**: `data/raw/ukraine_tweets_sample_100.csv` (72KB)

**Use when**: First-time setup, quick pipeline verification

---

### create_sample_dataset.py

**Purpose**: Create custom-sized samples using reservoir sampling

```bash
python tools/data_preparation/create_sample_dataset.py
```

**Parameters**: Edit script to change sample size (default: 70,000)

**Output**: `data/raw/ukraine_tweets_sample.csv`

**Use when**: Testing with larger datasets, performance tuning

---

### download_dataset.py

**Purpose**: Download full dataset from Kaggle

```bash
python tools/data_preparation/download_dataset.py
```

**Requirements**:

-   Kaggle API credentials
-   ~50GB free space

**Use when**: Production deployment, full-scale analysis

---

### create_mock_data.py

**Purpose**: Generate synthetic test data

```bash
python tools/data_preparation/create_mock_data.py
```

**Use when**: Testing without real data, development

---

## 💾 Database Loaders

Location: `tools/database_loaders/`

### load_to_postgres_sqlalchemy.py ⭐ **RECOMMENDED**

**Purpose**: Load sentiment results to PostgreSQL using SQLAlchemy

```bash
python tools/database_loaders/load_to_postgres_sqlalchemy.py
```

**Features**:

-   Automatic type conversion
-   Handles NaN values
-   Creates indexes
-   Shows data summary

**Requirements**:

-   `pandas`, `sqlalchemy` installed
-   PostgreSQL running on localhost:5432

**Output**: Table `ukraine_tweets_sentiment` in PostgreSQL

---

### load_to_postgres_direct.py

**Purpose**: Direct insertion using psycopg2

```bash
python tools/database_loaders/load_to_postgres_direct.py
```

**Use when**: SQLAlchemy method fails, need more control

---

### load_to_postgres_fixed.py

**Purpose**: Alternative method with CSV cleaning

```bash
python tools/database_loaders/load_to_postgres_fixed.py
```

**Use when**: CSV has formatting issues

---

### load_to_postgres_simple.py

**Purpose**: Simple Docker cp + psql COPY method

```bash
python tools/database_loaders/load_to_postgres_simple.py
```

**Use when**: Other methods fail, maximum simplicity needed

---

## 🔍 Diagnostics

Location: `tools/diagnostics/`

### verify_postgres.py

**Purpose**: Check if data loaded successfully to PostgreSQL

```bash
python tools/diagnostics/verify_postgres.py
```

**Output**:

```
Sentiment Distribution:
  NEGATIVE: 74 tweets
  POSITIVE: 19 tweets
  None: 8 tweets

Total: 101 tweets
```

**Use when**: After loading data, before creating visualizations

---

### view_results.py

**Purpose**: Display sentiment analysis results from CSV

```bash
python tools/diagnostics/view_results.py
```

**Shows**:

-   Total tweets processed
-   Sentiment distribution
-   Sample tweets for each sentiment

**Use when**: Want to preview results without database

---

### monitor_pipeline.py

**Purpose**: Monitor Airflow DAG execution

```bash
python tools/diagnostics/monitor_pipeline.py
```

**Shows**:

-   DAG run status
-   Task completion
-   Execution times
-   Failures (if any)

**Use when**: Pipeline is running, debugging issues

---

### check_druid_data.py

**Purpose**: Verify data in Apache Druid

```bash
python tools/diagnostics/check_druid_data.py
```

**Use when**: Using Druid for analytics (alternative to PostgreSQL)

---

### diagnose_druid_connection.py

**Purpose**: Comprehensive Druid connectivity diagnostics

```bash
python tools/diagnostics/diagnose_druid_connection.py
```

**Checks**:

-   Broker availability
-   SQL endpoint
-   Available datasources
-   Data segments
-   Schema information

**Use when**: Troubleshooting Druid connection issues

---

## 🔄 Common Workflows

### First-Time Setup

```bash
# 1. Create test sample
python tools/data_preparation/create_sample_100.py

# 2. Run pipeline (via Airflow UI)

# 3. Load results
python tools/database_loaders/load_to_postgres_sqlalchemy.py

# 4. Verify
python tools/diagnostics/verify_postgres.py
```

### Scaling to Production

```bash
# 1. Download full dataset
python tools/data_preparation/download_dataset.py

# 2. Update DAG to use full dataset
# Edit: airflow/dags/twitter_sentiment_dag.py line 35

# 3. Run pipeline (via Airflow UI)

# 4. Load results
python tools/database_loaders/load_to_postgres_sqlalchemy.py
```

### Troubleshooting Pipeline

```bash
# 1. Check pipeline status
python tools/diagnostics/monitor_pipeline.py

# 2. View results if completed
python tools/diagnostics/view_results.py

# 3. Verify database
python tools/diagnostics/verify_postgres.py
```

### Testing with Different Sample Sizes

```bash
# Small (100 rows) - ~30 seconds
python tools/data_preparation/create_sample_100.py

# Medium (1,000 rows) - ~2 minutes
# Edit create_sample_dataset.py, set sample_size=1000
python tools/data_preparation/create_sample_dataset.py

# Large (100,000 rows) - ~20 minutes
# Edit create_sample_dataset.py, set sample_size=100000
python tools/data_preparation/create_sample_dataset.py
```

## 📦 Dependencies

### Python Packages Required

For data preparation:

```bash
pip install pandas
```

For database loaders:

```bash
pip install pandas sqlalchemy psycopg2-binary
```

For diagnostics:

```bash
pip install pandas requests sqlalchemy
```

Install all:

```bash
pip install pandas sqlalchemy psycopg2-binary requests
```

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Install missing packages
pip install pandas sqlalchemy psycopg2-binary requests
```

### "Connection refused" to PostgreSQL

```bash
# Check if PostgreSQL container is running
docker-compose ps | grep postgres

# Restart PostgreSQL if needed
docker-compose restart postgres
```

### CSV file not found

```bash
# Check if sample exists
ls data/raw/ukraine_tweets_sample_100.csv

# Create it if missing
python tools/data_preparation/create_sample_100.py
```

### "No data in database"

```bash
# Verify pipeline completed in Airflow UI
# Then run loader
python tools/database_loaders/load_to_postgres_sqlalchemy.py
```

## 📝 Adding New Tools

When adding a new tool:

1. Place in appropriate subdirectory:

    - Data prep → `data_preparation/`
    - Database loading → `database_loaders/`
    - Monitoring/debugging → `diagnostics/`

2. Include clear docstring:

```python
"""
Tool Name: what_it_does.py
Purpose: Brief description
Usage: python tools/category/what_it_does.py
Requirements: List dependencies
"""
```

3. Update this README with:

    - Tool name and purpose
    - Usage example
    - Expected output
    - When to use

4. Add entry to main [docs/INDEX.md](../docs/INDEX.md)

---

**Quick Links:**

-   📖 [Main Documentation](../docs/INDEX.md)
-   🏠 [Project README](../README.md)
-   🚀 [Quick Start Guide](../docs/QUICKSTART.md)
