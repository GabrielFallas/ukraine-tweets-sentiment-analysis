"""
Create a 100,000 row sample dataset for pipeline testing
"""
import pandas as pd
import os


def create_100k_sample():
    """Sample 100,000 rows from the dataset"""

    input_path = 'data/raw/ukraine_tweets.csv'
    output_path = 'data/raw/ukraine_tweets_sample_100000.csv'

    print(f"Reading first 100,000 rows from: {input_path}")

    # Read the first 100,000 rows
    df = pd.read_csv(
        input_path,
        encoding='utf-8',
        nrows=100000,
        on_bad_lines='skip',
        low_memory=False
    )

    print(f"Read {len(df):,} rows")

    # Save the dataset
    df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\n100K dataset saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")

    # Print sample statistics
    print("\n=== 100K Dataset Info ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"\nColumn names: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))


if __name__ == "__main__":
    create_100k_sample()
