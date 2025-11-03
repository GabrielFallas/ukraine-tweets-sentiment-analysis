"""
View and analyze the sentiment analysis results
"""
import pandas as pd

# Load the results with error handling
df = pd.read_csv('data/processed/sentiment_results.csv',
                 on_bad_lines='skip',
                 engine='python',
                 encoding='utf-8')

print("=" * 80)
print("UKRAINE TWEETS SENTIMENT ANALYSIS RESULTS")
print("=" * 80)

# Basic info
print(f"\nTotal tweets analyzed: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Sentiment distribution
print("\n=== Sentiment Distribution ===")
sentiment_counts = df['sentiment'].value_counts()
for sentiment, count in sentiment_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{sentiment}: {count} ({percentage:.1f}%)")

# Show some examples
print("\n=== Sample Tweets (First 5) ===")
for idx, row in df.head(5).iterrows():
    print(f"\n{idx + 1}. User: @{row['username']}")
    print(f"   Sentiment: {row['sentiment']}")
    print(f"   Tweet: {row['text'][:100]}...")
    print(f"   Cleaned: {row['cleaned_text'][:100]}...")

# Export summary
print("\n=== Summary Statistics ===")
# Create summary statistics
summary = {
    'Total Tweets': len(df),
    'Positive': sentiment_counts.get('POSITIVE', 0),
    'Negative': sentiment_counts.get('NEGATIVE', 0),
    'Neutral': sentiment_counts.get('NEUTRAL', 0),
    'Average Followers': df['followers'].mean(),
    'Average Retweets': df['retweetcount'].mean(),
}

print(f"Total Tweets: {summary['Total Tweets']}")
print(
    f"Positive: {summary['Positive']} ({summary['Positive']/summary['Total Tweets']*100:.1f}%)")
print(
    f"Negative: {summary['Negative']} ({summary['Negative']/summary['Total Tweets']*100:.1f}%)")
print(
    f"Neutral: {summary['Neutral']} ({summary['Neutral']/summary['Total Tweets']*100:.1f}%)")
print(f"Average Followers: {summary['Average Followers']:.0f}")
print(f"Average Retweets: {summary['Average Retweets']:.1f}")

summary_df = pd.DataFrame([summary])
summary_df.to_csv('data/processed/summary_statistics.csv', index=False)
print("\n✓ Saved summary statistics to: data/processed/summary_statistics.csv")
print("✓ Results file available at: data/processed/sentiment_results.csv")
