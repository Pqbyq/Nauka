#!/usr/bin/env python
import pika
import json
import time
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RabbitMQ connection settings
RABBITMQ_HOST = 'localhost'  # Use 'rabbitmq-broker' if running in docker network
RABBITMQ_PORT = 5672
RABBITMQ_VHOST = 'my_app_vhost'
RABBITMQ_USER = 'app_user'
RABBITMQ_PASS = 'app_password'

# Exchange and routing settings
TASK_EXCHANGE = 'task_exchange'
TASK_ROUTING_KEY = 'task'
NOTIFICATION_EXCHANGE = 'notification_exchange'

def connect_to_rabbitmq():
    """Establish connection to RabbitMQ and return the connection and channel"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        connection_attempts=3,
        retry_delay=5
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Confirm delivery
    channel.confirm_delivery()
    
    return connection, channel

def publish_task_message(channel, task_id, task_type, priority=5):
    """Publish a task message to the task exchange"""
    message = {
        'task_id': task_id,
        'task_type': task_type,
        'priority': priority,
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'value': random.randint(1, 100),
            'description': f"Task data for task {task_id}"
        }
    }
    
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=2,  # persistent message
        priority=priority,
        message_id=str(task_id),
        timestamp=int(time.time()),
        headers={'source': 'producer_app'}
    )
    
    try:
        channel.basic_publish(
            exchange=TASK_EXCHANGE,
            routing_key=TASK_ROUTING_KEY,
            body=json.dumps(message),
            properties=properties,
            mandatory=True
        )
        logger.info(f"Published task message: {task_id}")
        return True
    except pika.exceptions.UnroutableError:
        logger.error(f"Message could not be routed: {task_id}")
        return False

def publish_notification(channel, notification_type, subject, content):
    """Publish a notification to all interested subscribers"""
    message = {
        'notification_id': random.randint(10000, 99999),
        'type': notification_type,
        'subject': subject,
        'content': content,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=2,  # persistent message
        message_id=f"notification-{int(time.time())}-{random.randint(1000, 9999)}",
        timestamp=int(time.time())
    )
    
    try:
        channel.basic_publish(
            exchange=NOTIFICATION_EXCHANGE,
            routing_key='',  # fanout exchange ignores routing key
            body=json.dumps(message),
            properties=properties
        )
        logger.info(f"Published notification: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error publishing notification: {e}")
        return False

def main():
    """Main function to demonstrate producing messages"""
    try:
        connection, channel = connect_to_rabbitmq()
        logger.info("Connected to RabbitMQ successfully")
        
        # Publish 10 task messages
        for i in range(10):
            task_id = i + 1
            task_type = random.choice(['process', 'analyze', 'report', 'update'])
            priority = random.randint(1, 10)
            
            publish_task_message(channel, task_id, task_type, priority)
            time.sleep(0.5)  # Small delay between messages
        
        # Publish a notification
        publish_notification(
            channel,
            "system_update",
            "System Maintenance",
            "The system will be undergoing maintenance in 30 minutes."
        )
        
        connection.close()
        logger.info("Connection closed")
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()