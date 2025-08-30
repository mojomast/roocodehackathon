# Use the official Python image as the base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app/worker

# Copy the requirements file into the container
COPY ./worker/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the worker code into the container
COPY ./worker .

# Command to run the Celery worker
CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]