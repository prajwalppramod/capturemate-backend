# Use Python 3.9 as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libx11-6 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libopenblas-dev \
    liblapack-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install face recognition models
RUN pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition_models --verbose

# Copy project files
COPY capturemate_app/ .

# Expose port
EXPOSE 3001

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:3001"] 