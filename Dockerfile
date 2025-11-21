# Use official Python 3.12 image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (optional — useful for many libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app with Uvicorn
# Replace "main:app" with your module and app name
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
