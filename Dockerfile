# Use an official Airflow image as the base image
FROM apache/airflow:2.8.2-python3.11

# Set the working directory to the Airflow home directory
WORKDIR /opt/airflow_app

# Copy the project files to the container
COPY requirements.txt /opt/airflow_app/requirements.txt

# Switch back to root to install Chromium and Chromedriver
USER root

# Setup Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver 

USER airflow
# Install any additional dependencies
RUN pip install -r /opt/airflow_app/requirements.txt
