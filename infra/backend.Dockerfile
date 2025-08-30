# Use the official Python image as the base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app/backend

# Copy the requirements file into the container
COPY ./backend/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code into the container
COPY ./backend .

# Expose the port the FastAPI application will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]