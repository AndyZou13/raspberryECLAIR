# syntax=docker/dockerfile:1

# Set base image (host OS)
FROM python:3.12

# By default, listen on port 5000
EXPOSE 8000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .

# Specify the command to run on container start
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]