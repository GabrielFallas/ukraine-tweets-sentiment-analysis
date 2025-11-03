FROM python:3.11-slim

USER root

# Install Java and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    wget \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"
ENV PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.9.7-src.zip:${PYTHONPATH}"

RUN wget -q "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" && \
    tar -xzf "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" && \
    mv "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" "${SPARK_HOME}" && \
    rm "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"

# Install Python dependencies
RUN pip install --no-cache-dir \
    transformers==4.35.2 \
    torch==2.1.1 \
    pandas==2.1.3 \
    pyarrow==14.0.1 \
    scikit-learn==1.3.2 \
    psycopg2-binary==2.9.9 \
    requests==2.31.0 \
    pyspark==3.5.0

# Create directories
RUN mkdir -p /opt/spark-apps /opt/airflow/data

# Set permissions
RUN chmod -R 777 /opt/spark-apps /opt/airflow/data "${SPARK_HOME}"

WORKDIR /opt/spark-apps
