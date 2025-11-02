#!/bin/bash

# Setup script for Ukraine Tweets Sentiment Analysis Pipeline
# Linux/Mac version

echo "============================================"
echo "Ukraine Tweets Sentiment Analysis Pipeline"
echo "Setup Script"
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

echo "[OK] Docker is installed"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: docker-compose is not installed"
    echo "Please install docker-compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[OK] docker-compose is installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "[OK] .env file created"
    echo ""
    echo "IMPORTANT: Please edit .env file and add your keys:"
    echo "  1. Generate Fernet key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    echo "  2. Generate Superset secret: openssl rand -base64 42"
    echo ""
else
    echo "[OK] .env file already exists"
    echo ""
fi

# Create data directories
mkdir -p data/raw data/processed
echo "[OK] Data directories created"
echo ""

# Create airflow directories
mkdir -p airflow/logs airflow/plugins
echo "[OK] Airflow directories created"
echo ""

# Create superset directories
mkdir -p superset/dashboards
echo "[OK] Superset directories created"
echo ""

# Make scripts executable
chmod +x scripts/init-databases.sh
chmod +x superset/init_superset.sh
chmod +x openmetadata/init_openmetadata.sh
echo "[OK] Scripts made executable"
echo ""

echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Edit .env file with your generated keys"
echo "2. Download the Ukraine tweets dataset from Kaggle:"
echo "   https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows"
echo "3. Place the CSV file in: data/raw/ukraine_tweets.csv"
echo "4. Run: docker-compose build"
echo "5. Run: docker-compose up -d"
echo "6. Wait 2-3 minutes for services to initialize"
echo "7. Access Airflow at http://localhost:8080 (admin/admin)"
echo ""
echo "For more information, see README.md"
echo ""
