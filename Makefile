.PHONY: install test test-unit test-bdd run-dev build run clean docker-up docker-down docker-logs

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test: test-unit test-bdd

# Run unit tests
test-unit:
	pytest tests/ -v

# Run BDD tests
test-bdd:
	behave features/

# Run development server
run-dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
build:
	docker build -t ant-colony-api .

# Run with Docker
run:
	docker run -p 8000:8000 ant-colony-api

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Docker Compose commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development with Docker Compose
docker-dev:
	docker-compose up --build

# Production deployment
docker-prod:
	docker-compose --profile production up -d

# Test in Docker
docker-test:
	docker build -t ant-colony-test .
	docker run --rm ant-colony-test pytest tests/ -v