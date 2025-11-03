"""
Create mock sentiment dataset for testing the pipeline
"""
import pandas as pd
import random
from datetime import datetime

# Set seed for reproducibility
random.seed(42)

# Read a sample of the original data
print("Reading sample data...")
df = pd.read_csv('/opt/airflow/data/raw/ukraine_tweets.csv', nrows=5000)

# Select relevant columns
columns_to_keep = ['userid', 'username', 'location', 'followers', 'following',
                   'tweetid', 'tweetcreatedts', 'text', 'hashtags', 'retweetcount']

df_sample = df[columns_to_keep].copy()

# Add mock sentiment labels based on simple keyword analysis


def assign_sentiment(text):
    if pd.isna(text):
        return 'NEUTRAL'

    text_lower = str(text).lower()

    # Positive keywords
    positive_keywords = ['support', 'help', 'peace', 'victory', 'freedom', 'hope',
                         'brave', 'hero', 'strong', 'win', 'success', 'glory',
                         'donate', 'solidarity', 'love', 'together']

    # Negative keywords
    negative_keywords = ['war', 'attack', 'bomb', 'kill', 'death', 'destroy',
                         'invasion', 'crisis', 'threat', 'violence', 'casualties',
                         'dead', 'wounded', 'strikes', 'missile']

    positive_count = sum(
        1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(
        1 for keyword in negative_keywords if keyword in text_lower)

    if positive_count > negative_count:
        return 'POSITIVE'
    elif negative_count > positive_count:
        return 'NEGATIVE'
    else:
        return 'NEUTRAL'


print("Processing tweets...")

# Add cleaned_text (simplified version of text)
df_sample['cleaned_text'] = df_sample['text'].fillna(
    '').str.replace(r'http\S+', '', regex=True)
df_sample['cleaned_text'] = df_sample['cleaned_text'].str.replace(
    r'@\w+', '', regex=True)
df_sample['cleaned_text'] = df_sample['cleaned_text'].str.replace(
    r'#(\w+)', r'\1', regex=True)
df_sample['cleaned_text'] = df_sample['cleaned_text'].str.strip()

# Apply sentiment labeling
df_sample['sentiment'] = df_sample['text'].apply(assign_sentiment)

# Save as CSV
output_path = '/opt/airflow/data/processed/sentiment_results/mock_sentiment_results.csv'
print(f"Saving to {output_path}...")
df_sample.to_csv(output_path, index=False)

# Print summary
print(f"\n{'='*60}")
print(f"Mock dataset created with {len(df_sample)} tweets")
print(f"\nSentiment distribution:")
print(df_sample['sentiment'].value_counts())
print(f"\nFile saved to: {output_path}")
print(f"{'='*60}")
