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
    # Pocket Option API - тільки реальний
    POCKET_SSID = os.getenv('POCKET_SSID')
    
    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
    
    # Сигнали
    SIGNAL_INTERVAL = int(os.getenv('SIGNAL_INTERVAL', 600))
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.75))
    MAX_DURATION = float(os.getenv('MAX_DURATION', 5.0))
    MAX_SIGNALS_HISTORY = int(os.getenv('MAX_SIGNALS_HISTORY', 100))
    MAX_SIGNALS_ON_SITE = int(os.getenv('MAX_SIGNALS_ON_SITE', 6))
    
    # Активи
    ASSETS_RAW = [asset.strip() for asset in os.getenv('ASSETS', 'GBPJPY_otc,EURUSD_otc,USDJPY_otc').split(',')]
    ASSETS = [asset.replace('/', '') for asset in ASSETS_RAW]
    
    TIMEFRAMES = int(os.getenv('TIMEFRAMES', 60))
    
    # Навчання
    FEEDBACK_ENABLED = os.getenv('FEEDBACK_ENABLED', 'true').lower() == 'true'
    
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
    LANGUAGE = os.getenv('LANGUAGE', 'uk')

    @staticmethod
    def get_kyiv_time():
        return datetime.now(Config.KYIV_TZ)

    @staticmethod
    def validate_ssid_format(ssid):
        """Перевіряє базовий формат SSID"""
        if not ssid:
            return False, "SSID порожній"
        
        if not ssid.startswith('42["auth"'):
            return False, "SSID повинен починатися з 42[\"auth\""
        
        return True, "SSID валідний"
    
    @classmethod
    def get_validated_ssid(cls):
        """Повертає SSID для реального рахунку з обробкою PHP серіалізації"""
        ssid = cls.POCKET_SSID
        
        if not ssid:
            logger.error("❌ POCKET_SSID не знайдено! Перевірте .env або GitHub Secrets")
            return None
        
        logger.info(f"🔍 Оригінальний SSID: {ssid[:100]}...")
        logger.info(f"🔍 Довжина: {len(ssid)} символів")
        
        # АНАЛІЗ СТРУКТУРИ ТОКЕНА
        if '"session":"a:4:' in ssid:
            logger.info("⚙️ Виявлено PHP серіалізацію, обробляю...")
            
            # 1. Спроба отримати session_id з PHP серіалізації
            php_pattern = r'session_id";s:32:"([a-f0-9]{32})"'
            match = re.search(php_pattern, ssid)
            
            if match:
                session_id = match.group(1)
                logger.info(f"✅ Витягнуто session_id: {session_id}")
                
                # 2. ВИКОРИСТОВУЄМО ВАРІАНТ 1: sessionToken
                # Створюємо новий SSID з sessionToken
                new_ssid = re.sub(
                    r'"session":"a:4:\{[^}]+\}[^"]+"',
                    f'"sessionToken":"{session_id}"',
                    ssid
                )
                
                # 3. Додатково видаляємо залишки серіалізації
                new_ssid = new_ssid.replace('f6f547041e4a7965fb57feb838eba278",', '",')
                
                # 4. Переконуємось що isDemo=0
                if '"isDemo":0' not in new_ssid:
                    new_ssid = new_ssid.replace('"sessionToken"', '"isDemo":0,"sessionToken"')
                
                # 5. Перевіряємо platform - завжди ставимо 8 (сучасна версія)
                if '"platform":2' in new_ssid:
                    new_ssid = new_ssid.replace('"platform":2', '"platform":8')
                elif '"platform":8' not in new_ssid:
                    # Додаємо platform якщо немає
                    new_ssid = new_ssid.replace('"isDemo":0,', '"isDemo":0,"platform":8,')
                
                # 6. Переконуємось що є всі обов'язкові поля
                required_fields = ['isDemo', 'uid', 'platform', 'isFastHistory', 'isOptimized']
                for field in required_fields:
                    if f'"{field}":' not in new_ssid:
                        logger.warning(f"⚠️ Відсутнє поле {field} в SSID")
                
                logger.info("✅ Конвертовано PHP серіалізацію в sessionToken формат")
                logger.info(f"📋 Новий SSID: {new_ssid[:120]}...")
                logger.info(f"📏 Довжина нового SSID: {len(new_ssid)}")
                
                # Перевірка на реальний рахунок
                if '"isDemo":0' in new_ssid:
                    logger.info("🎯 Режим: реальний рахунок (isDemo=0)")
                else:
                    logger.error("❌ Увага: SSID не містить isDemo:0")
                    return None
                
                return new_ssid
            else:
                logger.error("❌ Не вдалося витягти session_id з PHP серіалізації")
                logger.warning("⚠️ Спробую використати оригінальний SSID")
        
        # Якщо PHP серіалізації немає
        else:
            logger.info("ℹ️ PHP серіалізація не виявлена")
            
            # Перевіряємо який формат використовується
            if '"sessionToken"' in ssid:
                logger.info("✅ Використовується sessionToken формат (варіант 1)")
            elif '"session"' in ssid and 'a:4:' not in ssid:
                logger.info("ℹ️ Використовується простий session формат (варіант 2)")
            else:
                logger.warning("⚠️ Невідомий формат SSID")
            
            # Перевірка на реальний рахунок
            if '"isDemo":0' in ssid:
                logger.info("✅ Режим: реальний рахунок (isDemo=0)")
            elif '"isDemo":1' in ssid:
                logger.error("❌ Це DEMO рахунок! (isDemo=1)")
                return None
            else:
                logger.warning("⚠️ Увага: SSID не містить поля isDemo")
        
        # Фінальна валідація
        is_valid, message = cls.validate_ssid_format(ssid)
        
        if is_valid:
            logger.info("✅ SSID валідний")
            return ssid
        else:
            logger.error(f"❌ {message}")
            return None
    
    @classmethod
    def validate(cls):
        """Базова перевірка конфігурації"""
        errors = []
        
        if not cls.POCKET_SSID:
            errors.append("❌ POCKET_SSID не встановлено")
        
        if not cls.GROQ_API_KEY:
            errors.append("❌ GROQ_API_KEY не встановлено")
        
        if not cls.ASSETS:
            errors.append("❌ Не вказано активи")
        
        # Додаткова перевірка для токена
        if cls.POCKET_SSID:
            if 'g.a000' in cls.POCKET_SSID:
                errors.append("❌ Виявлено DEMO формат токена (g.a000)")
                errors.append("❌ Отримай REAL токен з реального кабінету")
            
            # Перевіряємо наявність обов'язкових полів
            if '"uid"' not in cls.POCKET_SSID:
                errors.append("⚠️ В токені відсутнє поле uid")
            
            # Перевіряємо формат
            is_valid, message = cls.validate_ssid_format(cls.POCKET_SSID)
            if not is_valid:
                errors.append(f"❌ {message}")
        
        if errors:
            for error in errors:
                logger.error(error)
            return False
        
        logger.info("✅ Конфігурація валідна")
        return True
