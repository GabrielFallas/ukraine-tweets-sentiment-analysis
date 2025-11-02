"""
Spark Sentiment Analysis Script for Ukraine-Russia Crisis Twitter Dataset
Processes tweets, performs sentiment analysis, and saves results for Druid ingestion.
"""

import sys
import re
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, regexp_replace, trim, lower, to_timestamp
from pyspark.sql.types import StringType, StructType, StructField, TimestampType, IntegerType
from transformers import pipeline
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TweetSentimentAnalyzer:
    """Handles sentiment analysis of tweets using Spark and Hugging Face"""

    def __init__(self, input_path, output_path, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize the analyzer

        Args:
            input_path: Path to input CSV file
            output_path: Path to output directory
            model_name: Hugging Face model for sentiment analysis
        """
        self.input_path = input_path
        self.output_path = output_path
        self.model_name = model_name

        # Initialize Spark Session
        self.spark = SparkSession.builder \
            .appName("UkraineTwitterSentimentAnalysis") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .getOrCreate()

        logger.info(f"Spark session initialized: {self.spark.version}")

        # Pre-download model to avoid repeated downloads
        logger.info(f"Loading sentiment analysis model: {self.model_name}")
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name)
            logger.info("Model and tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

        # Initialize sentiment analysis pipeline
        logger.info(f"Loading sentiment analysis model: {self.model_name}")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            device=-1  # Use CPU
        )
        logger.info("Sentiment model loaded successfully")

    @staticmethod
    def clean_tweet(text):
        """
        Clean tweet text by removing URLs, mentions, hashtags, and special characters

        Args:
            text: Raw tweet text

        Returns:
            Cleaned tweet text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)

        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)

        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def analyze_sentiment_batch(self, texts):
        """
        Analyze sentiment for a batch of texts

        Args:
            texts: List of text strings

        Returns:
            List of sentiment labels
        """
        results = []
        for text in texts:
            if not text or len(text.strip()) < 3:
                results.append("NEUTRAL")
                continue

            try:
                # Truncate text to model's max length
                text_truncated = text[:512]
                sentiment_result = self.sentiment_pipeline(text_truncated)[0]

                # Map model output to our labels
                label = sentiment_result['label'].upper()
                if label == 'POSITIVE':
                    results.append('POSITIVE')
                elif label == 'NEGATIVE':
                    results.append('NEGATIVE')
                else:
                    results.append('NEUTRAL')
            except Exception as e:
                logger.warning(f"Error analyzing text: {str(e)}")
                results.append('NEUTRAL')

        return results

    def load_data(self):
        """Load CSV data from Kaggle dataset"""
        logger.info(f"Loading data from: {self.input_path}")

        try:
            # Read CSV with appropriate options
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .option("escape", "\"") \
                .option("multiLine", "true") \
                .csv(self.input_path)

            logger.info(f"Loaded {df.count()} rows")
            logger.info(f"Schema: {df.columns}")

            return df

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def preprocess_data(self, df):
        """
        Preprocess the DataFrame by cleaning and transforming columns

        Args:
            df: Input Spark DataFrame

        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting data preprocessing...")

        # Register UDF for cleaning tweets
        clean_tweet_udf = udf(self.clean_tweet, StringType())

        # Select and rename relevant columns (adjust based on actual CSV structure)
        # Common columns: userid, username, acctdesc, location, following, followers,
        # totaltweets, usercreatedts, tweetid, tweetcreatedts, retweetcount, text, hashtags

        # Clean the tweet text
        df_cleaned = df.withColumn("cleaned_text", clean_tweet_udf(col("text"))) \
            .filter(col("cleaned_text").isNotNull()) \
            .filter(col("cleaned_text") != "")

        # Parse timestamp if needed
        if "tweetcreatedts" in df_cleaned.columns:
            df_cleaned = df_cleaned.withColumn(
                "tweet_timestamp",
                to_timestamp(col("tweetcreatedts"))
            )

        logger.info(
            f"Preprocessing complete. {df_cleaned.count()} rows after cleaning")

        return df_cleaned

    def analyze_sentiment(self, df):
        """
        Apply sentiment analysis to the DataFrame

        Args:
            df: Preprocessed Spark DataFrame

        Returns:
            DataFrame with sentiment column added
        """
        logger.info("Starting sentiment analysis...")

        # For large datasets, process in batches using Pandas UDF for efficiency
        # Convert to Pandas for sentiment analysis (for smaller datasets or batches)

        # Sample for testing (remove for production)
        # df = df.limit(10000)

        # Collect cleaned text for sentiment analysis
        # For very large datasets, consider using mapPartitions or Pandas UDF
        texts = df.select("cleaned_text").rdd.flatMap(lambda x: x).collect()

        logger.info(f"Analyzing sentiment for {len(texts)} texts...")

        # Process in batches to avoid memory issues
        batch_size = 100
        sentiments = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_sentiments = self.analyze_sentiment_batch(batch)
            sentiments.extend(batch_sentiments)

            if (i // batch_size + 1) % 10 == 0:
                logger.info(f"Processed {i + len(batch)} / {len(texts)} texts")

        logger.info("Sentiment analysis complete")

        # Create a new DataFrame with sentiments
        sentiment_df = self.spark.createDataFrame(
            [(text, sentiment) for text, sentiment in zip(texts, sentiments)],
            ["cleaned_text", "sentiment"]
        )

        # Join with original DataFrame
        df_with_sentiment = df.join(
            sentiment_df, on="cleaned_text", how="inner")

        return df_with_sentiment

    def save_results(self, df):
        """
        Save processed results to CSV for Druid ingestion

        Args:
            df: DataFrame with sentiment analysis results
        """
        logger.info(f"Saving results to: {self.output_path}")

        # Select final columns for output
        output_columns = [
            "userid", "username", "location", "followers", "following",
            "tweetid", "tweetcreatedts", "text", "cleaned_text",
            "hashtags", "retweetcount", "sentiment"
        ]

        # Filter columns that exist
        existing_columns = [col for col in output_columns if col in df.columns]

        df_final = df.select(*existing_columns)

        # Save as CSV with header
        df_final.coalesce(1) \
            .write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv(self.output_path)

        logger.info("Results saved successfully")

        # Print summary statistics
        self.print_summary(df_final)

    def print_summary(self, df):
        """Print summary statistics of sentiment analysis"""
        logger.info("=== Sentiment Analysis Summary ===")

        sentiment_counts = df.groupBy("sentiment").count().collect()

        total = sum([row['count'] for row in sentiment_counts])

        for row in sentiment_counts:
            sentiment = row['sentiment']
            count = row['count']
            percentage = (count / total) * 100
            logger.info(f"{sentiment}: {count} ({percentage:.2f}%)")

        logger.info(f"Total tweets processed: {total}")

    def run(self):
        """Execute the complete sentiment analysis pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Ukraine Twitter Sentiment Analysis Pipeline")
            logger.info("=" * 60)

            # Load data
            df = self.load_data()

            # Preprocess
            df_cleaned = self.preprocess_data(df)

            # Analyze sentiment
            df_with_sentiment = self.analyze_sentiment(df_cleaned)

            # Save results
            self.save_results(df_with_sentiment)

            logger.info("=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise

        finally:
            # Clean up
            self.spark.stop()
            logger.info("Spark session stopped")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: spark-submit sentiment_analysis.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    analyzer = TweetSentimentAnalyzer(input_path, output_path)
    analyzer.run()


if __name__ == "__main__":
    main()
