import json
import re
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ініціалізація логера
logger = logging.getLogger("signal_bot")

BASE_DIR = Path(__file__).parent.parent

class Config:
    # Pocket Option
    POCKET_SSID = os.getenv('POCKET_SSID')
    POCKET_DEMO = os.getenv('POCKET_DEMO', 'true').lower() == 'true'
    
    # ... інші налаштування ...
    
    @staticmethod
    def validate_ssid_format(ssid):
        """Перевіряє чи SSID у правильному форматі"""
        if not ssid:
            return False, "SSID порожній"
        
        # Перевірка формату
        pattern = r'^42\["auth",\{.*\}\]$'
        if not re.match(pattern, ssid):
            return False, f"Неправильний формат SSID"
        
        return True, "SSID валідний"
    
    @classmethod
    def get_validated_ssid(cls):
        """Повертає валідований SSID"""
        ssid = cls.POCKET_SSID
        
        if not ssid:
            logger.error("SSID не знайдено! Перевірте .env або GitHub Secrets")
            return None
        
        # Якщо SSID не у повному форматі, конвертуємо
        if ssid and not ssid.startswith('42["auth"'):
            logger.warning(f"SSID не у повному форматі, конвертую...")
            logger.info(f"Оригінальний SSID: {ssid[:50]}...")
            
            # Конвертуємо у повний формат
            ssid = f'42["auth",{{"session":"{ssid}","isDemo":1,"uid":12345,"platform":1}}]'
            logger.info(f"Конвертований SSID: {ssid[:50]}...")
        
        is_valid, message = cls.validate_ssid_format(ssid)
        
        if is_valid:
            logger.info(f"✅ SSID валідний ({len(ssid)} символів)")
        else:
            logger.error(f"❌ Помилка валідації SSID: {message}")
            logger.error(f"SSID: {ssid[:100]}...")
        
        return ssid
