FROM python:3.12.5-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Update and install essential build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy necessary files for dependency installation
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi

# Optional: Install watchdog for development environment
ARG ENV=prod
RUN if [ "$ENV" = "dev" ]; then \
    poetry add watchdog --dev; \
  fi

# Copy the rest of the project files
COPY . .

# Copy the migration script and set permissions
RUN chmod +x /app/scripts/run_migration.sh

# Copy the entrypoint script and set execute permission
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Debug: List the file permissions to confirm
RUN ls -l /app/entrypoint.sh
RUN ls -l /app/scripts/run_migration.sh

# Expose the required port for the service
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
