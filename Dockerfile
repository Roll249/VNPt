# VNPT AI Hackathon - Optimized Dockerfile
# Base image with CUDA 12.2 (as required)
FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Set working directory
WORKDIR /code

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce image size
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /code/data /code/output

# Default command
CMD ["bash", "inference.sh"]
