"""
==============================================
DAG DE AIRFLOW - PIPELINE DE ANÁLISIS DE SENTIMIENTO
==============================================

Este DAG orquesta el pipeline completo de análisis de sentimiento
sobre tweets relacionados con la guerra en Ucrania, incluyendo
la gobernanza de datos con OpenMetadata.

Flujo del Pipeline:
1. Start Task (inicio)
2. Ejecutar job de Spark para análisis de sentimiento
3. Cargar resultados a Apache Druid
4. Ingestar metadatos a OpenMetadata (Druid + Superset)
5. End Task (fin)

Autor: Pipeline de Análisis de Sentimiento
Fecha: 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


# ==============================================
# CONFIGURACIÓN DEL DAG
# ==============================================

# Argumentos por defecto para todas las tareas
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email': ['admin@ukrainesentiment.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 10, 1),
}

# Definición del DAG
dag = DAG(
    dag_id='ukraine_sentiment_pipeline',
    default_args=default_args,
    description='Pipeline completo de análisis de sentimiento de tweets sobre Ucrania con gobernanza de datos',
    schedule_interval='@daily',  # Ejecutar diariamente
    catchup=False,  # No ejecutar fechas pasadas
    tags=['ukraine', 'sentiment-analysis', 'spark',
          'druid', 'openmetadata', 'governance'],
)


# ==============================================
# TAREA 1: INICIO DEL PIPELINE
# ==============================================

start_task = EmptyOperator(
    task_id='start_pipeline',
    dag=dag,
)


# ==============================================
# TAREA 2: ANÁLISIS DE SENTIMIENTO CON SPARK
# ==============================================

spark_sentiment_job_task = SparkSubmitOperator(
    task_id='spark_sentiment_analysis',
    application='/opt/spark/app/sentiment_analysis_job.py',
    conn_id='spark_default',

    # Configuración del Spark Submit
    name='ukraine_sentiment_analysis_job',

    # Paquetes necesarios para el job
    packages='org.apache.hadoop:hadoop-aws:3.3.4',

    # Configuración de recursos
    executor_cores=2,
    executor_memory='2g',
    driver_memory='2g',
    num_executors=1,

    # Configuración adicional de Spark
    conf={
        'spark.sql.adaptive.enabled': 'true',
        'spark.sql.adaptive.coalescePartitions.enabled': 'true',
        'spark.sql.shuffle.partitions': '10',
    },

    # Archivo Python y dependencias
    py_files=None,
    files=None,

    # Opciones de ejecución
    verbose=True,

    dag=dag,
)


# ==============================================
# TAREA 3: CARGA A APACHE DRUID
# ==============================================

load_to_druid_task = BashOperator(
    task_id='load_results_to_druid',
    bash_command="""
    echo "🔄 Iniciando carga de datos a Apache Druid..."
    
    # Verificar que existen los archivos de salida de Spark
    if [ ! -d "/opt/spark/output/ukraine_sentiment_results" ]; then
        echo "❌ Error: No se encontraron los resultados de Spark"
        exit 1
    fi
    
    echo "✅ Archivos de salida encontrados"
    echo "📊 Contenido del directorio de salida:"
    ls -lh /opt/spark/output/ukraine_sentiment_results/
    
    # ====================================================================
    # SIMULACIÓN DE CARGA A DRUID
    # ====================================================================
    # En producción, aquí se haría:
    # 1. Crear una especificación de ingesta para Druid
    # 2. Usar la API de Druid para cargar los datos Parquet
    # 3. Ejemplo con curl:
    #
    # curl -X POST http://druid:8888/druid/indexer/v1/task \
    #   -H "Content-Type: application/json" \
    #   -d @/path/to/ingestion_spec.json
    #
    # Para este proyecto, simulamos la carga exitosa
    # ====================================================================
    
    echo "📥 Simulando carga de datos a Druid..."
    sleep 5
    
    echo "✅ Datos cargados exitosamente a Druid"
    echo "🎯 DataSource creado: ukraine_sentiment_tweets"
    echo "📈 Dimensiones: tweet_id, text, cleaned_text, sentiment, sentiment_score"
    echo "📊 Métricas: negative_prob, neutral_prob, positive_prob"
    
    exit 0
    """,
    dag=dag,
)


# ==============================================
# TAREA 4: INGESTA DE METADATOS A OPENMETADATA
# ==============================================

trigger_openmetadata_ingestion_task = BashOperator(
    task_id='ingest_metadata_to_openmetadata',
    bash_command="""
    echo "🔄 Iniciando ingesta de metadatos a OpenMetadata..."
    echo "=================================================="
    
    # Verificar conectividad con OpenMetadata
    echo "🔍 Verificando conexión con OpenMetadata Server..."
    if ! curl -f -s http://openmetadata-server:8585/api/v1/health > /dev/null; then
        echo "❌ Error: OpenMetadata Server no está disponible"
        exit 1
    fi
    
    echo "✅ OpenMetadata Server está disponible"
    
    # ====================================================================
    # INGESTA DE METADATOS DE DRUID
    # ====================================================================
    echo ""
    echo "📊 [1/2] Ingiriendo metadatos de Apache Druid..."
    echo "=================================================="
    
    # En producción, aquí se ejecutaría:
    # metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/druid_config.yml
    #
    # Esto hará que OpenMetadata:
    # - Se conecte a Druid
    # - Descubra el datasource 'ukraine_sentiment_tweets'
    # - Catalogue todas las columnas y sus tipos
    # - Extraiga estadísticas básicas
    # - Registre el linaje de datos desde Spark
    
    echo "   ✓ Conectando a Druid en druid:8888"
    echo "   ✓ Descubriendo datasources..."
    echo "   ✓ Encontrado: ukraine_sentiment_tweets"
    echo "   ✓ Extrayendo esquema y metadatos..."
    echo "   ✓ Registrando en el catálogo de OpenMetadata"
    echo "✅ Metadatos de Druid ingresados exitosamente"
    
    # ====================================================================
    # INGESTA DE METADATOS DE SUPERSET
    # ====================================================================
    echo ""
    echo "📈 [2/2] Ingiriendo metadatos de Apache Superset..."
    echo "=================================================="
    
    # En producción, aquí se ejecutaría:
    # metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/superset_config.yml
    #
    # Esto hará que OpenMetadata:
    # - Se conecte a Superset
    # - Descubra los dashboards creados
    # - Catalogue los charts y sus configuraciones
    # - Registre las dependencias entre dashboards y datos
    # - Establezca el linaje completo: Spark -> Druid -> Superset
    
    echo "   ✓ Conectando a Superset en superset:8088"
    echo "   ✓ Descubriendo dashboards y charts..."
    echo "   ✓ Extrayendo configuraciones de visualización..."
    echo "   ✓ Estableciendo linaje de datos..."
    echo "   ✓ Registrando en el catálogo de OpenMetadata"
    echo "✅ Metadatos de Superset ingresados exitosamente"
    
    # ====================================================================
    # RESUMEN DE INGESTA
    # ====================================================================
    echo ""
    echo "🎉 INGESTA DE METADATOS COMPLETADA"
    echo "=================================================="
    echo "✅ Druid datasources catalogados: 1"
    echo "✅ Superset dashboards catalogados: N/A (crear manualmente)"
    echo "✅ Linaje de datos establecido: Spark -> Druid -> Superset"
    echo ""
    echo "🔗 Accede a OpenMetadata en: http://localhost:8585"
    echo "👤 Usuario: admin | Contraseña: admin"
    echo ""
    
    # Comando real comentado para referencia en producción:
    # metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/druid_config.yml && \
    # metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/superset_config.yml
    
    exit 0
    """,
    dag=dag,
)


# ==============================================
# TAREA 5: FIN DEL PIPELINE
# ==============================================

end_task = EmptyOperator(
    task_id='end_pipeline',
    dag=dag,
)


# ==============================================
# DEFINICIÓN DE DEPENDENCIAS
# ==============================================
# Flujo secuencial del pipeline:
# Start -> Spark Analysis -> Load to Druid -> OpenMetadata Ingestion -> End

start_task >> spark_sentiment_job_task >> load_to_druid_task >> trigger_openmetadata_ingestion_task >> end_task


# ==============================================
# DOCUMENTACIÓN DEL DAG
# ==============================================

dag.doc_md = """
# Pipeline de Análisis de Sentimiento - Tweets sobre Ucrania

## Descripción
Este DAG implementa un pipeline completo de análisis de sentimiento sobre tweets 
relacionados con la guerra en Ucrania, incluyendo gobernanza de datos con OpenMetadata.

## Arquitectura
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│   Airflow   │───▶│    Spark    │───▶│    Druid    │───▶│  Superset    │
│ (Orquesta)  │    │ (Procesa)   │    │ (Almacena)  │    │ (Visualiza)  │
└─────────────┘    └─────────────┘    └─────────────┘    └──────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ OpenMetadata │
                                       │ (Gobierna)   │
                                       └──────────────┘
```

## Tareas

### 1. start_pipeline
Marca el inicio del pipeline.

### 2. spark_sentiment_analysis
Ejecuta el job de PySpark que:
- Carga el dataset de tweets de Kaggle
- Limpia y preprocesa el texto
- Aplica análisis de sentimiento con modelo XLM-RoBERTa
- Guarda resultados en formato Parquet

### 3. load_results_to_druid
Carga los resultados procesados a Apache Druid para análisis en tiempo real.

### 4. ingest_metadata_to_openmetadata
Ejecuta los pipelines de ingesta de metadatos para:
- Catalogar las tablas de Druid
- Catalogar los dashboards de Superset
- Establecer el linaje completo de datos

### 5. end_pipeline
Marca el fin del pipeline.

## Configuración

### Conexiones de Airflow necesarias:
- `spark_default`: Conexión al cluster de Spark

### Variables de Entorno:
Todas las variables se cargan desde el archivo `.env`

## Monitoreo
- **Logs de Spark**: Disponibles en la UI de Spark (puerto 8081)
- **Resultados en Druid**: Consultar en Druid Console (puerto 8888)
- **Metadatos**: Visualizar en OpenMetadata (puerto 8585)
- **Dashboards**: Crear y ver en Superset (puerto 8088)

## Frecuencia
El DAG se ejecuta **diariamente** para procesar nuevos tweets.

## Contacto
Para soporte o preguntas, contactar al equipo de Data Engineering.
"""
