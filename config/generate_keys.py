"""
Generate required keys for the sentiment analysis pipeline
Run this script to automatically generate Fernet and Secret keys
"""

import secrets
import base64
import sys


def generate_fernet_key():
    """Generate a Fernet key for Airflow"""
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()


def generate_secret_key():
    """Generate a random secret key for Superset"""
    return base64.b64encode(secrets.token_bytes(32)).decode()


def update_env_file():
    """Update .env file with generated keys"""
    try:
        # Read .env.example or .env
        try:
            with open('.env', 'r') as f:
                content = f.read()
        except FileNotFoundError:
            with open('.env.example', 'r') as f:
                content = f.read()

        # Generate keys
        fernet_key = generate_fernet_key()
        secret_key = generate_secret_key()

        # Replace placeholders
        content = content.replace('your_fernet_key_here', fernet_key)
        content = content.replace('your_superset_secret_key_here', secret_key)

        # Write to .env
        with open('.env', 'w') as f:
            f.write(content)

        print("✅ Keys generated successfully!")
        print("\n" + "="*60)
        print("Generated Keys:")
        print("="*60)
        print(f"\nAIRFLOW_FERNET_KEY:\n{fernet_key}")
        print(f"\nSUPERSET_SECRET_KEY:\n{secret_key}")
        print("\n" + "="*60)
        print("\n✅ Keys have been saved to .env file")
        print("\nNext steps:")
        print("1. Download dataset to data/raw/ukraine_tweets.csv")
        print("2. Run: docker-compose build")
        print("3. Run: docker-compose up -d")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPlease ensure .env.example exists in the current directory")
        sys.exit(1)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Ukraine Tweets Sentiment Analysis Pipeline")
    print("Key Generation Script")
    print("="*60 + "\n")

    # Check if cryptography is installed
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("❌ Error: cryptography package not installed")
        print("\nInstalling required package...")
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "cryptography"])
        print("✅ Package installed successfully\n")

    # Generate and update keys
    update_env_file()


if __name__ == "__main__":
    main()
