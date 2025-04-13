#!/usr/bin/env python
import requests
import json
import time
import sys
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rabbitmq-setup')

# Konfiguracja połączenia do RabbitMQ
RABBITMQ_HOST = 'localhost'  # Zmień na odpowiedni host, jeśli potrzebne
RABBITMQ_MANAGEMENT_PORT = 15672
RABBITMQ_API_URL = f'http://{RABBITMQ_HOST}:{RABBITMQ_MANAGEMENT_PORT}/api'
RABBITMQ_USERNAME = 'admin'
RABBITMQ_PASSWORD = 'admin_password'

# Konfiguracja elementów do utworzenia
VHOST_NAME = 'my_app_vhost'
APP_USERNAME = 'app_user'
APP_PASSWORD = 'app_password'
APP_TAGS = 'monitoring'

# Definicje kolejek
QUEUES = [
    {
        'name': 'task_queue',
        'vhost': VHOST_NAME,
        'durable': True,
        'auto_delete': False,
        'arguments': {
            'x-queue-type': 'classic',
            'x-max-length': 10000,
            'x-message-ttl': 3600000  # 1 godzina
        }
    },
    {
        'name': 'notification_queue',
        'vhost': VHOST_NAME,
        'durable': True,
        'auto_delete': False,
        'arguments': {
            'x-queue-type': 'quorum',
            'x-max-length': 10000,
            'x-message-ttl': 86400000  # 24 godziny
        }
    }
]

# Definicje wymian
EXCHANGES = [
    {
        'name': 'task_exchange',
        'vhost': VHOST_NAME,
        'type': 'direct',
        'durable': True,
        'auto_delete': False,
        'internal': False,
        'arguments': {}
    },
    {
        'name': 'notification_exchange',
        'vhost': VHOST_NAME,
        'type': 'fanout',
        'durable': True,
        'auto_delete': False,
        'internal': False,
        'arguments': {}
    }
]

# Definicje powiązań
BINDINGS = [
    {
        'source': 'task_exchange',
        'vhost': VHOST_NAME,
        'destination': 'task_queue',
        'destination_type': 'queue',
        'routing_key': 'task',
        'arguments': {}
    },
    {
        'source': 'notification_exchange',
        'vhost': VHOST_NAME,
        'destination': 'notification_queue',
        'destination_type': 'queue',
        'routing_key': '',  # pusty dla fanout
        'arguments': {}
    }
]

def make_api_request(method, endpoint, data=None):
    """Wykonuje zapytanie do API RabbitMQ Management"""
    url = f"{RABBITMQ_API_URL}/{endpoint}"
    auth = (RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method.lower() == 'get':
            response = requests.get(url, auth=auth, headers=headers)
        elif method.lower() == 'put':
            response = requests.put(url, auth=auth, headers=headers, data=json.dumps(data) if data else None)
        elif method.lower() == 'post':
            response = requests.post(url, auth=auth, headers=headers, data=json.dumps(data) if data else None)
        elif method.lower() == 'delete':
            response = requests.delete(url, auth=auth, headers=headers)
        else:
            logger.error(f"Nieobsługiwana metoda: {method}")
            return False, None
        
        if response.status_code < 200 or response.status_code >= 300:
            logger.error(f"Błąd API ({response.status_code}): {response.text}")
            return False, response
        
        return True, response
    except requests.exceptions.RequestException as e:
        logger.error(f"Błąd zapytania: {e}")
        return False, None

def wait_for_rabbitmq():
    """Czeka aż RabbitMQ będzie dostępny"""
    max_attempts = 30
    attempt = 0
    
    logger.info(f"Czekam na dostępność RabbitMQ pod adresem {RABBITMQ_API_URL}...")
    
    while attempt < max_attempts:
        success, response = make_api_request('get', 'overview')
        if success:
            logger.info("RabbitMQ jest dostępny!")
            return True
        attempt += 1
        logger.info(f"Próba {attempt}/{max_attempts} nie powiodła się. Ponowna próba za 2 sekundy...")
        time.sleep(2)
    
    logger.error("Nie można połączyć się z RabbitMQ po wielu próbach.")
    return False

def create_vhost():
    """Tworzy host wirtualny"""
    logger.info(f"Tworzę host wirtualny: {VHOST_NAME}")
    success, response = make_api_request('put', f'vhosts/{VHOST_NAME}')
    if success:
        logger.info(f"Host wirtualny {VHOST_NAME} utworzony lub już istnieje.")
        return True
    return False

def create_user():
    """Tworzy użytkownika aplikacji"""
    logger.info(f"Tworzę użytkownika aplikacji: {APP_USERNAME}")
    
    # Sprawdź, czy użytkownik już istnieje
    success, response = make_api_request('get', 'users')
    if success:
        users = response.json()
        if any(user['name'] == APP_USERNAME for user in users):
            logger.info(f"Użytkownik {APP_USERNAME} już istnieje.")
            return True
    
    # Utwórz nowego użytkownika
    user_data = {
        'password': APP_PASSWORD,
        'tags': APP_TAGS
    }
    success, response = make_api_request('put', f'users/{APP_USERNAME}', user_data)
    if not success:
        logger.error("Nie udało się utworzyć użytkownika.")
        return False
    
    logger.info(f"Użytkownik {APP_USERNAME} utworzony pomyślnie.")
    return True

def set_permissions():
    """Ustawia uprawnienia dla użytkowników"""
    # Uprawnienia dla administratora
    logger.info(f"Ustawiam uprawnienia dla administratora w {VHOST_NAME}")
    admin_permissions = {
        'configure': '.*',
        'write': '.*',
        'read': '.*'
    }
    success, _ = make_api_request('put', f'permissions/{VHOST_NAME}/{RABBITMQ_USERNAME}', admin_permissions)
    if not success:
        logger.warning("Nie udało się ustawić uprawnień dla administratora.")
    
    # Uprawnienia dla użytkownika aplikacji
    logger.info(f"Ustawiam uprawnienia dla {APP_USERNAME} w {VHOST_NAME}")
    app_permissions = {
        'configure': '.*',
        'write': '.*',
        'read': '.*'
    }
    success, _ = make_api_request('put', f'permissions/{VHOST_NAME}/{APP_USERNAME}', app_permissions)
    if not success:
        logger.error(f"Nie udało się ustawić uprawnień dla {APP_USERNAME}.")
        return False
    
    logger.info("Uprawnienia ustawione pomyślnie.")
    return True

def create_queues():
    """Tworzy kolejki"""
    for queue in QUEUES:
        logger.info(f"Tworzę kolejkę: {queue['name']} w {queue['vhost']}")
        success, _ = make_api_request('put', f"queues/{queue['vhost']}/{queue['name']}", queue)
        if not success:
            logger.error(f"Nie udało się utworzyć kolejki {queue['name']}.")
            return False
        logger.info(f"Kolejka {queue['name']} utworzona pomyślnie.")
    
    return True

def create_exchanges():
    """Tworzy wymiany"""
    for exchange in EXCHANGES:
        logger.info(f"Tworzę wymianę: {exchange['name']} w {exchange['vhost']}")
        success, _ = make_api_request('put', f"exchanges/{exchange['vhost']}/{exchange['name']}", exchange)
        if not success:
            logger.error(f"Nie udało się utworzyć wymiany {exchange['name']}.")
            return False
        logger.info(f"Wymiana {exchange['name']} utworzona pomyślnie.")
    
    return True

def create_bindings():
    """Tworzy powiązania między wymianami a kolejkami"""
    for binding in BINDINGS:
        vhost = binding['vhost']
        source = binding['source']
        destination_type = binding['destination_type']
        destination = binding['destination']
        routing_key = binding['routing_key']
        
        logger.info(f"Tworzę powiązanie: {source} -> {destination} z kluczem {routing_key}")
        
        # Dla powiązań e-> kolejka format URL jest inny niż dla pozostałych typów
        endpoint = f"bindings/{vhost}/e/{source}/{destination_type[0]}/{destination}"
        success, _ = make_api_request('post', endpoint, {'routing_key': routing_key, 'arguments': binding['arguments']})
        if not success:
            logger.error(f"Nie udało się utworzyć powiązania {source} -> {destination}.")
            return False
        
        logger.info(f"Powiązanie {source} -> {destination} utworzone pomyślnie.")
    
    return True

def setup_rabbitmq():
    """Główna funkcja konfigurująca RabbitMQ"""
    logger.info("Rozpoczynam konfigurację RabbitMQ...")
    
    # Sprawdź, czy RabbitMQ jest dostępny
    if not wait_for_rabbitmq():
        return False
    
    # Wykonaj wszystkie kroki konfiguracji
    steps = [
        create_vhost,
        create_user,
        set_permissions,
        create_queues,
        create_exchanges,
        create_bindings
    ]
    
    for step in steps:
        if not step():
            logger.error(f"Krok {step.__name__} nie powiódł się. Przerywam konfigurację.")
            return False
    
    logger.info("Konfiguracja RabbitMQ zakończona pomyślnie!")
    return True

if __name__ == "__main__":
    success = setup_rabbitmq()
    sys.exit(0 if success else 1)