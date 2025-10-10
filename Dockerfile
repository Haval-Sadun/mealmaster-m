FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app    

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

EXPOSE 8000

# Use ASGI entry point from mainapp
CMD ["uvicorn", "mainapp.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
