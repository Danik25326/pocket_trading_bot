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
            if not Config.POCKET_SSID:
                logger.error("❌ SSID не знайдено!")
                return self
            
            logger.info("🔗 Ініціалізація PocketOption клієнта...")
            
            # Отримуємо SSID у правильному форматі
            ssid = Config.POCKET_SSID
            # Якщо SSID не починається з 42["auth", то конвертуємо
            if not ssid.startswith('42["auth"'):
                # Конвертуємо в повний формат
                ssid = f'42["auth",{{"session":"{ssid}","isDemo":1,"uid":102582216,"platform":1}}]'
            
            # Створюємо клієнт з параметрами згідно документації
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                demo=Config.POCKET_DEMO,  # можливо, is_demo -> demo
                uid=102582216,  # це твій uid, можна взяти з конфига
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
            
            logger.info("🔗 Підключення...")
            
            # Підключаємося
            await self.client.connect()
            
            # Перевіряємо, чи підключення успішне
            if self.client.connected:
                logger.info("✅ Успішно підключено до PocketOption!")
                self.connected = True
                
                # Отримуємо баланс для підтвердження
                try:
                    balance = await self.client.get_balance()
                    logger.info(f"💰 Баланс: {balance.balance} {balance.currency}")
                except Exception as e:
                    logger.warning(f"Баланс не отримано: {e}")
                
                return True
            else:
                logger.error("❌ Не вдалося підключитися до PocketOption")
                self.connected = False
                return False
        
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            self.connected = False
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.connected:
                logger.warning(f"Спробую підключитися для {asset}...")
                if not await self.connect():
                    logger.error(f"Не вдалося підключитися для {asset}")
                    return None
            
            logger.info(f"📊 Запит свічок: {asset}")
            
            # Використовуємо метод get_candles
            candles = await self.client.get_candles(
                asset=asset,
                timeframe=timeframe,
                count=count
            )
            
            if candles and len(candles) > 0:
                logger.info(f"✅ Отримано {len(candles)} свічок для {asset}")
                return candles
            else:
                logger.warning(f"Отримано 0 свічок для {asset}")
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
