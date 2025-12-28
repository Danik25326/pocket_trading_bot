import asyncio
import logging

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
            # Імпортуємо тут, щоб уникнути помилок
            from pocketoptionapi_async import AsyncPocketOptionClient
            from config import Config
            
            ssid = Config.POCKET_SSID
            if not ssid:
                logger.error("❌ SSID не знайдено!")
                return self
            
            logger.info("🔗 Ініціалізація PocketOption клієнта...")
            
            # Форматуємо SSID
            if not ssid.startswith('42["auth"'):
                is_demo = 1 if Config.POCKET_DEMO else 0
                ssid = f'42["auth",{{"session":"{ssid}","isDemo":{is_demo},"uid":102582216,"platform":1}}]'
            
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                enable_logging=False
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
            
            await asyncio.sleep(2)
            
            # Проста перевірка підключення
            self.connected = True
            logger.info("✅ Підключено до PocketOption")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            self.connected = False
            return False
    
    async def get_candles(self, asset, timeframe, count=30):
        """Отримання свічок для активу"""
        try:
            if not self.connected:
                if not await self.connect():
                    return None
            
            logger.info(f"📊 Запит свічок для {asset}")
            
            candles = await self.client.get_candles(
                asset=asset,
                timeframe=timeframe,
                count=count
            )
            
            if candles:
                logger.info(f"✅ Отримано {len(candles)} свічок")
                return candles
            else:
                logger.warning(f"⚠️ Немає свічок для {asset}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок: {e}")
            return None
    
    async def disconnect(self):
        try:
            if self.client and self.connected:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено")
                return True
            return False
        except Exception as e:
            logger.warning(f"Помилка відключення: {e}")
            return False
