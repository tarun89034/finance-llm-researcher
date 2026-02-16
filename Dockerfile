FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime libs and musl for compatibility with abetlen wheels
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    libgomp1 \
    musl \
    && rm -rf /var/lib/apt/lists/*

# Fix for missing musl libc on Debian
RUN ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1

# Install llama-cpp-python first using pre-built wheels
RUN pip install --no-cache-dir \
    llama-cpp-python==0.3.2 \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu \
    --only-binary :all:

# Copy and install other Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create models directory for model downloads
RUN mkdir -p /app/models

# Create a non-root user (required by HF Spaces)
RUN useradd -m -u 1000 user && \
    chown -R user:user /app
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
