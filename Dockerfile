# Use the official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application code to the container
COPY . .

# Install system dependencies and Python dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port the Flask app runs on
EXPOSE 5000

# Set the entry point for the container
CMD ["python", "app.py"]

