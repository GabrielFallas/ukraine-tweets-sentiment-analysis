"""
Download Ukraine-Russia Crisis Twitter Dataset from Kaggle
Uses kagglehub to download the dataset directly
"""

import os
import sys
import shutil


def download_dataset():
    """Download dataset from Kaggle using kagglehub"""

    print("=" * 60)
    print("Ukraine Tweets Dataset Downloader")
    print("=" * 60)
    print()

    # Check if kagglehub is installed
    try:
        import kagglehub
        print("✓ kagglehub is installed")
    except ImportError:
        print("✗ kagglehub not found. Installing...")
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "kagglehub"])
        import kagglehub
        print("✓ kagglehub installed successfully")

    print()
    print("Downloading dataset from Kaggle...")
    print("This may take a few minutes depending on your connection...")
    print()

    try:
        # Download latest version
        path = kagglehub.dataset_download(
            "bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows")

        print()
        print("✓ Dataset downloaded successfully!")
        print(f"Path to dataset files: {path}")
        print()

        # List downloaded files
        print("Downloaded files:")
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(
                    file_path) / (1024 * 1024)  # Size in MB
                print(f"  - {file} ({file_size:.2f} MB)")

        print()

        # Find CSV files
        csv_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))

        if not csv_files:
            print("✗ No CSV files found in downloaded dataset")
            return False

        print(f"Found {len(csv_files)} CSV files")
        print("Merging all CSV files into one dataset...")
        print("This will take several minutes...")
        print()

        # Merge all CSV files
        dest_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
        dest_file = os.path.join(dest_dir, 'ukraine_tweets.csv')

        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)

        # Try to use pandas for efficient merging
        try:
            import pandas as pd

            print("Using pandas for efficient merging...")

            # Read and merge all CSV files
            all_dfs = []
            for i, csv_file in enumerate(csv_files, 1):
                if i % 50 == 0:
                    print(f"Processing file {i}/{len(csv_files)}...")
                try:
                    df = pd.read_csv(csv_file, low_memory=False)
                    all_dfs.append(df)
                except Exception as e:
                    print(
                        f"Warning: Skipping {os.path.basename(csv_file)}: {str(e)}")

            print(f"\nMerging {len(all_dfs)} dataframes...")
            combined_df = pd.concat(all_dfs, ignore_index=True)

            print(f"Writing merged dataset to: {dest_file}")
            combined_df.to_csv(dest_file, index=False)

            print(f"Total rows: {len(combined_df):,}")

        except ImportError:
            print("pandas not found. Installing pandas...")
            import subprocess
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pandas"])

            print("Please run the script again to merge the files.")
            return False

        print()
        print("=" * 60)
        print("✓ Dataset ready!")
        print("=" * 60)
        print()
        print(f"Dataset location: {dest_file}")
        print(
            f"File size: {os.path.getsize(dest_file) / (1024 * 1024):.2f} MB")
        print()
        print("Next steps:")
        print("1. Run: docker-compose build")
        print("2. Run: docker-compose up -d")
        print("3. Access Airflow at http://localhost:8080")
        print()

        return True

    except Exception as e:
        print()
        print(f"✗ Error downloading dataset: {str(e)}")
        print()
        print("Please ensure:")
        print("1. You have a Kaggle account")
        print("2. Kaggle API credentials are configured")
        print("   - Place kaggle.json in: ~/.kaggle/ (Linux/Mac)")
        print("   - Or: C:\\Users\\<username>\\.kaggle\\kaggle.json (Windows)")
        print()
        print("Get your API key from: https://www.kaggle.com/settings/account")
        print()
        return False


if __name__ == "__main__":
    success = download_dataset()
    sys.exit(0 if success else 1)
