# ==============================================
# DOCKERFILE PERSONALIZADO PARA AIRFLOW
# ==============================================
# Extiende la imagen oficial de Airflow para incluir:
# 1. Cliente de OpenMetadata para ingesta de metadatos
# 2. Dependencias adicionales para análisis de sentimiento
# 3. Conectores para Spark, Druid y Superset

FROM apache/airflow:2.7.3-python3.10

# Cambiar a usuario root para instalar dependencias del sistema
USER root

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Volver al usuario airflow
USER airflow

# Instalar el cliente de OpenMetadata con soporte para Airflow
# Esto permite ejecutar pipelines de ingesta de metadatos desde DAGs de Airflow
# NOTE: Removed openmetadata-ingestion to avoid provider conflicts
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.3.0 \
    apache-airflow-providers-postgres==5.7.1 \
    psycopg2-binary==2.9.9 \
    pyspark==3.5.0 \
    pandas==2.1.3 \
    transformers==4.35.2 \
    torch==2.1.1 \
    kaggle==1.5.16

# Crear directorios necesarios
RUN mkdir -p /opt/airflow/openmetadata/ingestion_configs

# Configuración de Kaggle
ENV KAGGLE_CONFIG_DIR=/opt/airflow/.kaggle

WORKDIR /opt/airflow
