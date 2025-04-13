FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the scripts executable
RUN chmod +x producer.py consumer.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command will be specified in docker-compose.yml
CMD ["echo", "Specify a command in docker-compose.yml"]