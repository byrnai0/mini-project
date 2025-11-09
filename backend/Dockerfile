# Use Python 3.10 base image (required for Charm-crypto)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Charm-crypto
RUN apt-get update && apt-get install -y \
    build-essential \
    libgmp-dev \
    libssl-dev \
    python3-dev \
    m4 \
    flex \
    bison \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PBC library (required for Charm-crypto)
RUN cd /tmp && \
    wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && \
    tar xzf pbc-0.5.14.tar.gz && \
    cd pbc-0.5.14 && \
    ./configure LDFLAGS="-lgmp" && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/pbc-0.5.14*

# Install Charm-crypto from source
RUN cd /tmp && \
    git clone https://github.com/JHUISI/charm.git && \
    cd charm && \
    ./configure.sh && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/charm

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
