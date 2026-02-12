FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# gcc and python3-dev might be needed for some packages, though standard django/drf usually don't need them on slim if wheels exist.
# kept minimal for now.
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
