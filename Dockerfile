# Use Red Hat Universal Base Image with Python 3.11
FROM registry.access.redhat.com/ubi9/python-311:latest

# Switch to root for installations
USER root

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create .streamlit directory and copy config
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/

# Create data directory for optional volume mounting
RUN mkdir -p /app/data

# Set proper permissions
RUN chmod -R 755 /app

# Switch back to non-root user for security
USER 1001

# Expose port 8501 (Streamlit's default port)
EXPOSE 8501

# Health check using curl-minimal (pre-installed in UBI9)
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl --fail --silent --max-time 10 http://localhost:8501/_stcore/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]