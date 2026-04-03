# Tanzania Stock Market AI - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5001

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/api/health || exit 1

# Start the application
CMD ["python", "instant_ml_api.py"]
