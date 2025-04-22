# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt params.yaml dvc.yaml .dvcignore .gitignore /app/
COPY config.py main.py /app/
COPY scripts/ /app/scripts/

# Install Python dependencies and DVC
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && pip install dvc

# Make scripts executable
RUN chmod +x /app/scripts/*.py

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]