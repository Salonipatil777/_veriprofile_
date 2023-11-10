FROM python:3.10-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE veriprofile.settings

# Create and set the working directory
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port on which the ASGI application will run
EXPOSE 8000

# Start the ASGI application using Gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "veriprofile.asgi:application"]

