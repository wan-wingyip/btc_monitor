FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]