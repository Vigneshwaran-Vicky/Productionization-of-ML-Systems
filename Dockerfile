# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose correct port
EXPOSE 8501

# Run app
CMD ["python", "app.py"]