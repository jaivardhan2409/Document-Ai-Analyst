FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create persistent data directory (HF Spaces mounts /data as persistent volume)
RUN mkdir -p /data/chroma_db /data/uploads && chmod -R 777 /data

# Copy all code into the container
COPY . .

# Install backend dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install frontend dependencies
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Set permissions for the run script
RUN chmod +x run.sh

# Expose the ports (HF uses 7860 by default)
EXPOSE 8000
EXPOSE 7860

# Run the startup script
CMD ["/bin/bash", "run.sh"]
