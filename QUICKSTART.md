# 🚀 Guía de Inicio Rápido

## ⚡ Iniciar el Proyecto en 5 Minutos

### ✅ Prerrequisitos Verificados

Antes de comenzar, asegúrate de tener:

-   [x] **Docker Desktop** instalado y corriendo
-   [x] **Docker Compose** v2.x o superior
-   [x] **8 GB RAM mínimo** disponible (16 GB recomendado)
-   [x] **20 GB espacio en disco** libre
-   [x] **PowerShell** (Windows) o **Bash** (Linux/Mac)

### 📂 Dataset Incluido ✅

**¡Buenas noticias!** El dataset ya está incluido en el proyecto:

-   **Ubicación**: `spark/data/ukraine-war-tweets/`
-   **Archivos**: 50+ archivos CSV diarios (Agosto-Octubre 2022)
-   **Tweets**: Miles de tweets únicos sobre la guerra en Ucrania
-   **Estado**: Listo para usar, no necesitas descargar nada

---

## 🎯 Pasos para Iniciar

### 1️⃣ Clonar el Repositorio

```powershell
# Windows PowerShell
git clone https://github.com/GabrielFallas/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis
```

```bash
# Linux/Mac
git clone https://github.com/GabrielFallas/ukraine-tweets-sentiment-analysis.git
cd ukraine-tweets-sentiment-analysis
```

### 2️⃣ Configurar Variables de Entorno

El archivo `.env` ya existe con valores por defecto. Para producción, cámbialo:

```powershell
# Windows - Opcional: editar configuración
notepad .env

# Linux/Mac
nano .env
```

**Para desarrollo/testing, puedes usar los valores por defecto sin cambios.**

### 3️⃣ Iniciar Todos los Servicios

```powershell
# Windows PowerShell - Opción 1 (Recomendada)
.\manage.ps1 install

# Windows PowerShell - Opción 2 (Manual)
docker-compose build
docker-compose up -d
```

```bash
# Linux/Mac - Opción 1 (Recomendada)
make install

# Linux/Mac - Opción 2 (Manual)
docker-compose build
docker-compose up -d
```

⏱️ **Tiempo de inicio**: 5-10 minutos (primera vez)docker system prune

```powershell
# Windows
.\manage.ps1 health

# Linux/Mac
make health
```

Deberías ver todos los servicios como ✅ OK

---

## 🌐 Acceder a las Interfaces

Una vez iniciado, abre tu navegador y accede a:

| Servicio            | URL                   | Usuario | Contraseña |
| ------------------- | --------------------- | ------- | ---------- |
| **Airflow** 🎯      | http://localhost:8080 | `admin` | `admin`    |
| **Spark UI** ⚡     | http://localhost:8081 | -       | -          |
| **Superset** 📊     | http://localhost:8088 | `admin` | `admin`    |
| **Druid** 🗄️        | http://localhost:8888 | -       | -          |
| **OpenMetadata** 🏛️ | http://localhost:8585 | `admin` | `admin`    |

---

## ▶️ Ejecutar el Pipeline

### Opción 1: Desde Airflow UI (Recomendada)

1. Abrir http://localhost:8080
2. Login con `admin` / `admin`
3. Buscar el DAG: **`ukraine_sentiment_pipeline`**
4. Activar el DAG (toggle a la izquierda)
5. Click en el botón ▶️ "Trigger DAG"
6. Monitorear en la vista "Graph" o "Grid"

### Opción 2: Desde la Línea de Comandos

```powershell
# Windows
.\manage.ps1 trigger-dag

# Linux/Mac
make trigger-dag
```

### ⏱️ Tiempo de Ejecución

-   **Carga de datos**: ~2-3 minutos
-   **Análisis con ML**: ~10-20 minutos (depende del hardware)
-   **Carga a Druid**: ~1-2 minutos
-   **Catalogación**: ~1 minuto

**Total**: ~15-30 minutos para el pipeline completo

---

## 📊 Ver Resultados

### 1. Monitorear en Airflow

-   **URL**: http://localhost:8080
-   Ver estado de cada tarea
-   Revisar logs en tiempo real
-   Ver métricas de ejecución

### 2. Ver Resultados en Spark

```powershell
# Ver archivos generados
docker exec -it spark-master ls -lh /opt/spark/output/ukraine_sentiment_results/

# Ver contenido (primeras líneas)
docker exec -it spark-master head /opt/spark/output/ukraine_sentiment_results/sentiment=positive/*.parquet
```

### 3. Consultar en Druid

1. Abrir http://localhost:8888
2. Ir a "Query"
3. Ver el datasource: `ukraine_sentiment_tweets`
4. Ejecutar queries SQL

### 4. Crear Dashboards en Superset

1. Abrir http://localhost:8088
2. Login: `admin` / `admin`
3. Settings > Database Connections > + Database
4. Seleccionar: Apache Druid
5. SQLAlchemy URI: `druid://druid:8888/druid/v2/sql`
6. Test Connection > Save
7. Crear charts y dashboards

### 5. Explorar en OpenMetadata

1. Abrir http://localhost:8585
2. Login: `admin` / `admin`
3. Explorar:
    - **Explore** > Ver catálogo de datos
    - **Lineage** > Ver flujo de datos
    - **Data Quality** > Métricas de calidad

---

## 🎨 Ejemplos de Visualizaciones

### Chart 1: Distribución de Sentimientos (Pie Chart)

```
Positivo: 35%
Neutral:  45%
Negativo: 20%
```

### Chart 2: Tendencia Temporal (Line Chart)

Evolución de sentimientos día a día

### Chart 3: Top Hashtags por Sentimiento

Los hashtags más usados en tweets positivos vs negativos

---

## 🛑 Detener los Servicios

```powershell
# Windows - Detener sin eliminar datos
.\manage.ps1 down

# Windows - Detener y eliminar TODO (incluye datos)
.\manage.ps1 down-volumes
```

```bash
# Linux/Mac - Detener sin eliminar datos
make down

# Linux/Mac - Detener y eliminar TODO
make down-volumes
```

---

## 🔍 Ver Logs

```powershell
# Windows - Ver todos los logs
.\manage.ps1 logs

# Ver logs de un servicio específico
.\manage.ps1 logs-airflow
.\manage.ps1 logs-spark
.\manage.ps1 logs-openmetadata
```

```bash
# Linux/Mac - Ver todos los logs
make logs

# Ver logs de servicios específicos
make logs-airflow
make logs-spark
```

---

## 🆘 Problemas Comunes

### "Contenedor no inicia"

```powershell
# Ver logs del servicio con problemas
docker-compose logs <nombre-servicio>

# Reiniciar servicio específico
docker-compose restart <nombre-servicio>
```

### "Puerto ya en uso"

```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8080

# Cambiar puerto en docker-compose.yml o detener el proceso
```

### "Sin memoria"

1. Abrir Docker Desktop
2. Settings > Resources > Memory
3. Aumentar a mínimo 8 GB
4. Apply & Restart

### "Dataset no encontrado"

```powershell
# Verificar que el dataset existe
ls .\spark\data\ukraine-war-tweets\

# Debe mostrar 50+ archivos CSV
```

Para más ayuda, consulta: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 Próximos Pasos

Después de ejecutar el pipeline exitosamente:

1. **Explorar los datos** en Druid Console
2. **Crear visualizaciones** en Superset
3. **Revisar el linaje** en OpenMetadata
4. **Experimentar** con diferentes modelos ML
5. **Contribuir** al proyecto (ver [CONTRIBUTING.md](CONTRIBUTING.md))

---

## 🎓 Aprender Más

### Documentación

-   [README.md](README.md) - Documentación completa
-   [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura detallada
-   [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolución de problemas
-   [spark/data/DATASET_INFO.md](spark/data/DATASET_INFO.md) - Info del dataset

### Comandos Útiles

```powershell
# Windows
.\manage.ps1 help              # Ver todos los comandos
.\manage.ps1 ps                # Ver estado de servicios
.\manage.ps1 health            # Verificar salud
.\manage.ps1 backup-db         # Hacer backup
.\manage.ps1 clean             # Limpiar archivos temporales
```

```bash
# Linux/Mac
make help                      # Ver todos los comandos
make ps                        # Ver estado
make health                    # Verificar salud
make backup-db                 # Backup
```

---

## ✅ Checklist de Verificación

Antes de ejecutar el pipeline, verifica:

-   [ ] Docker Desktop está corriendo
-   [ ] Tienes 8+ GB RAM disponible
-   [ ] Tienes 20+ GB espacio en disco
-   [ ] El archivo `.env` existe
-   [ ] El dataset está en `spark/data/ukraine-war-tweets/`
-   [ ] Puertos 8080, 8081, 8088, 8888, 8585 están libres
-   [ ] Has esperado 5-10 min para que todos los servicios inicien

---

## 🎉 ¡Listo!

Si todos los pasos anteriores funcionaron:

✅ **Tu pipeline está corriendo**  
✅ **El dataset está siendo procesado**  
✅ **Los servicios están disponibles**  
✅ **Puedes visualizar los resultados**

**¡Felicitaciones! 🎊 Ahora tienes un sistema completo de análisis de sentimiento con gobernanza de datos.**

---

## 📞 Soporte

¿Necesitas ayuda?

-   📖 Lee la [documentación completa](README.md)
-   🔧 Consulta [troubleshooting](TROUBLESHOOTING.md)
-   💬 Abre un [issue en GitHub](https://github.com/GabrielFallas/ukraine-tweets-sentiment-analysis/issues)
-   📧 Email: gabriel@example.com

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Completamente funcional con dataset incluido
