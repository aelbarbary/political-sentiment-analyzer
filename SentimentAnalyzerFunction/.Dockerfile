# Use an official Python 3.12 image as a base (Ubuntu image or official python base)
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /var/task

# Install necessary system dependencies (this may vary based on your dependencies)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the Python dependencies in the container's /var/task directory
RUN pip install openai pydantic -t .

# This step ensures the dependencies are placed in the working directory
