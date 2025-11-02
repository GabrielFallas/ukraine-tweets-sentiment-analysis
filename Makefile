# Makefile for Ukraine Tweets Sentiment Analysis Pipeline

.PHONY: help setup build up down logs clean restart status

help:
	@echo "Ukraine Tweets Sentiment Analysis Pipeline"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make setup     - Initial setup (create env file)"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View all logs"
	@echo "  make status    - Check service status"
	@echo "  make clean     - Stop and remove all volumes"
	@echo "  make airflow   - View Airflow logs"
	@echo "  make spark     - View Spark logs"
	@echo "  make druid     - View Druid logs"
	@echo "  make superset  - View Superset logs"
	@echo ""

setup:
	@echo "Setting up environment..."
	@if not exist .env (copy .env.example .env && echo .env file created. Please edit it with your keys.) else (echo .env file already exists.)
	@if not exist data\raw mkdir data\raw
	@if not exist data\processed mkdir data\processed
	@echo "Setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .env file with your Fernet and Secret keys"
	@echo "2. Download dataset to data/raw/ukraine_tweets.csv"
	@echo "3. Run 'make build' to build Docker images"

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services starting... Wait 2-3 minutes for initialization"
	@echo "Access points:"
	@echo "  Airflow:       http://localhost:8080"
	@echo "  Spark Master:  http://localhost:8081"
	@echo "  Druid:         http://localhost:8888"
	@echo "  Superset:      http://localhost:8088"
	@echo "  OpenMetadata:  http://localhost:8585"

down:
	@echo "Stopping all services..."
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

status:
	@echo "Service Status:"
	@docker-compose ps

clean:
	@echo "WARNING: This will remove all data volumes!"
	@echo "Press Ctrl+C to cancel, or"
	@pause
	docker-compose down -v
	@echo "All volumes removed."

airflow:
	docker-compose logs -f airflow-webserver airflow-scheduler

spark:
	docker-compose logs -f spark-master spark-worker

druid:
	docker-compose logs -f druid-coordinator druid-broker druid-historical

superset:
	docker-compose logs -f superset

test-spark:
	@echo "Testing Spark connectivity..."
	docker exec -it sentiment-spark-master spark-submit --version

test-airflow:
	@echo "Testing Airflow..."
	docker exec -it sentiment-airflow-webserver airflow version

shell-spark:
	docker exec -it sentiment-spark-master bash

shell-airflow:
	docker exec -it sentiment-airflow-webserver bash

shell-postgres:
	docker exec -it sentiment-postgres psql -U airflow -d airflow
