# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy everything in the current directory to the container's working directory
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point for the scheduled programs
CMD [ "python", "scheduler.py" ]
