FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt README.md /app/
COPY reflex_app.py rxconfig.py /app/
COPY marker_converter/ /app/marker_converter/
COPY src/ /app/src/
COPY app/ /app/app/

# Install Python dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 3000 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# Run Reflex app
CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]
