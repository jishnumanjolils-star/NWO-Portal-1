# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 7860

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (UID 1000 required by Hugging Face)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install dependencies
COPY requirements.txt /home/user/app/
RUN pip install --upgrade pip && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

# Copy project files and change ownership
COPY --chown=user:user . /home/user/app/

# Set executable permissions for scripts
RUN chmod +x start.sh build.sh

# Switch to the non-root user
USER user

# Collect static files during build
RUN python manage.py collectstatic --noinput --clear || true

# Run startup script
CMD ["bash", "start.sh"]
