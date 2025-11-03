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
        logger.info(f"Using sentiment model: {self.model_name}")
        logger.info("Model will be loaded per partition during processing")

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
        """Load CSV data from pre-sampled 70k dataset"""
        logger.info(f"Loading data from: {self.input_path}")

        try:
            # Read CSV with appropriate options
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .option("escape", "\"") \
                .option("multiLine", "true") \
                .csv(self.input_path)

            total_count = df.count()
            logger.info(f"Total rows in dataset: {total_count}")

            # Dataset is already pre-sampled to 70,000 rows, so no need to sample again
            logger.info(
                "Using full pre-sampled dataset (no additional sampling)")
            logger.info(f"Schema: {df.columns}")

            # Repartition to enable parallel processing across multiple executors
            # Use 4 partitions to parallelize the sentiment analysis
            df = df.repartition(4)
            logger.info(
                f"Repartitioned data into 4 partitions for parallel processing")

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
        Apply sentiment analysis to the DataFrame using mapPartitions for efficiency

        Args:
            df: Preprocessed Spark DataFrame

        Returns:
            DataFrame with sentiment column added
        """
        logger.info("Starting sentiment analysis...")

        model_name = self.model_name

        def process_partition(iterator):
            """
            Process a partition of data with its own model instance
            This avoids serialization issues and allows batch processing
            """
            from transformers import pipeline
            import logging

            # Initialize logger for this partition
            partition_logger = logging.getLogger(__name__)
            partition_logger.info(
                "Initializing sentiment model for partition...")

            # Initialize model once per partition (not per row)
            try:
                sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=-1,  # CPU
                    truncation=True,
                    max_length=512
                )
                partition_logger.info("Model loaded successfully in partition")
            except Exception as e:
                partition_logger.error(
                    f"Error loading model in partition: {str(e)}")
                # Return empty if model fails to load
                return iter([])

            # Process rows in this partition
            results = []
            batch = []
            batch_size = 100  # Larger batches for better throughput

            for row in iterator:
                text = row.cleaned_text if row.cleaned_text else ""

                if len(text.strip()) == 0:
                    # Empty text
                    results.append((*row, "NEUTRAL"))
                else:
                    # Store row and truncated text
                    batch.append((row, text[:512]))

                    # Process batch when full
                    if len(batch) >= batch_size:
                        try:
                            texts_only = [t for _, t in batch]
                            sentiments = sentiment_analyzer(texts_only)
                            for (original_row, _), sentiment in zip(batch, sentiments):
                                results.append(
                                    (*original_row, sentiment['label'].upper()))
                        except Exception as e:
                            partition_logger.warning(
                                f"Batch processing error: {str(e)}")
                            # Add NEUTRAL for failed batch
                            for original_row, _ in batch:
                                results.append((*original_row, "NEUTRAL"))
                        batch = []

            # Process remaining items in batch
            if batch:
                try:
                    texts_only = [t for _, t in batch]
                    sentiments = sentiment_analyzer(texts_only)
                    for (original_row, _), sentiment in zip(batch, sentiments):
                        results.append(
                            (*original_row, sentiment['label'].upper()))
                except Exception as e:
                    partition_logger.warning(
                        f"Final batch processing error: {str(e)}")
                    for original_row, _ in batch:
                        results.append((*original_row, "NEUTRAL"))

            return iter(results)

        # Convert to RDD, process partitions, convert back to DataFrame
        logger.info("Processing sentiment analysis using mapPartitions...")

        # Get the schema and add sentiment column
        from pyspark.sql.types import StructType, StringType, StructField
        original_schema = df.schema
        new_schema = StructType(
            original_schema.fields + [StructField("sentiment", StringType(), True)])

        # Apply mapPartitions
        rdd_with_sentiment = df.rdd.mapPartitions(process_partition)

        # Convert back to DataFrame
        df_with_sentiment = self.spark.createDataFrame(
            rdd_with_sentiment, schema=new_schema)

        # Count to trigger computation and log progress
        count = df_with_sentiment.count()
        logger.info(f"Sentiment analysis complete for {count} records")

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

        # Convert to pandas and save directly (works better for small datasets)
        logger.info("Converting Spark DataFrame to Pandas...")
        pandas_df = df_final.toPandas()

        # Save using pandas (avoids Spark permission issues)
        import os
        output_file = os.path.join(self.output_path, 'sentiment_results.csv')
        pandas_df.to_csv(output_file, index=False)

        logger.info(f"Results saved to: {output_file}")
        logger.info(f"Total rows saved: {len(pandas_df)}")

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

            # Clean output directory if it exists to avoid file conflicts
            import shutil
            import os
            try:
                if os.path.exists(self.output_path):
                    shutil.rmtree(self.output_path, ignore_errors=True)
                    logger.info(
                        f"Cleaned output directory: {self.output_path}")
                # Recreate the directory
                os.makedirs(self.output_path, exist_ok=True)
                logger.info(
                    f"Created fresh output directory: {self.output_path}")
            except Exception as clean_error:
                logger.warning(
                    f"Could not clean output directory: {clean_error}")

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
