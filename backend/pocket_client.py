import asyncio
import logging
from datetime import datetime, timedelta
from config import Config

# Налаштуємо логування для pocketoptionapi_async - відключимо DEBUG логи
logging.getLogger("pocketoptionapi_async").setLevel(logging.WARNING)
logging.getLogger("pocketoptionapi_async.websocket_client").setLevel(logging.WARNING)
logging.getLogger("pocketoptionapi_async.client").setLevel(logging.WARNING)

logger = logging.getLogger("signal_bot")

class PocketOptionClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._initialized = False
        self._connection_attempts = 0
        self._max_attempts = 3
        self._last_connection_time = None
        self._reconnection_delay = 5
    
    async def initialize(self):
        if self._initialized:
            return self
        
        try:
            # Отримуємо SSID з конфігурації
            ssid = Config.get_validated_ssid()
            if not ssid:
                logger.error("❌ Не вдалося отримати валідний SSID!")
                return self
            
            logger.info(f"🔗 Ініціалізація PocketOption клієнта")
            
            # ========== ВАЖЛИВО: Вказуємо режим ==========
            is_demo_mode = Config.POCKET_DEMO
            logger.info(f"   Режим: {'DEMO' if is_demo_mode else 'REAL'}")
            
            # ДОДАТКОВЕ ЛОГУВАННЯ ДЛЯ РЕАЛЬНОГО РАХУНКУ
            if not is_demo_mode:
                logger.warning("🚨 УВАГА: Використовується РЕАЛЬНИЙ рахунок!")
                logger.warning("🚨 Усі операції будуть з реальними грошима!")
                logger.warning(f"🚨 SSID починається з: {ssid[:100]}")
            
            # Імпортуємо асинхронного клієнта
            try:
                from pocketoptionapi_async import AsyncPocketOptionClient
            except ImportError as e:
                logger.error(f"❌ Не вдалося імпортувати pocketoptionapi_async: {e}")
                logger.info("ℹ️ Встановіть бібліотеку: pip install pocketoptionapi-async==2.0.1")
                return self
            
            # КРИТИЧНО ВАЖЛИВО: передаємо правильний режим
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                is_demo=is_demo_mode,  # ← передаємо режим з Config
                enable_logging=False  # ← ВИМКНУТИ детальне логування!
            )
            
            self._initialized = True
            logger.info("✅ Клієнт ініціалізовано")
            return self
        
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації PocketOption: {e}")
            import traceback
            logger.error(f"Деталі: {traceback.format_exc()}")
            return self
    
    async def connect(self):
        """Метод підключення до PocketOption"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.client:
                logger.error("❌ Клієнт не ініціалізований")
                return False
            
            logger.info(f"🔗 Підключення до PocketOption...")
            
            # ========== ВАЖЛИВО: Виводимо інформацію про режим ==========
            mode_info = "РЕАЛЬНИЙ" if not Config.POCKET_DEMO else "ДЕМО"
            logger.info(f"   Режим: {mode_info}")
            
            if not Config.POCKET_DEMO:
                logger.warning("⚠️  УВАГА: Використовується РЕАЛЬНИЙ рахунок!")
                logger.warning("⚠️  Усі операції будуть з реальними грошима!")
            
            # Спробуємо підключитися
            try:
                await self.client.connect()
                logger.info("✅ Виклик connect() успішний")
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Помилка при виклику connect(): {e}")
                # Для реального рахунку даємо детальнішу інформацію
                if not Config.POCKET_DEMO:
                    logger.error("💥 Можливі причини помилки для реального рахунку:")
                    logger.error("   1. SSID прострочений (живе 1-2 години)")
                    logger.error("   2. Неправильний формат SSID (потрібен sessionToken)")
                    logger.error("   3. Проблеми з мережею Pocket Option")
                return False
            
            # Спробуємо отримати баланс
            try:
                logger.info("🔄 Перевірка підключення через баланс...")
                balance = await self.client.get_balance()
                if balance and hasattr(balance, 'balance'):
                    self.connected = True
                    
                    # ВИВІД ЗАЛЕЖНО ВІД РЕЖИМУ
                    if Config.POCKET_DEMO:
                        logger.info(f"✅ Успішно підключено до ДЕМО рахунку!")
                    else:
                        logger.info(f"✅ Успішно підключено до РЕАЛЬНОГО рахунку!")
                        logger.info("🎉 Вітаю! Ви підключені до РЕАЛЬНОГО рахунку!")
                    
                    logger.info(f"💰 Баланс: {balance.balance} {balance.currency}")
                    
                    # Додаткова перевірка для реального рахунку
                    if not Config.POCKET_DEMO:
                        if balance.balance <= 0:
                            logger.error("❌ УВАГА: Реальний баланс дорівнює або менше нуля!")
                        elif balance.balance < 10:
                            logger.warning("⚠️  УВАГА: Реальний баланс менше $10!")
                    
                    return True
                else:
                    logger.error("❌ Баланс не отримано або неправильний формат")
                    return False
            except Exception as e:
                logger.error(f"❌ Не вдалося отримати баланс: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            import traceback
            logger.error(f"Трейс: {traceback.format_exc()}")
            self.connected = False
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок"""
        try:
            # Конвертуємо формат активу
            asset_clean = asset.replace('/', '')
            
            if not self.connected:
                logger.warning(f"🔌 Не підключено для {asset}, спробую підключитися...")
                if not await self.connect():
                    logger.error(f"❌ Не вдалося підключитися для {asset}")
                    # ========== ВАЖЛИВО: Для реального рахунку НЕ повертаємо тестові дані ==========
                    if Config.POCKET_DEMO:
                        return await self._get_mock_candles(count)
                    return None
            
            logger.info(f"📊 Запит свічок для {asset_clean}...")
            logger.info(f"   Режим: {'DEMO' if Config.POCKET_DEMO else 'REAL'}")
            
            candles = await self.client.get_candles(
                asset=asset_clean,
                timeframe=timeframe,
                count=count
            )
            
            if not candles:
                logger.warning(f"⚠️ Не отримано свічок для {asset_clean}")
                # ========== ВАЖЛИВО: Для реального рахунку НЕ повертаємо тестові дані ==========
                if Config.POCKET_DEMO:
                    return await self._get_mock_candles(count)
                return None
            
            # Перевіряємо дані
            if len(candles) > 0:
                first_candle = candles[0]
                if hasattr(first_candle, 'close'):
                    if first_candle.close == 0 or first_candle.open == 0:
                        logger.warning(f"⚠️ Отримані нульові дані для {asset_clean}")
                        if Config.POCKET_DEMO:
                            return await self._get_mock_candles(count)
                        return None
            
            logger.info(f"✅ Отримано {len(candles)} коректних свічок для {asset_clean}")
            
            # Додаткова інформація для реального рахунку
            if not Config.POCKET_DEMO and len(candles) > 0:
                last_candle = candles[-1]
                logger.info(f"📈 Остання свічка: {last_candle.close} (час: {last_candle.timestamp})")
            
            return candles
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок для {asset}: {e}")
            # ========== ВАЖЛИВО: Для реального рахунку НЕ повертаємо тестові дані ==========
            if Config.POCKET_DEMO:
                return await self._get_mock_candles(count)
            return None
    
    async def _get_mock_candles(self, count=50):
        """Повернення тестових свічок для демо-режиму"""
        # ========== ВАЖЛИВО: Для реального рахунку НЕ генеруємо тестові дані ==========
        if not Config.POCKET_DEMO:
            logger.error("🚫 Тестові дані недоступні для реального рахунку!")
            return None
            
        import random
        from collections import namedtuple
        
        logger.info("🔄 Генерую тестові свічки для демо-режиму...")
        
        Candle = namedtuple('Candle', ['timestamp', 'open', 'high', 'low', 'close'])
        now = datetime.now()
        candles = []
        
        base_price = 150.0
        
        for i in range(count):
            timestamp = now - timedelta(minutes=2 * (count - i))
            
            change = random.uniform(-0.5, 0.5)
            open_price = base_price + random.uniform(-1, 1)
            close_price = open_price + change
            
            high_price = max(open_price, close_price) + random.uniform(0, 0.3)
            low_price = min(open_price, close_price) - random.uniform(0, 0.3)
            
            candle = Candle(
                timestamp=timestamp,
                open=round(open_price, 5),
                high=round(high_price, 5),
                low=round(low_price, 5),
                close=round(close_price, 5)
            )
            candles.append(candle)
            
            base_price = close_price
        
        logger.info(f"✅ Згенеровано {len(candles)} тестових свічок")
        return candles
    
    async def disconnect(self):
        if self.client:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від PocketOption")
            except Exception as e:
                logger.warning(f"⚠️ Помилка при відключенні: {e}")
        else:
            logger.info("ℹ️ Не було активного підключення")
