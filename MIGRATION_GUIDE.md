# 📦 Project Refactoring - Migration Guide

The project structure has been reorganized for better clarity and maintainability.

## 🔄 What Changed

### File Relocations

#### Documentation (→ `docs/`)

| Old Location                   | New Location                        |
| ------------------------------ | ----------------------------------- |
| `ARCHITECTURE.md`              | `docs/ARCHITECTURE.md`              |
| `INDEX.md`                     | `docs/INDEX.md`                     |
| `PROJECT_STRUCTURE.md`         | `docs/PROJECT_STRUCTURE.md`         |
| `SUMMARY.md`                   | `docs/SUMMARY.md`                   |
| `VISUAL_OVERVIEW.md`           | `docs/VISUAL_OVERVIEW.md`           |
| `TROUBLESHOOTING.md`           | `docs/TROUBLESHOOTING.md`           |
| `QUICKSTART.md`                | `docs/QUICKSTART.md`                |
| `CHECKLIST.md`                 | `docs/CHECKLIST.md`                 |
| `SUPERSET_CONNECTION_GUIDE.md` | `docs/SUPERSET_CONNECTION_GUIDE.md` |
| `SUPERSET_SETUP.md`            | `docs/SUPERSET_SETUP.md`            |
| `CONNECT_SUPERSET_TO_DRUID.md` | `docs/CONNECT_SUPERSET_TO_DRUID.md` |

#### Data Preparation (→ `tools/data_preparation/`)

| Old Location               | New Location                                      |
| -------------------------- | ------------------------------------------------- |
| `create_sample_100.py`     | `tools/data_preparation/create_sample_100.py`     |
| `create_sample_dataset.py` | `tools/data_preparation/create_sample_dataset.py` |
| `create_mock_data.py`      | `tools/data_preparation/create_mock_data.py`      |
| `download_dataset.py`      | `tools/data_preparation/download_dataset.py`      |

#### Database Loaders (→ `tools/database_loaders/`)

| Old Location                     | New Location                                            |
| -------------------------------- | ------------------------------------------------------- |
| `load_to_postgres_sqlalchemy.py` | `tools/database_loaders/load_to_postgres_sqlalchemy.py` |
| `load_to_postgres_direct.py`     | `tools/database_loaders/load_to_postgres_direct.py`     |
| `load_to_postgres_fixed.py`      | `tools/database_loaders/load_to_postgres_fixed.py`      |
| `load_to_postgres_simple.py`     | `tools/database_loaders/load_to_postgres_simple.py`     |
| `load_results_to_postgres.py`    | `tools/database_loaders/load_results_to_postgres.py`    |

#### Diagnostics (→ `tools/diagnostics/`)

| Old Location                   | New Location                                     |
| ------------------------------ | ------------------------------------------------ |
| `check_druid_data.py`          | `tools/diagnostics/check_druid_data.py`          |
| `diagnose_druid_connection.py` | `tools/diagnostics/diagnose_druid_connection.py` |
| `verify_postgres.py`           | `tools/diagnostics/verify_postgres.py`           |
| `view_results.py`              | `tools/diagnostics/view_results.py`              |
| `monitor_pipeline.py`          | `tools/diagnostics/monitor_pipeline.py`          |

#### Configuration (→ `config/`)

| Old Location       | New Location              |
| ------------------ | ------------------------- |
| `generate_keys.py` | `config/generate_keys.py` |

#### Scripts (→ `scripts/`)

| Old Location     | New Location             |
| ---------------- | ------------------------ |
| `query_druid.sh` | `scripts/query_druid.sh` |

## 📁 New Directory Structure

```
ukraine-tweets-sentiment-analysis/
├── 📂 docs/                      # 📚 All documentation
├── 📂 tools/                     # 🛠️ Utility scripts
│   ├── data_preparation/         # Data sampling tools
│   ├── database_loaders/         # Database loading scripts
│   └── diagnostics/              # Monitoring & debugging
├── 📂 config/                    # ⚙️ Configuration utilities
├── 📂 airflow/                   # Airflow components (unchanged)
├── 📂 spark/                     # Spark jobs (unchanged)
├── 📂 superset/                  # Superset config (unchanged)
├── 📂 scripts/                   # Setup scripts (unchanged)
└── 📂 data/                      # Data storage (unchanged)
```

## 🔧 Updating Your Workflow

### If you have scripts or aliases

**Before:**

```bash
python create_sample_100.py
python load_to_postgres_sqlalchemy.py
python verify_postgres.py
```

**After:**

```bash
python tools/data_preparation/create_sample_100.py
python tools/database_loaders/load_to_postgres_sqlalchemy.py
python tools/diagnostics/verify_postgres.py
```

### If you reference documentation

**Before:**

```
See SUPERSET_CONNECTION_GUIDE.md
See TROUBLESHOOTING.md
```

**After:**

```
See docs/SUPERSET_CONNECTION_GUIDE.md
See docs/TROUBLESHOOTING.md
```

### If you have local modifications

1. **Check your local changes:**

    ```bash
    git status
    ```

2. **Stash or commit them:**

    ```bash
    git stash  # or git commit
    ```

3. **Pull the refactored structure:**

    ```bash
    git pull origin main
    ```

4. **Reapply your changes** to the new file locations

## ✅ Quick Migration Checklist

-   [ ] Update any custom scripts that reference old file paths
-   [ ] Update bookmarks/favorites for documentation pages
-   [ ] Update any README or documentation you added
-   [ ] Update any shell aliases or shortcuts
-   [ ] Test that your workflows still work:
    -   [ ] Data preparation
    -   [ ] Pipeline execution
    -   [ ] Database loading
    -   [ ] Diagnostics

## 🎯 Benefits of New Structure

### Before (Root Clutter)

-   ❌ 30+ files in root directory
-   ❌ Hard to find specific tools
-   ❌ Mixed documentation and code
-   ❌ No clear organization

### After (Organized)

-   ✅ Clean root directory
-   ✅ Tools grouped by purpose
-   ✅ All docs in one place
-   ✅ Clear hierarchy
-   ✅ Easier to navigate
-   ✅ Better for new contributors

## 🚀 Updated Common Commands

### Data Preparation

```bash
# Create test sample
python tools/data_preparation/create_sample_100.py

# Create custom sample
python tools/data_preparation/create_sample_dataset.py

# Download full dataset
python tools/data_preparation/download_dataset.py
```

### Database Operations

```bash
# Load results to PostgreSQL (recommended method)
python tools/database_loaders/load_to_postgres_sqlalchemy.py

# Verify data loaded
python tools/diagnostics/verify_postgres.py
```

### Monitoring & Debugging

```bash
# View results
python tools/diagnostics/view_results.py

# Monitor pipeline
python tools/diagnostics/monitor_pipeline.py

# Check Druid connection
python tools/diagnostics/diagnose_druid_connection.py
```

### Documentation

```bash
# Main README
cat README.md

# Documentation index
cat docs/INDEX.md

# Superset setup
cat docs/SUPERSET_CONNECTION_GUIDE.md

# Troubleshooting
cat docs/TROUBLESHOOTING.md
```

## 📝 No Code Changes Required!

**Important**: Docker services and core functionality are unchanged:

-   ✅ `docker-compose.yml` - Same
-   ✅ Airflow DAGs - Same
-   ✅ Spark jobs - Same
-   ✅ Service URLs - Same
-   ✅ Database schemas - Same

Only file locations changed, not functionality!

## 🆘 Having Issues?

### Scripts not found

```bash
# Old command fails:
python verify_postgres.py
# Error: No such file or directory

# Solution: Use new path
python tools/diagnostics/verify_postgres.py
```

### Documentation links broken

-   Check `docs/INDEX.md` for updated links
-   All documentation is now in `docs/` folder

### Need help?

-   See `docs/TROUBLESHOOTING.md`
-   Check `tools/README.md` for tool usage
-   Open an issue on GitHub

## 📚 Key Documentation

-   **[README.md](../README.md)** - Updated main README
-   **[docs/INDEX.md](docs/INDEX.md)** - Documentation index
-   **[tools/README.md](tools/README.md)** - Tools reference
-   **[docs/SUPERSET_CONNECTION_GUIDE.md](docs/SUPERSET_CONNECTION_GUIDE.md)** - Visualization setup

---

**Questions?** Check the documentation or open an issue!
