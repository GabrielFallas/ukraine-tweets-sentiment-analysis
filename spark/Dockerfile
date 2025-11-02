FROM apache/spark:3.5.0-python3

USER root

# Install Python dependencies compatible with Python 3.8
RUN pip install --no-cache-dir \
    transformers==4.35.2 \
    torch==2.1.1 \
    pandas==2.0.3 \
    pyarrow==14.0.1 \
    scikit-learn==1.3.2 \
    psycopg2-binary==2.9.9 \
    requests==2.31.0

# Create directories
RUN mkdir -p /opt/spark-apps /opt/spark-data

# Set permissions
RUN chmod -R 777 /opt/spark-apps /opt/spark-data

USER 1001

WORKDIR /opt/spark-apps
