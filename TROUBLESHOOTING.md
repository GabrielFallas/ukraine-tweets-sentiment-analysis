# 🔧 Guía de Troubleshooting

## Índice de Problemas Comunes

1. [Servicios no inician](#servicios-no-inician)
2. [Errores de conexión entre servicios](#errores-de-conexión-entre-servicios)
3. [Problemas de memoria](#problemas-de-memoria)
4. [Dataset no encontrado](#dataset-no-encontrado)
5. [Errores en el DAG de Airflow](#errores-en-el-dag-de-airflow)
6. [Spark job falla](#spark-job-falla)
7. [OpenMetadata no se conecta](#openmetadata-no-se-conecta)
8. [Superset no carga dashboards](#superset-no-carga-dashboards)
9. [PostgreSQL no responde](#postgresql-no-responde)
10. [Elasticsearch falla](#elasticsearch-falla)

---

## Servicios no inician

### Síntoma

```
ERROR: Container failed to start
```

### Diagnóstico

```powershell
# Ver logs del servicio
docker-compose logs <nombre-servicio>

# Ver estado de todos los servicios
docker-compose ps
```

### Soluciones

#### 1. Puerto ya en uso

```powershell
# Ver qué proceso está usando el puerto
netstat -ano | findstr :8080

# Matar el proceso (reemplaza PID)
taskkill /PID <PID> /F
```

#### 2. Falta el archivo .env

```powershell
# Copiar el ejemplo
copy .env.example .env

# Editar el archivo .env según necesites
notepad .env
```

#### 3. Imagen corrupta

```powershell
# Reconstruir la imagen
docker-compose build --no-cache <nombre-servicio>

# Reiniciar
docker-compose up -d <nombre-servicio>
```

#### 4. Volumen corrupto

```powershell
# Detener servicios
docker-compose down

# Eliminar volúmenes
docker volume rm ukraine-tweets-sentiment-analysis_<nombre-volumen>

# Reiniciar
docker-compose up -d
```

---

## Errores de conexión entre servicios

### Síntoma

```
Connection refused to <service>:port
```

### Diagnóstico

```powershell
# Verificar que todos los servicios estén en la misma red
docker network inspect ukraine-tweets-sentiment-analysis_ukraine_sentiment_network

# Verificar conectividad desde un contenedor
docker exec -it airflow-webserver ping spark-master
```

### Soluciones

#### 1. Servicio no levantó completamente

```powershell
# Esperar a que el servicio esté healthy
docker-compose ps

# Ver logs para identificar el problema
docker-compose logs <servicio>
```

#### 2. Usar nombres de servicios correctos

En Docker Compose, usa los nombres de servicios definidos en `docker-compose.yml`:

-   ✅ `spark-master` (correcto)
-   ❌ `localhost` (incorrecto desde contenedores)

#### 3. Recrear la red

```powershell
docker-compose down
docker network prune
docker-compose up -d
```

---

## Problemas de memoria

### Síntoma

```
Container killed due to out of memory
java.lang.OutOfMemoryError
```

### Diagnóstico

```powershell
# Ver uso de recursos
docker stats

# Ver configuración de Docker Desktop
# Settings > Resources
```

### Soluciones

#### 1. Aumentar memoria de Docker

1. Abrir Docker Desktop
2. Settings > Resources > Memory
3. Aumentar a mínimo 8 GB (recomendado 12-16 GB)
4. Apply & Restart

#### 2. Reducir recursos de Spark

Editar `.env`:

```env
SPARK_WORKER_MEMORY=1g  # Reducir de 2g a 1g
SPARK_WORKER_CORES=1    # Reducir de 2 a 1
```

#### 3. Procesar menos datos

```python
# En sentiment_analysis_job.py
# Limitar el número de filas para pruebas
df = df.limit(1000)  # Solo procesar 1000 tweets
```

#### 4. Ajustar particiones de Spark

Editar `.env`:

```env
# Reducir particiones
spark.sql.shuffle.partitions=5  # De 10 a 5
```

---

## Dataset no encontrado

### Síntoma

```
FileNotFoundException: /opt/spark/data/ukraine_tweets.csv
```

### Diagnóstico

```powershell
# Verificar que el archivo existe
docker exec -it spark-master ls -lh /opt/spark/data/
```

### Soluciones

#### 1. Copiar el dataset

```powershell
# Desde PowerShell
docker cp .\spark\data\ukraine_tweets.csv spark-master:/opt/spark/data/

# Verificar
docker exec -it spark-master ls -lh /opt/spark/data/
```

#### 2. Verificar el volumen

En `docker-compose.yml`, asegúrate de que el volumen esté montado:

```yaml
volumes:
    - ./spark/data:/opt/spark/data
```

#### 3. Descargar dataset de Kaggle

```powershell
# Instalar Kaggle CLI
pip install kaggle

# Configurar credenciales (descargar kaggle.json de kaggle.com)
mkdir $env:USERPROFILE\.kaggle
copy kaggle.json $env:USERPROFILE\.kaggle\

# Descargar dataset (ejemplo)
kaggle datasets download -d <dataset-name> -p .\spark\data\
```

---

## Errores en el DAG de Airflow

### Síntoma

```
DAG import error
Broken DAG
```

### Diagnóstico

```powershell
# Ver logs de Airflow
docker-compose logs airflow-scheduler

# Verificar DAGs desde el CLI
docker exec -it airflow-webserver airflow dags list

# Ver errores de un DAG específico
docker exec -it airflow-webserver airflow dags show ukraine_sentiment_pipeline
```

### Soluciones

#### 1. Error de sintaxis Python

```powershell
# Validar el archivo Python localmente
python -m py_compile .\airflow\dags\ukraine_sentiment_pipeline_dag.py
```

#### 2. Falta dependencia

```powershell
# Acceder al contenedor
docker exec -it airflow-webserver bash

# Instalar dependencia faltante
pip install <paquete-faltante>

# O reconstruir la imagen con la dependencia en Dockerfile
```

#### 3. DAG pausado

1. Ir a Airflow UI: http://localhost:8080
2. Buscar el DAG
3. Activar el toggle switch (debe estar en azul/verde)

#### 4. Conexión Spark no configurada

```powershell
# Crear conexión desde CLI
docker exec -it airflow-webserver airflow connections add \
  'spark_default' \
  --conn-type 'spark' \
  --conn-host 'spark://spark-master' \
  --conn-port '7077'
```

---

## Spark job falla

### Síntoma

```
Spark job failed with exception
```

### Diagnóstico

```powershell
# Ver logs de Spark Master
docker-compose logs spark-master

# Ver logs de Spark Worker
docker-compose logs spark-worker

# Ver la UI de Spark
# http://localhost:8081
```

### Soluciones

#### 1. Modelo de Hugging Face no descarga

```python
# En sentiment_analysis_job.py, agregar cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Especificar directorio de cache
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-xlm-roberta-base-sentiment",
    cache_dir="/opt/spark/models"
)
```

#### 2. Error de memoria en UDF

```python
# Procesar en lotes más pequeños
# Modificar la función analyze_batch para procesar de a 10 textos
```

#### 3. Datos corruptos

```python
# Agregar manejo de errores
try:
    df = spark.read.csv(path, header=True)
except Exception as e:
    print(f"Error leyendo CSV: {e}")
    # Intentar con encoding diferente
    df = spark.read.option("encoding", "ISO-8859-1").csv(path, header=True)
```

#### 4. Ejecutar en modo local para debug

```powershell
# Acceder a Spark
docker exec -it spark-master bash

# Ejecutar manualmente
spark-submit \
  --master local[*] \
  --driver-memory 2g \
  /opt/spark/app/sentiment_analysis_job.py
```

---

## OpenMetadata no se conecta

### Síntoma

```
Failed to connect to OpenMetadata server
```

### Diagnóstico

```powershell
# Verificar estado de OpenMetadata
docker-compose ps openmetadata-server

# Ver logs
docker-compose logs openmetadata-server

# Verificar Elasticsearch (requerido)
docker-compose logs elasticsearch
```

### Soluciones

#### 1. Elasticsearch no está healthy

```powershell
# Verificar salud
curl http://localhost:9200/_cluster/health

# Si falla, reiniciar
docker-compose restart elasticsearch

# Esperar a que esté verde
docker-compose logs -f elasticsearch
```

#### 2. PostgreSQL de OpenMetadata no está listo

```powershell
# Verificar conexión
docker exec -it postgres_openmetadata_db psql -U openmetadata -d openmetadata_db

# Si falla, recrear
docker-compose down
docker volume rm ukraine-tweets-sentiment-analysis_postgres_openmetadata_data
docker-compose up -d postgres_openmetadata_db
```

#### 3. OpenMetadata no inicializó

```powershell
# Ver logs de inicialización
docker-compose logs openmetadata-server | findstr "ERROR"

# Recrear el servicio
docker-compose up -d --force-recreate openmetadata-server
```

#### 4. Acceso desde navegador

-   URL correcta: http://localhost:8585 (sin /api)
-   Usuario: `admin`
-   Contraseña: `admin`

---

## Superset no carga dashboards

### Síntoma

```
Dashboard not found
Database connection error
```

### Diagnóstico

```powershell
# Ver logs
docker-compose logs superset

# Acceder al contenedor
docker exec -it superset bash

# Verificar base de datos
superset db upgrade
```

### Soluciones

#### 1. Base de datos no inicializada

```powershell
docker exec -it superset superset db upgrade
docker exec -it superset superset init
```

#### 2. Usuario admin no existe

```powershell
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin
```

#### 3. Conexión a Druid no configurada

1. Ir a: http://localhost:8088
2. Settings > Database Connections > + Database
3. Seleccionar: Apache Druid
4. SQLAlchemy URI: `druid://druid:8888/druid/v2/sql`
5. Test Connection > Save

---

## PostgreSQL no responde

### Síntoma

```
Connection refused to postgres:5432
```

### Diagnóstico

```powershell
# Ver logs
docker-compose logs postgres_airflow_db
docker-compose logs postgres_superset_db
docker-compose logs postgres_openmetadata_db

# Verificar estado
docker-compose ps
```

### Soluciones

#### 1. Contenedor no está healthy

```powershell
# Esperar a que pase el healthcheck
docker-compose ps

# Ver por qué falla el healthcheck
docker exec -it postgres_airflow_db pg_isready -U airflow
```

#### 2. Puerto ya en uso

```powershell
# Cambiar puerto en docker-compose.yml
# De:
ports:
  - "5432:5432"
# A:
ports:
  - "5435:5432"
```

#### 3. Volumen corrupto

```powershell
# ADVERTENCIA: Esto borrará todos los datos
docker-compose down
docker volume rm ukraine-tweets-sentiment-analysis_postgres_airflow_data
docker-compose up -d postgres_airflow_db
```

---

## Elasticsearch falla

### Síntoma

```
Elasticsearch startup failed
max virtual memory areas vm.max_map_count too low
```

### Diagnóstico

```powershell
docker-compose logs elasticsearch
```

### Soluciones

#### 1. Aumentar vm.max_map_count (Linux/WSL2)

```bash
# Desde WSL2
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144

# Para que persista
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
```

#### 2. Reducir memoria de ES

En `docker-compose.yml`:

```yaml
elasticsearch:
    environment:
        - ES_JAVA_OPTS=-Xms256m -Xmx256m # Reducir de 512m
```

#### 3. Deshabilitar seguridad si da problemas

```yaml
elasticsearch:
    environment:
        - xpack.security.enabled=false
```

---

## Comandos Útiles para Debugging

### Ver logs en tiempo real

```powershell
docker-compose logs -f <servicio>
```

### Acceder a un contenedor

```powershell
docker exec -it <contenedor> bash
```

### Ver uso de recursos

```powershell
docker stats
```

### Limpiar todo y empezar de cero

```powershell
# ADVERTENCIA: Elimina todos los datos
docker-compose down -v
docker system prune -a
docker volume prune
docker-compose build --no-cache
docker-compose up -d
```

### Verificar conectividad de red

```powershell
# Desde un contenedor a otro
docker exec -it airflow-webserver curl http://spark-master:8081
docker exec -it airflow-webserver ping openmetadata-server
```

### Inspeccionar configuración

```powershell
# Ver variables de entorno de un contenedor
docker exec -it <contenedor> env

# Ver configuración de Docker Compose
docker-compose config
```

---

## Obtener Ayuda Adicional

### Logs de Airflow

```powershell
# Ver logs de una tarea específica
docker exec -it airflow-webserver airflow tasks logs ukraine_sentiment_pipeline spark_sentiment_analysis <date>
```

### Comunidades y Recursos

-   Apache Airflow: https://airflow.apache.org/community/
-   Apache Spark: https://spark.apache.org/community.html
-   OpenMetadata: https://slack.open-metadata.org/
-   Stack Overflow: Etiquetas `airflow`, `spark`, `druid`

### Reportar un Bug

Si encuentras un problema con el proyecto:

1. Crea un issue en GitHub
2. Incluye logs relevantes
3. Describe los pasos para reproducir
4. Menciona tu sistema operativo y versión de Docker

---

## Checklist de Verificación

Antes de reportar un problema, verifica:

-   [ ] Docker Desktop está corriendo
-   [ ] Tienes suficiente memoria (8GB+)
-   [ ] El archivo `.env` existe y está configurado
-   [ ] El dataset está en `spark/data/ukraine_tweets.csv`
-   [ ] Todos los servicios están "healthy" (`docker-compose ps`)
-   [ ] No hay conflictos de puertos
-   [ ] Los volúmenes no están corruptos
-   [ ] Has esperado suficiente tiempo para la inicialización (~5-10 min)

---

**¿Aún tienes problemas?** Abre un issue en GitHub con:

-   Descripción del problema
-   Logs completos
-   Comando ejecutado
-   Sistema operativo y versión de Docker
