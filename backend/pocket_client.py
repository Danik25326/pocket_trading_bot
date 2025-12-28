import asyncio
import logging
from pocketoptionapi_async import AsyncPocketOptionClient
from config import Config

logger = logging.getLogger("signal_bot")

class PocketOptionClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return self
        
        try:
            # Отримуємо SSID з конфігурації
            ssid = Config.POCKET_SSID
            if not ssid:
                logger.error("❌ SSID не знайдено!")
                return self
            
            logger.info(f"🔗 Ініціалізація PocketOption клієнта (Demo: {Config.POCKET_DEMO})...")
            
            # Форматуємо SSID
            if not ssid.startswith('42["auth"'):
                logger.warning("Форматуємо SSID...")
                ssid = f'42["auth",{{"session":"{ssid}","isDemo":{1 if Config.POCKET_DEMO else 0},"uid":102582216,"platform":1}}]'
            
            logger.debug(f"SSID (перші 100 символів): {ssid[:100]}...")
            
            # Створюємо клієнт
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                demo=Config.POCKET_DEMO,
                uid=102582216,
                enable_logging=True
            )
            
            self._initialized = True
            logger.info("✅ Клієнт ініціалізовано")
            return self
        
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації: {e}")
            return self
    
    async def connect(self):
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.client:
                logger.error("❌ Клієнт не ініціалізований")
                return False
            
            logger.info("🔗 Підключення до PocketOption...")
            await self.client.connect()
            
            # Чекаємо на підключення
            await asyncio.sleep(2)
            
            if self.client.connected:
                logger.info("✅ Успішно підключено до PocketOption!")
                self.connected = True
                return True
            else:
                logger.error("❌ Не вдалося підключитися")
                self.connected = False
                return False
        
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            self.connected = False
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок для активу"""
        try:
            if not self.connected:
                logger.warning("Не підключено, спробую підключитися...")
                if not await self.connect():
                    return None
            
            logger.info(f"📊 Запит свічок для {asset} (таймфрейм: {timeframe}с, кількість: {count})")
            
            # Використовуємо правильний метод API
            candles = await self.client.get_candles(
                asset=asset,
                timeframe=timeframe,
                count=count
            )
            
            if candles:
                logger.info(f"✅ Отримано {len(candles)} свічок для {asset}")
                return candles
            else:
                logger.warning(f"⚠️ Не отримано свічок для {asset}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок для {asset}: {e}")
            return None
    
    async def disconnect(self):
        try:
            if self.client and self.connected:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від PocketOption")
                return True
            return False
        except Exception as e:
            logger.warning(f"Помилка відключення: {e}")
            return False
