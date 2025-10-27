# Dataset de Ejemplo - Tweets sobre Ucrania

Este directorio debe contener el dataset de tweets para el análisis.

## 📥 Obtener el Dataset

### Opción 1: Kaggle

1. Instala el CLI de Kaggle:

    ```bash
    pip install kaggle
    ```

2. Configura tus credenciales de Kaggle:

    - Ve a https://www.kaggle.com/settings
    - Crea un nuevo API token
    - Descarga el archivo `kaggle.json`
    - En Windows, colócalo en: `%USERPROFILE%\.kaggle\kaggle.json`

3. Descarga el dataset (ajusta según el dataset real):
    ```bash
    kaggle datasets download -d <dataset-author>/<dataset-name>
    ```

### Opción 2: Dataset personalizado

Si usas tu propio dataset, asegúrate de que tenga el formato CSV esperado.

## 📊 Formato Esperado del Dataset

El archivo `ukraine_tweets.csv` debe tener las siguientes columnas:

| Columna         | Tipo      | Descripción               | Ejemplo                          |
| --------------- | --------- | ------------------------- | -------------------------------- |
| `tweet_id`      | string    | ID único del tweet        | "1234567890"                     |
| `text`          | string    | Texto completo del tweet  | "Breaking news from #Ukraine..." |
| `created_at`    | timestamp | Fecha de creación         | "2024-01-15 14:30:00"            |
| `user_id`       | string    | ID del usuario            | "user_123"                       |
| `username`      | string    | Nombre de usuario         | "@user_name"                     |
| `language`      | string    | Idioma del tweet          | "en", "es", "uk"                 |
| `retweet_count` | integer   | Número de retweets        | 150                              |
| `like_count`    | integer   | Número de likes           | 320                              |
| `location`      | string    | Ubicación (si disponible) | "Kyiv, Ukraine"                  |

### Ejemplo de Estructura:

```csv
tweet_id,text,created_at,user_id,username,language,retweet_count,like_count,location
1234567890,"Breaking news from #Ukraine today...",2024-01-15 14:30:00,user_123,@john_doe,en,150,320,"New York, USA"
1234567891,"Solidarity with #Ukraine 🇺🇦",2024-01-15 14:35:00,user_456,@jane_smith,en,85,200,"London, UK"
```

## ✅ Validación del Dataset

Después de colocar el archivo, valida que esté correcto:

```bash
# Ver primeras líneas
docker exec -it spark-master head -n 5 /opt/spark/data/ukraine_tweets.csv

# Contar filas
docker exec -it spark-master wc -l /opt/spark/data/ukraine_tweets.csv
```

## 🔍 Columnas Mínimas Requeridas

El script de análisis **requiere al menos** estas columnas:

-   `text`: El texto del tweet (obligatorio)
-   Cualquier otra columna es opcional y se preservará en la salida

Si tu dataset tiene nombres de columnas diferentes, ajusta el script:
`spark/app/sentiment_analysis_job.py`

## 📝 Notas Importantes

1. **Codificación**: El archivo debe estar en UTF-8
2. **Tamaño**: Se recomienda empezar con un subset para pruebas (~10,000 tweets)
3. **Limpieza**: No es necesario limpiar el texto previamente, el script lo hace automáticamente
4. **Idiomas**: El modelo XLM-RoBERTa soporta 100+ idiomas

## 🌐 Datasets Públicos Sugeridos

Algunos datasets públicos relacionados con Ucrania:

1. **Twitter Ukraine Dataset** (buscar en Kaggle)
2. **Conflict-related Tweets** (buscar en data.world)
3. **European News Dataset** (contiene noticias sobre Ucrania)

## 🔒 Consideraciones de Privacidad

-   ⚠️ Respeta los términos de servicio de Twitter/X
-   ⚠️ No compartas información personal identificable
-   ⚠️ Cumple con GDPR y regulaciones locales
-   ⚠️ Usa los datos solo para investigación/educación
