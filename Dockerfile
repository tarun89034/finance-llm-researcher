FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for llama-cpp-python compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Copy application code
COPY app/ ./app/

# Create models directory for model downloads
RUN mkdir -p /app/app/models

# Create a non-root user (required by HF Spaces)
RUN useradd -m -u 1000 user
USER user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Launch Streamlit
CMD ["streamlit", "run", "app/app.py", "--server.port=7860", "--server.address=0.0.0.0"]
