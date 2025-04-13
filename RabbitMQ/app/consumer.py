#!/usr/bin/env python
import pika
import json
import time
import logging
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RabbitMQ connection settings
RABBITMQ_HOST = 'rabbitmq-broker'  # ZMIANA Z 'localhost' na 'rabbitmq-broker'
RABBITMQ_PORT = 5672
RABBITMQ_VHOST = 'my_app_vhost'
RABBITMQ_USER = 'app_user'
RABBITMQ_PASS = 'app_password'

# Queue names
TASK_QUEUE = 'task_queue'
NOTIFICATION_QUEUE = 'notification_queue'

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
    
    # Set QoS (prefetch_count)
    channel.basic_qos(prefetch_count=1)
    
    return connection, channel

def process_task(body, properties):
    """Process a task message"""
    try:
        message = json.loads(body)
        task_id = message.get('task_id')
        task_type = message.get('task_type')
        priority = message.get('priority', 5)
        data = message.get('data', {})
        
        logger.info(f"Processing task {task_id} of type {task_type} with priority {priority}")
        
        # Simulate processing time based on priority
        # Higher priority tasks are processed faster
        processing_time = max(1, 10 - priority)
        time.sleep(processing_time)
        
        # Process the task data (this is just a simulation)
        value = data.get('value', 0)
        result = value * 2  # Just a dummy calculation
        
        logger.info(f"Task {task_id} processed successfully. Result: {result}")
        return True
        
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON message")
        return False
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return False

def process_notification(body, properties):
    """Process a notification message"""
    try:
        message = json.loads(body)
        notification_type = message.get('type')
        subject = message.get('subject')
        content = message.get('content')
        
        logger.info(f"Received notification: {subject}")
        logger.info(f"Type: {notification_type}, Content: {content}")
        
        # Simulate some processing
        time.sleep(0.5)
        
        logger.info("Notification processed")
        return True
        
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON notification")
        return False
    except Exception as e:
        logger.error(f"Error processing notification: {e}")
        return False

def task_callback(channel, method, properties, body):
    """Callback function for task queue messages"""
    logger.info(f"Received task message with ID: {properties.message_id}")
    
    try:
        success = process_task(body, properties)
        
        if success:
            # Acknowledge the message (remove it from the queue)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Reject the message and requeue it
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        logger.error(f"Error in task callback: {e}")
        # Reject and requeue on exception
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def notification_callback(channel, method, properties, body):
    """Callback function for notification queue messages"""
    logger.info(f"Received notification message with ID: {properties.message_id}")
    
    try:
        success = process_notification(body, properties)
        
        if success:
            # Acknowledge the message
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Reject the message but don't requeue (notifications are less critical)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    except Exception as e:
        logger.error(f"Error in notification callback: {e}")
        # Reject without requeuing
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer(queue_name, callback):
    """Start a consumer for the specified queue with the given callback"""
    try:
        connection, channel = connect_to_rabbitmq()
        logger.info(f"Connected to RabbitMQ, consuming from {queue_name}")
        
        # Set up consuming
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        # Start consuming
        logger.info(f"Starting to consume from {queue_name}...")
        channel.start_consuming()
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"AMQP Connection error: {e}")
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if connection and connection.is_open:
            connection.close()

def main():
    """Main function to start both consumers in separate threads"""
    # Create threads for each consumer
    task_thread = threading.Thread(
        target=start_consumer,
        args=(TASK_QUEUE, task_callback),
        daemon=True
    )
    
    notification_thread = threading.Thread(
        target=start_consumer,
        args=(NOTIFICATION_QUEUE, notification_callback),
        daemon=True
    )
    
    # Start the threads
    task_thread.start()
    notification_thread.start()
    
    logger.info("Both consumers started. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Application shutdown initiated")

if __name__ == "__main__":
    main()