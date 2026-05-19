# Use a lightweight Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Flask app setup (using python directly since it's a DispatcherMiddleware)
ENV FLASK_ENV=development

# Expose port 5000 for the Flask app
EXPOSE 5000

# Start the app using python (not flask run, since it's not a standard Flask app)
CMD ["python", "app/app.py"]
