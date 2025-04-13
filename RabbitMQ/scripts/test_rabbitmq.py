#!/usr/bin/env python
import pika
import json
import time
import random
import logging
import argparse
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rabbitmq-test')

# Konfiguracja połączenia
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5672
DEFAULT_VHOST = 'my_app_vhost'
DEFAULT_USER = 'app_user'
DEFAULT_PASS = 'app_password'

def parse_arguments():
    """Parsuje argumenty wiersza poleceń"""
    parser = argparse.ArgumentParser(description='Test RabbitMQ - wysyłanie wiadomości')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host RabbitMQ (domyślnie: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port RabbitMQ (domyślnie: {DEFAULT_PORT})')
    parser.add_argument('--vhost', default=DEFAULT_VHOST, help=f'Host wirtualny (domyślnie: {DEFAULT_VHOST})')
    parser.add_argument('--user', default=DEFAULT_USER, help=f'Nazwa użytkownika (domyślnie: {DEFAULT_USER})')
    parser.add_argument('--password', default=DEFAULT_PASS, help=f'Hasło (domyślnie: {DEFAULT_PASS})')
    parser.add_argument('--task-count', type=int, default=10, help='Liczba zadań do wysłania (domyślnie: 10)')
    parser.add_argument('--notify-count', type=int, default=3, help='Liczba powiadomień do wysłania (domyślnie: 3)')
    parser.add_argument('--stress-test', action='store_true', help='Wykonaj test obciążeniowy (1000 wiadomości)')
    return parser.parse_args()

def connect_to_rabbitmq(host, port, vhost, username, password):
    """Nawiązuje połączenie z RabbitMQ i zwraca obiekt połączenia oraz kanał"""
    logger.info(f"Łączenie z RabbitMQ: {host}:{port}, vhost: {vhost}")
    
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=vhost,
        credentials=credentials,
        heartbeat=600,
        connection_attempts=3,
        retry_delay=5
    )
    
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        # Potwierdzenie dostarczenia
        channel.confirm_delivery()
        logger.info("Połączono z RabbitMQ pomyślnie")
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Błąd połączenia z RabbitMQ: {e}")
        raise
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {e}")
        raise

def send_task(channel, task_id, task_type="test", priority=5):
    """Wysyła wiadomość zadania do odpowiedniej wymiany"""
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
        headers={'source': 'test_script'}
    )
    
    try:
        channel.basic_publish(
            exchange='task_exchange',
            routing_key='task',
            body=json.dumps(message),
            properties=properties,
            mandatory=True
        )
        logger.info(f"Wysłano zadanie: {task_id}, typ: {task_type}, priorytet: {priority}")
        return True
    except pika.exceptions.UnroutableError:
        logger.error(f"Wiadomość nie mogła być przekazana: {task_id}")
        return False
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania zadania: {e}")
        return False

def send_notification(channel, notification_id, subject, content):
    """Wysyła powiadomienie do wszystkich zainteresowanych subskrybentów"""
    message = {
        'notification_id': notification_id,
        'type': "test_notification",
        'subject': subject,
        'content': content,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=2,  # persistent message
        message_id=f"notification-{notification_id}",
        timestamp=int(time.time())
    )
    
    try:
        channel.basic_publish(
            exchange='notification_exchange',
            routing_key='',  # fanout exchange ignores routing key
            body=json.dumps(message),
            properties=properties
        )
        logger.info(f"Wysłano powiadomienie: {subject}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania powiadomienia: {e}")
        return False

def run_stress_test(channel, message_count=1000):
    """Wykonuje test obciążeniowy wysyłając dużą liczbę wiadomości"""
    logger.info(f"Rozpoczynam test obciążeniowy - wysyłam {message_count} wiadomości...")
    start_time = time.time()
    
    success_count = 0
    
    for i in range(message_count):
        task_id = 10000 + i
        task_type = random.choice(['process', 'analyze', 'report', 'update'])
        priority = random.randint(1, 10)
        
        if send_task(channel, task_id, task_type, priority):
            success_count += 1
        
        if i % 100 == 0 and i > 0:
            logger.info(f"Wysłano {i} wiadomości ({success_count} pomyślnie)...")
        
        # Małe opóźnienie, aby nie obciążać systemu zbyt mocno
        time.sleep(0.01)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    rate = message_count / elapsed_time
    
    logger.info(f"Test obciążeniowy zakończony!")
    logger.info(f"Wysłano: {success_count}/{message_count} wiadomości")
    logger.info(f"Czas wykonania: {elapsed_time:.2f} sekund")
    logger.info(f"Szybkość: {rate:.2f} wiadomości na sekundę")

def main():
    """Główna funkcja programu"""
    args = parse_arguments()
    
    try:
        connection, channel = connect_to_rabbitmq(
            args.host, args.port, args.vhost, args.user, args.password
        )
        
        if args.stress_test:
            run_stress_test(channel)
        else:
            # Wysyłanie zadań
            logger.info(f"Wysyłam {args.task_count} zadań...")
            for i in range(args.task_count):
                task_id = i + 1
                task_type = random.choice(['process', 'analyze', 'report', 'update'])
                priority = random.randint(1, 10)
                send_task(channel, task_id, task_type, priority)
                time.sleep(0.2)  # Krótka przerwa między zadaniami
            
            # Wysyłanie powiadomień
            logger.info(f"Wysyłam {args.notify_count} powiadomień...")
            for i in range(args.notify_count):
                notification_id = i + 1
                subject = f"Test Notification {notification_id}"
                content = f"This is test notification content #{notification_id}"
                send_notification(channel, notification_id, subject, content)
                time.sleep(0.2)  # Krótka przerwa między powiadomieniami
        
        # Zakończenie połączenia
        connection.close()
        logger.info("Zakończono wysyłanie wiadomości")
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Błąd połączenia z RabbitMQ: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Przerwano przez użytkownika")
        return 0
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())