# Use the official Python slim image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY app.py .

# Expose the Flask app port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
