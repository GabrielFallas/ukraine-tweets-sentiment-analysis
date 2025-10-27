"""
==============================================
SCRIPT DE ANÁLISIS DE SENTIMIENTO CON PYSPARK
==============================================

Este script realiza el análisis de sentimiento sobre tweets relacionados
con la guerra en Ucrania utilizando Apache Spark y un modelo de Hugging Face.

Pipeline:
1. Inicialización de SparkSession
2. Carga del dataset de Kaggle
3. Limpieza y preprocesamiento de texto
4. Análisis de sentimiento con modelo multilingüe (XLM-RoBERTa)
5. Guardado de resultados en formato Parquet

Modelo: cardiffnlp/twitter-xlm-roberta-base-sentiment
- Soporta múltiples idiomas
- Especializado en análisis de sentimiento en Twitter
- Clasifica: Negativo, Neutral, Positivo
"""

import re
from datetime import datetime
from typing import List, Dict

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, udf, pandas_udf, lower, trim, regexp_replace,
    when, length, current_timestamp, lit
)
from pyspark.sql.types import (
    StructType, StructField, StringType, FloatType,
    IntegerType, TimestampType
)

# Importaciones de Transformers (Hugging Face)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class SentimentAnalyzer:
    """
    Clase para análisis de sentimiento usando modelo de Hugging Face
    """

    def __init__(self, model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"):
        """
        Inicializa el analizador de sentimiento

        Args:
            model_name: Nombre del modelo de Hugging Face a utilizar
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo y tokenizer de Hugging Face"""
        print(f"🔄 Cargando modelo: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name)
        self.model.eval()  # Modo evaluación
        print("✅ Modelo cargado exitosamente")

    def analyze_batch(self, texts: pd.Series) -> pd.DataFrame:
        """
        Analiza el sentimiento de un lote de textos

        Args:
            texts: Serie de pandas con los textos a analizar

        Returns:
            DataFrame con sentimiento, score y probabilidades
        """
        results = []

        for text in texts:
            if not text or pd.isna(text) or len(str(text).strip()) == 0:
                results.append({
                    'sentiment': 'unknown',
                    'sentiment_score': 0.0,
                    'negative_prob': 0.0,
                    'neutral_prob': 0.0,
                    'positive_prob': 0.0
                })
                continue

            try:
                # Tokenizar el texto
                inputs = self.tokenizer(
                    str(text),
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )

                # Inferencia
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probs = torch.softmax(logits, dim=1).squeeze().tolist()

                # Mapeo de probabilidades: [negativo, neutral, positivo]
                negative_prob = probs[0]
                neutral_prob = probs[1]
                positive_prob = probs[2]

                # Determinar sentimiento predominante
                max_idx = probs.index(max(probs))
                sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                sentiment = sentiment_map[max_idx]

                # Score: -1 (muy negativo) a +1 (muy positivo)
                sentiment_score = positive_prob - negative_prob

                results.append({
                    'sentiment': sentiment,
                    'sentiment_score': round(sentiment_score, 4),
                    'negative_prob': round(negative_prob, 4),
                    'neutral_prob': round(neutral_prob, 4),
                    'positive_prob': round(positive_prob, 4)
                })

            except Exception as e:
                print(f"❌ Error analizando texto: {e}")
                results.append({
                    'sentiment': 'error',
                    'sentiment_score': 0.0,
                    'negative_prob': 0.0,
                    'neutral_prob': 0.0,
                    'positive_prob': 0.0
                })

        return pd.DataFrame(results)


def clean_text(text: str) -> str:
    """
    Limpia el texto de un tweet

    Args:
        text: Texto original del tweet

    Returns:
        Texto limpio
    """
    if not text or pd.isna(text):
        return ""

    text = str(text)

    # Remover URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remover menciones (@usuario)
    text = re.sub(r'@\w+', '', text)

    # Remover hashtags pero mantener el texto (ej: #Ukraine -> Ukraine)
    text = re.sub(r'#(\w+)', r'\1', text)

    # Remover caracteres especiales y números, pero mantener espacios
    text = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]', '', text)

    # Remover espacios múltiples
    text = re.sub(r'\s+', ' ', text)

    # Quitar espacios al inicio y final
    text = text.strip()

    return text


def create_spark_session(app_name: str = "UkraineSentimentAnalysis") -> SparkSession:
    """
    Crea y configura la sesión de Spark

    Args:
        app_name: Nombre de la aplicación Spark

    Returns:
        SparkSession configurada
    """
    print("🚀 Inicializando SparkSession...")

    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()

    print(f"✅ SparkSession creada: {spark.version}")
    return spark


def load_dataset(spark: SparkSession, data_path: str):
    """
    Carga el dataset de tweets desde múltiples archivos CSV

    El dataset real contiene archivos diarios con nombres como:
    0819_UkraineCombinedTweetsDeduped.csv, 0820_UkraineCombinedTweetsDeduped.csv, etc.

    Args:
        spark: SparkSession activa
        data_path: Ruta al directorio con los archivos CSV

    Returns:
        DataFrame de Spark con los datos consolidados
    """
    print(f"📂 Cargando dataset desde: {data_path}")

    # Leer todos los archivos CSV del directorio
    df = spark.read.csv(
        data_path,
        header=True,
        inferSchema=True,
        encoding='utf-8'
    )

    # Seleccionar solo las columnas relevantes del dataset real
    # Columnas disponibles: userid, username, location, tweetid, tweetcreatedts,
    # retweetcount, text, hashtags, language, favorite_count, is_retweet, etc.
    relevant_columns = [
        'tweetid',
        'text',
        'tweetcreatedts',
        'username',
        'location',
        'language',
        'retweetcount',
        'favorite_count',
        'hashtags',
        'is_retweet'
    ]

    # Verificar qué columnas existen en el DataFrame
    existing_columns = [col for col in relevant_columns if col in df.columns]

    if existing_columns:
        df = df.select(*existing_columns)

    # Remover duplicados por tweetid
    df = df.dropDuplicates(['tweetid'])

    # Filtrar tweets nulos o vacíos
    df = df.filter(col('text').isNotNull())
    df = df.filter(length(col('text')) > 0)

    print(
        f"✅ Dataset cargado: {df.count():,} tweets únicos, {len(df.columns)} columnas")
    print(f"📋 Columnas seleccionadas: {df.columns}")

    return df


def preprocess_data(df):
    """
    Preprocesa el DataFrame aplicando limpieza de texto

    Args:
        df: DataFrame de Spark con tweets

    Returns:
        DataFrame preprocesado
    """
    print("🧹 Preprocesando datos...")

    # Registrar UDF para limpieza de texto
    clean_text_udf = udf(clean_text, StringType())

    # Aplicar limpieza
    df_clean = df.withColumn("cleaned_text", clean_text_udf(col("text"))) \
                 .withColumn("text_length", length(col("cleaned_text"))) \
                 .filter(col("text_length") > 10)  # Filtrar textos muy cortos

    print(f"✅ Preprocesamiento completado: {df_clean.count()} filas válidas")

    return df_clean


def analyze_sentiment_with_pandas_udf(df):
    """
    Aplica análisis de sentimiento usando Pandas UDF para procesamiento distribuido

    Args:
        df: DataFrame de Spark con tweets limpios

    Returns:
        DataFrame con análisis de sentimiento
    """
    print("🤖 Analizando sentimientos con modelo de Hugging Face...")

    # Definir schema de salida
    output_schema = StructType([
        StructField("sentiment", StringType(), False),
        StructField("sentiment_score", FloatType(), False),
        StructField("negative_prob", FloatType(), False),
        StructField("neutral_prob", FloatType(), False),
        StructField("positive_prob", FloatType(), False)
    ])

    # Crear analizador (se inicializará en cada worker)
    @pandas_udf(output_schema)
    def sentiment_udf(texts: pd.Series) -> pd.DataFrame:
        analyzer = SentimentAnalyzer()
        return analyzer.analyze_batch(texts)

    # Aplicar análisis de sentimiento
    df_with_sentiment = df.withColumn(
        "sentiment_analysis",
        sentiment_udf(col("cleaned_text"))
    )

    # Expandir la estructura anidada
    df_result = df_with_sentiment.select(
        col("*"),
        col("sentiment_analysis.sentiment").alias("sentiment"),
        col("sentiment_analysis.sentiment_score").alias("sentiment_score"),
        col("sentiment_analysis.negative_prob").alias("negative_prob"),
        col("sentiment_analysis.neutral_prob").alias("neutral_prob"),
        col("sentiment_analysis.positive_prob").alias("positive_prob")
    ).drop("sentiment_analysis")

    # Agregar timestamp de procesamiento
    df_result = df_result.withColumn("processed_at", current_timestamp())

    print("✅ Análisis de sentimiento completado")

    return df_result


def save_results(df, output_path: str):
    """
    Guarda los resultados en formato Parquet

    Args:
        df: DataFrame con resultados
        output_path: Ruta donde guardar los resultados
    """
    print(f"💾 Guardando resultados en: {output_path}")

    df.write \
        .mode("overwrite") \
        .partitionBy("sentiment") \
        .parquet(output_path)

    print("✅ Resultados guardados exitosamente")


def print_statistics(df):
    """
    Imprime estadísticas del análisis

    Args:
        df: DataFrame con resultados
    """
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS DEL ANÁLISIS DE SENTIMIENTO")
    print("="*60)

    total_tweets = df.count()
    print(f"\n📌 Total de tweets analizados: {total_tweets:,}")

    print("\n📈 Distribución de sentimientos:")
    sentiment_dist = df.groupBy("sentiment").count().orderBy(
        "count", ascending=False)
    sentiment_dist.show()

    print("\n📉 Estadísticas de scores:")
    df.select("sentiment_score").describe().show()

    print("\n🎯 Sentimientos promedio por categoría:")
    df.groupBy("sentiment") \
      .agg({
          "sentiment_score": "avg",
          "negative_prob": "avg",
          "neutral_prob": "avg",
          "positive_prob": "avg"
      }) \
        .show()


def main():
    """
    Función principal del script
    """
    print("\n" + "="*60)
    print("🇺🇦 PIPELINE DE ANÁLISIS DE SENTIMIENTO - TWEETS UCRANIA")
    print("="*60 + "\n")

    # Configuración
    # Cambiar para leer todos los archivos CSV del directorio
    DATA_PATH = "/opt/spark/data/ukraine-war-tweets/*.csv"
    OUTPUT_PATH = "/opt/spark/output/ukraine_sentiment_results"

    try:
        # 1. Crear SparkSession
        spark = create_spark_session()

        # 2. Cargar dataset
        df = load_dataset(spark, DATA_PATH)

        # 3. Preprocesar datos
        df_clean = preprocess_data(df)

        # 4. Análisis de sentimiento
        df_sentiment = analyze_sentiment_with_pandas_udf(df_clean)

        # 5. Guardar resultados
        save_results(df_sentiment, OUTPUT_PATH)

        # 6. Mostrar estadísticas
        print_statistics(df_sentiment)

        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR EN EL PIPELINE: {e}")
        raise

    finally:
        if 'spark' in locals():
            spark.stop()
            print("🛑 SparkSession detenida")


if __name__ == "__main__":
    main()
