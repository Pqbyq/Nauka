"""
Moduł do przetwarzania danych pogodowych
"""
import logging

logger = logging.getLogger(__name__)

def categorize_temperature(temp):
    """
    Kategoryzuje temperaturę na podstawie wartości
    
    Args:
        temp (float): Temperatura w stopniach Celsjusza
        
    Returns:
        str: Kategoria temperatury ('cold', 'moderate', 'warm')
    """
    if temp < 10:
        return 'cold'
    elif temp < 20:
        return 'moderate'
    else:
        return 'warm'

def celsius_to_fahrenheit(celsius):
    """
    Konwertuje temperaturę z Celsjusza na Fahrenheita
    
    Args:
        celsius (float): Temperatura w stopniach Celsjusza
        
    Returns:
        float: Temperatura w stopniach Fahrenheita
    """
    return (celsius * 9/5) + 32

def enrich_weather_data(weather_item):
    """
    Wzbogaca pojedynczy element danych pogodowych o dodatkowe informacje
    
    Args:
        weather_item (dict): Pojedynczy element danych pogodowych
        
    Returns:
        dict: Wzbogacony element danych
    """
    enriched_item = weather_item.copy()
    
    # Dodanie temperatury w Fahrenheitach
    enriched_item['temperature_f'] = celsius_to_fahrenheit(weather_item['temperature'])
    
    # Kategoryzacja temperatury
    enriched_item['temp_category'] = categorize_temperature(weather_item['temperature'])
    
    # Dodatkowe pola można dodać tutaj
    
    return enriched_item

def process_weather_data(**kwargs):
    """
    Przetwarza dane pogodowe pozyskane z API
    
    Args:
        **kwargs: Argumenty przekazane przez Airflow, w tym ti (TaskInstance)
        
    Returns:
        list: Lista przetworzonych danych pogodowych
    """
    # Pobierz dane z poprzedniego zadania
    ti = kwargs['ti']
    weather_data = ti.xcom_pull(task_ids='fetch_weather_data')
    
    if not weather_data:
        logger.warning("Brak danych do przetworzenia!")
        return []
    
    processed_data = []
    
    for weather_item in weather_data:
        processed_item = enrich_weather_data(weather_item)
        processed_data.append(processed_item)
    
    logger.info(f"Przetworzono dane dla {len(processed_data)} miast")
    return processed_data