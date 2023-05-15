# Use the official Python runtime as a parent image
FROM python:3.11-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]

# End of Flask-specific setup

# Install SQLite and create database file
# RUN apt-get update && apt-get install -y sqlite3 && \
#     sqlite3 /app/data.db "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT)"

# Start the database service
# CMD ["sqlite3", "/app/data.db"]
