"""
Create a test dataset with only 100 rows for quick pipeline verification
"""
import pandas as pd
import os


def create_test_sample():
    """Sample 100 rows from the dataset"""

    input_path = 'data/raw/ukraine_tweets.csv'
    output_path = 'data/raw/ukraine_tweets_sample_100.csv'

    print(f"Reading first 1000 rows from: {input_path}")

    # Read just the first 1000 rows to save time
    df = pd.read_csv(
        input_path,
        encoding='utf-8',
        nrows=1000,
        on_bad_lines='skip',
        low_memory=False
    )

    print(f"Read {len(df):,} rows")

    # Sample 100 rows randomly
    sample_size = 100
    df_sample = df.sample(n=min(sample_size, len(df)), random_state=42)

    print(f"Sampled {len(df_sample):,} rows")

    # Save the sampled dataset
    df_sample.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\nTest dataset saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")

    # Print sample statistics
    print("\n=== Test Dataset Info ===")
    print(f"Rows: {len(df_sample):,}")
    print(f"Columns: {len(df_sample.columns)}")
    print(f"\nColumn names: {list(df_sample.columns)}")
    print(f"\nFirst 3 rows:")
    print(df_sample.head(3))


if __name__ == "__main__":
    create_test_sample()
