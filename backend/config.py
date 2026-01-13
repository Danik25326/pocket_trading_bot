import os
import sys
import json
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import pytz

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

logger = logging.getLogger("signal_bot")

BASE_DIR = Path(__file__).parent.parent

class Config:
    # Pocket Option
    POCKET_SSID = os.getenv('POCKET_SSID')
    POCKET_DEMO = os.getenv('POCKET_DEMO', 'false').lower() == 'true'
    
    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
    
    # Сигнали
    SIGNAL_INTERVAL = int(os.getenv('SIGNAL_INTERVAL', 600))
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.75))
    MAX_DURATION = float(os.getenv('MAX_DURATION', 5.0))
    MAX_SIGNALS_HISTORY = int(os.getenv('MAX_SIGNALS_HISTORY', 100))
    ACTIVE_SIGNAL_TIMEOUT = int(os.getenv('ACTIVE_SIGNAL_TIMEOUT', 10))
    MAX_SIGNALS_ON_SITE = int(os.getenv('MAX_SIGNALS_ON_SITE', 6))
    
    # Актив
    ASSETS_RAW = [asset.strip() for asset in os.getenv('ASSETS', 'GBPJPY_otc,EURUSD_otc,USDJPY_otc').split(',')]
    ASSETS = [asset.replace('/', '') for asset in ASSETS_RAW]
    
    TIMEFRAMES = int(os.getenv('TIMEFRAMES', 60))
    
    # Навчання
    FEEDBACK_ENABLED = os.getenv('FEEDBACK_ENABLED', 'true').lower() == 'true'
    CLEANUP_COUNT = 6
    
    # Шляхи до файлів
    DATA_DIR = BASE_DIR / 'data'
    SIGNALS_FILE = DATA_DIR / 'signals.json'
    HISTORY_FILE = DATA_DIR / 'history.json'
    FEEDBACK_FILE = DATA_DIR / 'feedback.json'
    ASSETS_CONFIG_FILE = DATA_DIR / 'assets_config.json'
    LESSONS_FILE = DATA_DIR / 'lessons.json'
    
    # Налаштування логування
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'logs' / 'signals.log'
    
    # Часовий пояс
    KYIV_TZ = pytz.timezone('Europe/Kiev')

    # Мова
    LANGUAGE = os.getenv('LANGUAGE', 'uk')

    @staticmethod
    def get_kyiv_time():
        """Отримання поточного часу в Києві"""
        return datetime.now(Config.KYIV_TZ)

    @staticmethod
    def validate_ssid_format(ssid):
        """Перевіряє чи SSID у правильному форматі"""
        if not ssid:
            return False, "SSID порожній"
        
        pattern = r'^42\["auth",\{.*\}\]$'
        if not re.match(pattern, ssid):
            return False, f"Неправильний формат SSID"
        
        return True, "SSID валідний"
    
    @classmethod
    def get_validated_ssid(cls):
        """Повертає валідований SSID для реального або демо рахунку"""
        ssid = cls.POCKET_SSID
        
        if not ssid:
            logger.error("SSID не знайдено! Перевірте .env або GitHub Secrets")
            return None
        
        # Додамо детальну інформацію для дебагу
        logger.info(f"🔍 Оригінальний SSID: {ssid[:100]}...")
        logger.info(f"🔍 Режим: {'DEMO' if cls.POCKET_DEMO else 'REAL'}")
        
        # ========== КРИТИЧНЕ ВИПРАВЛЕННЯ ==========
        # Перевіряємо, чи вже є правильний формат для реального рахунку
        if not cls.POCKET_DEMO and 'sessionToken' in ssid:
            logger.info("✅ SSID вже у правильному форматі для реального рахунку")
            return ssid
        
        # Перевіряємо, чи вже є правильний формат для демо рахунку
        if cls.POCKET_DEMO and ssid.startswith('42["auth"'):
            logger.info("✅ SSID вже у правильному форматі для демо рахунку")
            return ssid
        
        # Якщо SSID не у повному форматі, конвертуємо відповідно до режиму
        logger.warning(f"SSID не у повному форматі, конвертую...")
        logger.info(f"Оригінальний SSID: {ssid[:50]}...")
        
        if cls.POCKET_DEMO:
            # ДЕМО РЕЖИМ: використовуємо "session" та isDemo=1
            is_demo_value = 1
            ssid = f'42["auth",{{"session":"{ssid}","isDemo":{is_demo_value},"uid":102582216,"platform":1}}]'
            logger.info("⚙️ Конвертовано для ДЕМО рахунку")
        else:
            # РЕАЛЬНИЙ РЕЖИМ: використовуємо "sessionToken" та isDemo=0
            # УВАГА: Для реального рахунку має бути короткий token (32 символи)
            is_demo_value = 0
            ssid = f'42["auth",{{"sessionToken":"{ssid}","uid":"102582216","lang":"ru","isDemo":{is_demo_value},"platform":1,"isChart":1}}]'
            logger.info("⚙️ Конвертовано для РЕАЛЬНОГО рахунку")
        
        logger.info(f"Конвертований SSID: {ssid[:50]}...")
        
        is_valid, message = cls.validate_ssid_format(ssid)
        
        if is_valid:
            logger.info(f"✅ SSID валідний ({len(ssid)} символів)")
        else:
            logger.error(f"❌ Помилка валідації SSID: {message}")
            logger.error(f"SSID: {ssid[:100]}...")
        
        return ssid
    
    @classmethod
    def validate(cls):
        """Перевірка конфігурації"""
        errors = []
        
        if not cls.POCKET_SSID:
            errors.append("❌ POCKET_SSID не встановлено")
        
        if not cls.GROQ_API_KEY:
            errors.append("❌ GROQ_API_KEY не встановлено")
        
        if not cls.ASSETS:
            errors.append("❌ Не вказано активи")
        
        # Додаткова перевірка для реального рахунку
        if not cls.POCKET_DEMO:
            # Для реального рахунку має бути короткий токен (~32 символи)
            ssid_length = len(cls.POCKET_SSID or '')
            if ssid_length > 100 and 'sessionToken' not in cls.POCKET_SSID:
                logger.warning("⚠️  Для реального рахунку очікується короткий токен (~32 символи)")
                logger.warning(f"⚠️  Ваш SSID має {ssid_length} символів - можливо це демо токен")
        
        if errors:
            for error in errors:
                logger.error(error)
            return False
        return True
