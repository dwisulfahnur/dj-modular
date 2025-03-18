FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=djmodular.settings

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run as non-root user for better security
RUN adduser --disabled-password --gecos '' django
RUN chown -R django:django /app
USER django

# Expose port for the Django application
EXPOSE 8000

# Command to run the server
CMD ["gunicorn", "djmodular.wsgi:application", "-w=1", "-b=0.0.0.0:8000"]
