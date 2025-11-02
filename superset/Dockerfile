FROM apache/superset:3.0.3

USER root

# Install additional dependencies
RUN pip install --no-cache-dir \
    pydruid==0.6.5 \
    psycopg2-binary==2.9.9

USER superset

WORKDIR /app
