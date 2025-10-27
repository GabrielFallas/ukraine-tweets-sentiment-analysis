# 🇺🇦 Pipeline de Análisis de Sentimiento - Tweets sobre Ucrania

## 📋 Descripción

Pipeline de datos completo con **gobernanza de datos** para analizar el sentimiento de tweets sobre la guerra en Ucrania. Este proyecto implementa una arquitectura moderna de datos utilizando las mejores herramientas del ecosistema Big Data.

### 🎯 Características

-   ✅ **Orquestación**: Apache Airflow para gestión de workflows
-   ✅ **Procesamiento Distribuido**: Apache Spark para análisis de sentimiento con ML
-   ✅ **Almacenamiento Analítico**: Apache Druid para consultas en tiempo real
-   ✅ **Visualización**: Apache Superset para dashboards interactivos
-   ✅ **Gobernanza de Datos**: OpenMetadata para catalogación y linaje de datos
-   ✅ **Análisis de Sentimiento**: Modelo XLM-RoBERTa multilingüe de Hugging Face
-   ✅ **Arquitectura Containerizada**: Docker Compose para fácil despliegue

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE ORQUESTACIÓN                        │
│                          Apache Airflow                             │
│                     (Gestión de Workflows)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE PROCESAMIENTO                          │
│                          Apache Spark                               │
│              (Limpieza, Transformación, ML)                         │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐                     │
│  │  Limpieza de     │───▶│  Análisis de     │                     │
│  │  Texto           │    │  Sentimiento     │                     │
│  │  (Regex, NLP)    │    │  (XLM-RoBERTa)   │                     │
│  └──────────────────┘    └──────────────────┘                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAPA DE ALMACENAMIENTO                            │
│                         Apache Druid                                │
│              (Base de Datos Analítica OLAP)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE VISUALIZACIÓN                          │
│                        Apache Superset                              │
│                 (Dashboards y Reportes)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE GOBERNANZA                               │
│                        OpenMetadata                                 │
│        (Catalogación, Linaje, Calidad de Datos)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
ukraine-tweets-sentiment-analysis/
│
├── docker-compose.yml              # Definición de todos los servicios
├── .env                            # Variables de entorno y credenciales
│
├── airflow/
│   ├── Dockerfile                  # Imagen personalizada con OpenMetadata
│   └── dags/
│       └── ukraine_sentiment_pipeline_dag.py  # DAG principal
│
├── spark/
│   ├── app/
│   │   └── sentiment_analysis_job.py  # Script PySpark de análisis
│   └── data/
│       └── (coloca aquí ukraine_tweets.csv)
│
├── druid/
│   └── (configuraciones de Druid)
│
└── openmetadata/
    └── ingestion_configs/
        ├── druid_config.yml        # Config de ingesta de Druid
        └── superset_config.yml     # Config de ingesta de Superset
```

---

## 🚀 Inicio Rápido

### Prerrequisitos

-   **Docker** (versión 20.x o superior)
-   **Docker Compose** (versión 2.x o superior)
-   **8 GB RAM mínimo** (recomendado 16 GB)
-   **20 GB espacio en disco**

### 1. Clonar el Repositorio

```bash
git clone https://github.com/GabrielFallas/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis
```

### 2. Dataset Incluido ✅

El dataset ya está incluido en el repositorio en la carpeta `spark/data/ukraine-war-tweets/`.

-   **Archivos**: 50+ archivos CSV diarios (agosto-octubre 2022)
-   **Formato**: `MMDD_UkraineCombinedTweetsDeduped.csv`
-   **Tweets totales**: Miles de tweets únicos sobre la guerra en Ucrania
-   **Columnas principales**:
    -   `tweetid`, `text`, `tweetcreatedts`
    -   `username`, `location`, `language`
    -   `retweetcount`, `favorite_count`, `hashtags`

**No necesitas descargar nada adicional** - el dataset está listo para usarse.

### 3. Configurar Variables de Entorno

El archivo `.env` ya está configurado con valores predeterminados. **IMPORTANTE**: En producción, cambia todas las contraseñas.

```bash
# Revisar configuración
cat .env

# (Opcional) Modificar según necesites
nano .env
```

### 4. Levantar los Servicios

```bash
# Construir las imágenes personalizadas
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

⏱️ **Tiempo estimado de inicio**: 5-10 minutos (primera vez)

**Nota**: El dataset ya está incluido en `spark/data/ukraine-war-tweets/`, no necesitas descargarlo.

### 5. Verificar que los Servicios Estén Activos

```bash
# Verificar estado de contenedores
docker-compose ps

# Deberías ver 12 servicios running:
# - postgres_airflow_db
# - postgres_superset_db
# - postgres_openmetadata_db
# - elasticsearch
# - airflow-webserver
# - airflow-scheduler
# - spark-master
# - spark-worker
# - druid
# - superset
# - openmetadata-server
# - openmetadata-ingestion
```

---

## 🌐 Acceso a las Interfaces Web

Una vez que todos los servicios estén levantados:

| Servicio          | URL                   | Usuario | Contraseña | Puerto |
| ----------------- | --------------------- | ------- | ---------- | ------ |
| **Airflow**       | http://localhost:8080 | admin   | admin      | 8080   |
| **Spark UI**      | http://localhost:8081 | -       | -          | 8081   |
| **Superset**      | http://localhost:8088 | admin   | admin      | 8088   |
| **Druid Console** | http://localhost:8888 | -       | -          | 8888   |
| **OpenMetadata**  | http://localhost:8585 | admin   | admin      | 8585   |
| **Elasticsearch** | http://localhost:9200 | -       | -          | 9200   |

---

## 📊 Ejecutar el Pipeline

### Opción 1: Desde la UI de Airflow

1. Abrir Airflow en http://localhost:8080
2. Login con `admin` / `admin`
3. Buscar el DAG: `ukraine_sentiment_pipeline`
4. Activar el DAG (toggle switch)
5. Hacer clic en "Trigger DAG" (botón play ▶️)
6. Monitorear el progreso en la vista de "Graph" o "Tree"

### Opción 2: Desde la Línea de Comandos

```bash
# Ejecutar el DAG manualmente
docker exec -it airflow-webserver airflow dags trigger ukraine_sentiment_pipeline

# Ver logs del DAG
docker exec -it airflow-webserver airflow dags list

# Ver tareas del DAG
docker exec -it airflow-webserver airflow tasks list ukraine_sentiment_pipeline
```

### Flujo de Ejecución del Pipeline

```
1. ✅ start_pipeline
   └─▶ Inicia el workflow

2. ⚡ spark_sentiment_analysis
   └─▶ Carga datos
   └─▶ Limpia texto
   └─▶ Analiza sentimiento (XLM-RoBERTa)
   └─▶ Guarda en Parquet

3. 📥 load_results_to_druid
   └─▶ Ingesta datos a Druid
   └─▶ Crea datasource 'ukraine_sentiment_tweets'

4. 🏛️ ingest_metadata_to_openmetadata
   └─▶ Cataloga tablas de Druid
   └─▶ Cataloga dashboards de Superset
   └─▶ Establece linaje de datos

5. ✅ end_pipeline
   └─▶ Finaliza exitosamente
```

---

## 📈 Crear Visualizaciones en Superset

### 1. Conectar Druid a Superset

```bash
# Acceder a Superset
# http://localhost:8088

# 1. Ir a: Settings > Database Connections > + Database
# 2. Seleccionar: Apache Druid
# 3. Configurar:
#    - Display Name: Ukraine Druid
#    - SQLAlchemy URI: druid://druid:8888/druid/v2/sql
# 4. Test Connection
# 5. Save
```

### 2. Crear Dataset

1. Ir a: **Data > Datasets > + Dataset**
2. Seleccionar:
    - Database: `Ukraine Druid`
    - Schema: `druid`
    - Table: `ukraine_sentiment_tweets`
3. Click en **Create Dataset and Create Chart**

### 3. Crear Charts

#### Chart 1: Distribución de Sentimientos (Pie Chart)

-   Chart Type: **Pie Chart**
-   Dimensions: `sentiment`
-   Metric: `COUNT(*)`

#### Chart 2: Sentimientos por Fecha (Line Chart)

-   Chart Type: **Line Chart**
-   X-Axis: `processed_at` (temporal)
-   Metric: `COUNT(*)`
-   Group by: `sentiment`

#### Chart 3: Promedio de Scores (Bar Chart)

-   Chart Type: **Bar Chart**
-   X-Axis: `sentiment`
-   Metric: `AVG(sentiment_score)`

### 4. Crear Dashboard

1. Ir a: **Dashboards > + Dashboard**
2. Nombre: `Ukraine Sentiment Analysis`
3. Agregar los charts creados
4. Organizar y guardar

---

## 🏛️ Explorar Gobernanza en OpenMetadata

### Acceso a OpenMetadata

```
URL: http://localhost:8585
Usuario: admin
Contraseña: admin
```

### Funcionalidades Disponibles

#### 1. **Catálogo de Datos**

-   Ver todas las tablas/datasources
-   Explorar esquemas y tipos de datos
-   Ver descripciones y documentación

#### 2. **Linaje de Datos**

-   Visualizar flujo: Spark → Druid → Superset
-   Entender dependencias
-   Rastrear origen de los datos

#### 3. **Calidad de Datos**

-   Definir tests de calidad
-   Monitorear métricas
-   Alertas sobre anomalías

#### 4. **Colaboración**

-   Agregar descripciones
-   Etiquetar datasets
-   Asignar propietarios
-   Comentarios y discusiones

### Ejecutar Ingesta de Metadatos Manualmente

```bash
# Ingestar metadatos de Druid
docker exec -it openmetadata-ingestion \
  metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/druid_config.yml

# Ingestar metadatos de Superset
docker exec -it openmetadata-ingestion \
  metadata ingest -c /opt/airflow/openmetadata/ingestion_configs/superset_config.yml
```

---

## 🔍 Monitoreo y Debugging

### Ver Logs de un Servicio Específico

```bash
# Airflow
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Spark
docker-compose logs -f spark-master
docker-compose logs -f spark-worker

# OpenMetadata
docker-compose logs -f openmetadata-server
docker-compose logs -f elasticsearch

# Druid
docker-compose logs -f druid

# Superset
docker-compose logs -f superset
```

### Acceder a un Contenedor

```bash
# Airflow
docker exec -it airflow-webserver bash

# Spark
docker exec -it spark-master bash

# Ver archivos procesados
docker exec -it spark-master ls -lh /opt/spark/output/ukraine_sentiment_results/
```

### Verificar Conectividad

```bash
# Desde Airflow a Spark
docker exec -it airflow-webserver curl http://spark-master:8081

# Desde Airflow a Druid
docker exec -it airflow-webserver curl http://druid:8888/status/health

# Desde Airflow a OpenMetadata
docker exec -it airflow-webserver curl http://openmetadata-server:8585/api/v1/health
```

---

## 🛠️ Solución de Problemas Comunes

### Problema 1: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs <nombre-servicio>

# Reiniciar servicio específico
docker-compose restart <nombre-servicio>

# Reconstruir imagen
docker-compose build --no-cache <nombre-servicio>
```

### Problema 2: Error de conexión entre servicios

```bash
# Verificar que todos los servicios estén en la misma red
docker network inspect ukraine-tweets-sentiment-analysis_ukraine_sentiment_network

# Reiniciar todos los servicios
docker-compose down
docker-compose up -d
```

### Problema 3: Falta de memoria

```bash
# Verificar uso de recursos
docker stats

# Aumentar memoria en Docker Desktop:
# Settings > Resources > Memory > Aumentar a 8GB+
```

### Problema 4: Dataset no encontrado

```bash
# Verificar que el archivo existe
docker exec -it spark-master ls -lh /opt/spark/data/

# Copiar dataset manualmente
docker cp ./spark/data/ukraine_tweets.csv spark-master:/opt/spark/data/
```

---

## 🧪 Testing

### Probar el Script de Spark Localmente

```bash
# Acceder al contenedor de Spark
docker exec -it spark-master bash

# Ejecutar el script
spark-submit \
  --master local[*] \
  /opt/spark/app/sentiment_analysis_job.py
```

### Verificar Salida de Spark

```bash
# Ver archivos generados
docker exec -it spark-master ls -lh /opt/spark/output/ukraine_sentiment_results/

# Leer algunos resultados
docker exec -it spark-master \
  spark-shell --packages org.apache.spark:spark-sql_2.12:3.5.0 \
  -e "spark.read.parquet('/opt/spark/output/ukraine_sentiment_results/').show(10)"
```

---

## 📚 Tecnologías Utilizadas

| Tecnología                    | Versión | Propósito                    |
| ----------------------------- | ------- | ---------------------------- |
| **Apache Airflow**            | 2.7.3   | Orquestación de workflows    |
| **Apache Spark**              | 3.5.0   | Procesamiento distribuido    |
| **Apache Druid**              | 27.0.0  | Base de datos analítica OLAP |
| **Apache Superset**           | 3.0.1   | Visualización de datos       |
| **OpenMetadata**              | 1.2.0   | Gobernanza y catalogación    |
| **PostgreSQL**                | 14      | Base de datos relacional     |
| **Elasticsearch**             | 8.10.2  | Motor de búsqueda            |
| **Hugging Face Transformers** | 4.35.2  | Modelos de ML para NLP       |
| **Docker**                    | 20.x+   | Containerización             |

### Modelo de Machine Learning

-   **Nombre**: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
-   **Tipo**: Transformer (XLM-RoBERTa)
-   **Características**:
    -   ✅ Multilingüe (100+ idiomas)
    -   ✅ Especializado en tweets
    -   ✅ 3 clases: Negativo, Neutral, Positivo
    -   ✅ Pre-entrenado en millones de tweets

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE: Producción

Este proyecto usa credenciales de desarrollo por defecto. **Antes de usar en producción**:

1. ✅ Cambiar TODAS las contraseñas en `.env`
2. ✅ Usar secretos de Docker/Kubernetes
3. ✅ Habilitar HTTPS/TLS
4. ✅ Configurar autenticación OAuth
5. ✅ Implementar roles y permisos
6. ✅ Hacer backup de bases de datos
7. ✅ Configurar logs de auditoría

---

## 🧹 Limpieza

### Detener Todos los Servicios

```bash
# Detener sin eliminar datos
docker-compose stop

# Detener y eliminar contenedores (conserva volúmenes)
docker-compose down

# Detener y eliminar TODO (contenedores + volúmenes + redes)
docker-compose down -v
```

### Eliminar Imágenes

```bash
# Eliminar imágenes personalizadas
docker rmi ukraine-tweets-sentiment-analysis-airflow-webserver
docker rmi ukraine-tweets-sentiment-analysis-airflow-scheduler

# Limpiar imágenes no utilizadas
docker image prune -a
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la branch (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📞 Contacto

**Gabriel Fallas**

-   GitHub: [@GabrielFallas](https://github.com/GabrielFallas)
-   Email: gabriel@example.com

---

## 🎓 Referencias y Recursos

-   [Apache Airflow Docs](https://airflow.apache.org/docs/)
-   [Apache Spark Docs](https://spark.apache.org/docs/latest/)
-   [Apache Druid Docs](https://druid.apache.org/docs/latest/)
-   [Apache Superset Docs](https://superset.apache.org/docs/)
-   [OpenMetadata Docs](https://docs.open-metadata.org/)
-   [Hugging Face Models](https://huggingface.co/models)
-   [XLM-RoBERTa Model](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment)

---

## 📊 Estado del Proyecto

![Status](https://img.shields.io/badge/status-active-success.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

**🇺🇦 Construido con ❤️ para análisis de sentimiento sobre Ucrania**
