FROM python:3.12-slim-bookworm

#Set environment variables for python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

#Set the working directory in the container
WORKDIR /app

#Install system dependencies needed for PostgreSQL client (psycopg2-binary) and git
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the requirements file into the container
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files into the container
COPY manage.py /app/manage.py
COPY nexus_commerce /app/nexus_commerce
COPY users /app/users

# Expose the port the Django project will run on
EXPOSE 8000

# Default command to run
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]