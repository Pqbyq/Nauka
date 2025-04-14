"""
Moduł konfigurujący logowanie dla projektu
"""
import logging
import sys
import os

# Dodanie ścieżki projektu do sys.path, aby można było importować z config
sys.path.append('/opt/airflow')
from modules.config.config import DATA_FOLDER

def setup_logger(name):
    """
    Konfiguruje i zwraca logger dla danego modułu
    
    Args:
        name (str): Nazwa modułu (zwykle __name__)
        
    Returns:
        logging.Logger: Skonfigurowany logger
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(name)
    
    # Ustawienie poziomu logowania z konfiguracji
    log_level = getattr(logging, LOG_LEVEL)
    logger.setLevel(log_level)
    
    # Handler stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger