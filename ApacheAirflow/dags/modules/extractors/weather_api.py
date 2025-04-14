"""
Moduł odpowiedzialny za pobieranie danych z API pogodowego
"""
import logging
import requests
from datetime import datetime
import sys
import os

# Dodanie ścieżki projektu do sys.path, aby można było importować z config
sys.path.append('/opt/airflow')
from modules.config.config import API_KEY, CITIES

logger = logging.getLogger(__name__)

def fetch_weather_for_city(city):
    """
    Pobiera dane pogodowe dla pojedynczego miasta
    
    Args:
        city (str): Nazwa miasta
        
    Returns:
        dict: Dane pogodowe dla miasta lub None w przypadku błędu
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        weather_data = {
            'city': city,
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        logger.info(f"Pobrano dane dla miasta: {city}")
        return weather_data
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych dla miasta {city}: {e}")
        return None

def fetch_weather_data(**kwargs):
    """
    Pobiera dane pogodowe dla wszystkich miast zdefiniowanych w konfiguracji
    
    Returns:
        list: Lista słowników z danymi pogodowymi
    """
    results = []
    
    for city in CITIES:
        city_data = fetch_weather_for_city(city)
        if city_data:
            results.append(city_data)
    
    logger.info(f"Pobrano dane dla {len(results)} miast")
    return results