"""
Create a sampled dataset with 70,000 rows from the full Ukraine tweets dataset
Uses chunk reading to avoid memory issues with large datasets
"""
import pandas as pd
import os
import random


def create_sample_dataset():
    """Sample 70,000 rows from the original dataset using reservoir sampling"""

    input_path = 'data/raw/ukraine_tweets.csv'
    output_path = 'data/raw/ukraine_tweets_sample_70k.csv'

    print(f"Reading dataset from: {input_path}")

    sample_size = 70000
    chunk_size = 50000

    # Read in chunks and use reservoir sampling to get 70k random rows
    reservoir = []
    total_rows = 0
    header_saved = False
    header = None

    print("Reading file in chunks to avoid memory issues...")

    chunk_iterator = pd.read_csv(
        input_path,
        encoding='utf-8',
        chunksize=chunk_size,
        on_bad_lines='skip',
        low_memory=False
    )

    for chunk_num, chunk in enumerate(chunk_iterator, 1):
        print(f"Processing chunk {chunk_num} ({len(chunk):,} rows)...")

        if header is None:
            header = chunk.columns

        for _, row in chunk.iterrows():
            total_rows += 1

            if len(reservoir) < sample_size:
                # Fill the reservoir
                reservoir.append(row)
            else:
                # Reservoir sampling algorithm
                # Random chance to replace existing item
                j = random.randint(0, total_rows - 1)
                if j < sample_size:
                    reservoir[j] = row

        print(f"Total rows processed so far: {total_rows:,}")

        # Break if we have enough data for statistical significance
        if total_rows >= sample_size * 10:  # Process at least 10x the sample size
            print(
                f"Processed sufficient data ({total_rows:,} rows) for random sampling")
            break

    print(f"\nTotal rows processed: {total_rows:,}")
    print(
        f"Sampled {len(reservoir):,} rows ({(len(reservoir)/total_rows)*100:.2f}% of processed data)")

    # Convert reservoir to DataFrame
    df_sample = pd.DataFrame(reservoir, columns=header)

    # Save the sampled dataset
    df_sample.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\nSampled dataset saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

    # Print sample statistics
    print("\n=== Sample Dataset Info ===")
    print(f"Rows: {len(df_sample):,}")
    print(f"Columns: {len(df_sample.columns)}")
    print(f"\nColumn names: {list(df_sample.columns)}")
    print(f"\nFirst few rows:")
    print(df_sample.head())


if __name__ == "__main__":
    create_sample_dataset()
