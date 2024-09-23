# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and buffer issues
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for mysqlclient
# RUN apt-get update && apt-get install -y \
#     default-libmysqlclient-dev \
#     gcc \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first for better caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the Django app runs on
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
