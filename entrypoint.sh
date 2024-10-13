#!/bin/bash
set -e



# Ensure the MODE environment variable is set
if [ -z "$MODE" ]; then
  echo "Error: MODE environment variable is not set."
  echo "Please set the MODE environment variable to 'api', 'worker', 'beat', 'flower', or 'debug'."
  exit 1
fi

# Ensure the ENV environment variable is set (dev or prod)
if [ -z "$ENV" ]; then
  echo "Warning: ENV environment variable is not set. Defaulting to 'prod'."
  ENV="prod"
fi

# Function to start the Celery healthcheck service
start_healthcheck() {
  echo "Starting Celery healthcheck service..."
  python -m uvicorn api_template.celery.health_check:router --host 0.0.0.0 --port 8001 &
}

# Function to check if a service is ready
wait_for_service() {
  echo "Waiting for $1 to be ready..."
  until nc -z $2 $3; do
    echo "$1 is unavailable - sleeping"
    sleep 1
  done
  echo "$1 is up - executing command"
}

# Wait for dependent services
wait_for_service "RabbitMQ" ${RABBITMQ_HOST:-rabbitmq} ${RABBITMQ_PORT:-5672}
wait_for_service "Redis" ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}

# Function to run database migrations
run_migrations() {
  echo "Running database migrations..."
  /app/scripts/run_migration.sh || {
    echo "Database migration failed. Exiting...";
    exit 1;
  }
}

# Trap SIGTERM
trap 'echo "Received SIGTERM. Shutting down..."; kill -TERM $PID; wait $PID' TERM

# Start the correct service based on the MODE environment variable
if [ "$MODE" = "api" ]; then
    echo "Starting API service..."
    run_migrations  # Run migrations before starting the API
    if [ "$ENV" = "dev" ]; then
      # Development mode with live reload
      exec uvicorn api_template.server:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload --log-level debug
    else
      # Production mode
      exec uvicorn api_template.server:app --host 0.0.0.0 --port ${API_PORT:-8000} --workers ${API_WORKERS:-4} --log-config /app/log_config.json
    fi
elif [ "$MODE" = "worker" ]; then
    echo "Starting Celery worker..."
    start_healthcheck  # Start healthcheck service before launching the worker
    if [ "$ENV" = "dev" ]; then
      # Development mode with autoreload
      exec celery -A api_template.celery.app.celery_app worker --loglevel=${LOG_LEVEL:-info} --pool=solo &
    else
      # Production mode
      exec celery -A api_template.celery.app.celery_app worker --loglevel=${LOG_LEVEL:-info} &
    fi
    PID=$!
    wait $PID
elif [ "$MODE" = "beat" ]; then
    echo "Starting Celery beat..."
    exec celery -A api_template.celery.app.celery_app beat --loglevel=${LOG_LEVEL:-info} &
    PID=$!
    wait $PID
elif [ "$MODE" = "flower" ]; then
    echo "Starting Flower Monitoring..."
    exec celery -A api_template.celery.app.celery_app flower &
    PID=$!
    wait $PID
elif [ "$MODE" = "debug" ]; then
    echo "Starting in debug mode..."
    exec uvicorn api_template.server:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload --log-level debug
else
    echo "Invalid MODE. Use 'api', 'worker', 'beat', 'flower', or 'debug'."
    exit 1
fi
