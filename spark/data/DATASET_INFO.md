# ✅ Dataset de Tweets sobre la Guerra en Ucrania

## Dataset Incluido

Este directorio contiene el **dataset completo** de tweets sobre la guerra en Ucrania, listo para análisis.

### 📊 Información del Dataset

**Ubicación**: `ukraine-war-tweets/`

**Archivos**: 50+ archivos CSV diarios

-   **Formato**: `MMDD_UkraineCombinedTweetsDeduped.csv`
-   **Período**: Agosto - Octubre 2022
-   **Estado**: Tweets ya deduplicados por archivo

**Ejemplos de archivos**:

```
0819_UkraineCombinedTweetsDeduped.csv  (19 de agosto 2022)
0820_UkraineCombinedTweetsDeduped.csv  (20 de agosto 2022)
0821_UkraineCombinedTweetsDeduped.csv  (21 de agosto 2022)
...
1001_UkraineCombinedTweetsDeduped.csv  (1 de octubre 2022)
1002_UkraineCombinedTweetsDeduped.csv  (2 de octubre 2022)
...
```

**Volumen**: Miles de tweets únicos por día sobre la guerra en Ucrania

---

## 📋 Estructura de las Columnas

Cada archivo CSV contiene las siguientes columnas:

| Columna                   | Tipo      | Descripción                             |
| ------------------------- | --------- | --------------------------------------- |
| **`tweetid`**             | string    | ID único del tweet                      |
| **`text`**                | string    | Contenido completo del tweet            |
| **`tweetcreatedts`**      | timestamp | Fecha y hora de creación del tweet      |
| **`username`**            | string    | Nombre de usuario de Twitter            |
| **`userid`**              | string    | ID del usuario                          |
| **`location`**            | string    | Ubicación del usuario (si disponible)   |
| **`language`**            | string    | Idioma del tweet (en, es, uk, ru, etc.) |
| **`retweetcount`**        | integer   | Número de retweets                      |
| **`favorite_count`**      | integer   | Número de likes/favoritos               |
| **`hashtags`**            | string    | Hashtags usados en el tweet             |
| **`is_retweet`**          | boolean   | Indica si es un retweet                 |
| `acctdesc`                | string    | Descripción de la cuenta                |
| `following`               | integer   | Número de cuentas seguidas              |
| `followers`               | integer   | Número de seguidores                    |
| `totaltweets`             | integer   | Total de tweets del usuario             |
| `coordinates`             | string    | Coordenadas geográficas (si disponible) |
| `original_tweet_id`       | string    | ID del tweet original (si es retweet)   |
| `original_tweet_username` | string    | Usuario del tweet original              |
| `is_quote_status`         | boolean   | Indica si es quote tweet                |
| `extractedts`             | timestamp | Fecha de extracción                     |

---

## 🎯 Columnas Utilizadas por el Pipeline

El script de análisis de sentimiento (`sentiment_analysis_job.py`) utiliza principalmente:

✅ **Columnas principales**:

-   `tweetid` - Identificador único
-   `text` - Contenido para análisis de sentimiento
-   `tweetcreatedts` - Análisis temporal
-   `username` - Identificación del autor
-   `language` - Análisis multilingüe
-   `retweetcount` - Métricas de engagement
-   `favorite_count` - Popularidad del tweet
-   `location` - Análisis geográfico
-   `hashtags` - Análisis de tendencias
-   `is_retweet` - Filtrado de contenido

---

## 📈 Estadísticas del Dataset

### Período Cubierto

-   **Inicio**: 19 de agosto de 2022
-   **Fin**: Octubre de 2022 (y más...)
-   **Duración**: ~2-3 meses de tweets

### Idiomas

El dataset incluye tweets en múltiples idiomas:

-   🇬🇧 Inglés (English)
-   🇺🇦 Ucraniano (Ukrainian)
-   🇷🇺 Ruso (Russian)
-   🇪🇸 Español (Spanish)
-   🇫🇷 Francés (French)
-   🇩🇪 Alemán (German)
-   Y muchos más...

### Contenido

Tweets relacionados con:

-   Guerra en Ucrania
-   Eventos militares
-   Política internacional
-   Ayuda humanitaria
-   Opiniones públicas globales

---

## 🔍 Validación del Dataset

Para verificar que el dataset está correcto:

### Ver primeras líneas de un archivo

```powershell
# Windows PowerShell
Get-Content .\spark\data\ukraine-war-tweets\0819_UkraineCombinedTweetsDeduped.csv -First 5
```

```bash
# Linux/Mac
head -5 spark/data/ukraine-war-tweets/0819_UkraineCombinedTweetsDeduped.csv
```

### Contar archivos

```powershell
# Windows
(Get-ChildItem .\spark\data\ukraine-war-tweets\*.csv).Count
```

```bash
# Linux/Mac
ls -1 spark/data/ukraine-war-tweets/*.csv | wc -l
```

### Verificar en Docker

```bash
# Ver archivos desde el contenedor de Spark
docker exec -it spark-master ls -lh /opt/spark/data/ukraine-war-tweets/

# Contar líneas de un archivo
docker exec -it spark-master wc -l /opt/spark/data/ukraine-war-tweets/0819_UkraineCombinedTweetsDeduped.csv
```

---

## ⚙️ Procesamiento del Dataset

El script de Spark (`spark/app/sentiment_analysis_job.py`) procesa el dataset de la siguiente manera:

1. **Lectura**: Lee todos los archivos CSV del directorio usando wildcard pattern

    ```python
    DATA_PATH = "/opt/spark/data/ukraine-war-tweets/*.csv"
    ```

2. **Selección**: Extrae solo las columnas relevantes

3. **Deduplicación**: Elimina tweets duplicados por `tweetid`

4. **Limpieza**:

    - Filtra tweets nulos o vacíos
    - Limpia URLs, menciones, caracteres especiales
    - Normaliza el texto

5. **Análisis**: Aplica el modelo XLM-RoBERTa para sentimiento

6. **Enriquecimiento**: Agrega scores y probabilidades

7. **Salida**: Guarda en Parquet particionado por sentimiento

---

## 🎨 Ejemplo de Tweet del Dataset

```csv
tweetid: 1560416252937617411
text: "Dear vaccine advocate Do take the COVID19 mRNA shot..."
tweetcreatedts: 2022-08-19 00:00:00
username: JoeMokolobetsi
language: en
retweetcount: 0
favorite_count: 5
location: Afrika Borwa
hashtags: #Ukraine #COVID19
```

---

## 🔒 Consideraciones de Privacidad

⚠️ **Importante**:

-   Este dataset contiene tweets públicos
-   Respeta los términos de servicio de Twitter/X
-   No compartas información personal identificable
-   Usa los datos solo para investigación y educación
-   Cumple con GDPR y regulaciones locales

---

## 📊 Uso en el Pipeline

El dataset se procesa automáticamente cuando ejecutas el DAG de Airflow:

```powershell
# Ejecutar el pipeline
.\manage.ps1 trigger-dag

# O desde Airflow UI
# http://localhost:8080
# Activar y ejecutar: ukraine_sentiment_pipeline
```

El resultado será:

-   ✅ Tweets procesados con sentimiento
-   ✅ Datos cargados a Druid
-   ✅ Metadatos catalogados en OpenMetadata
-   ✅ Listos para visualización en Superset

---

## 🆘 Problemas Comunes

### "Dataset no encontrado"

```powershell
# Verificar que los archivos existen
ls .\spark\data\ukraine-war-tweets\

# Debe mostrar múltiples archivos .csv
```

### "Error de encoding"

El script usa UTF-8 por defecto. Si hay problemas, los archivos CSV ya están en formato correcto.

### "Demasiados archivos / Memoria insuficiente"

Para testing, puedes limitar el número de archivos:

```python
# En sentiment_analysis_job.py, cambiar:
DATA_PATH = "/opt/spark/data/ukraine-war-tweets/08*.csv"  # Solo agosto
```

---

## 📚 Referencias

-   **Fuente**: Dataset de tweets sobre la guerra en Ucrania
-   **Período**: Agosto-Octubre 2022
-   **Formato**: CSV con múltiples columnas de metadata
-   **Procesamiento**: Apache Spark con PySpark
-   **Modelo ML**: XLM-RoBERTa para análisis de sentimiento

---

**✅ Dataset listo para análisis!**

No necesitas descargar ni configurar nada adicional. El dataset está incluido y el pipeline está configurado para procesarlo automáticamente.
