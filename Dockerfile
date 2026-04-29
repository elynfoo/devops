# Use a lightweight Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Flask app setup
ENV FLASK_APP=app.py:application
ENV FLASK_ENV=development

# Expose port 5000 for the Flask app
EXPOSE 5000

# Start the Flask development server on all interfaces
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
