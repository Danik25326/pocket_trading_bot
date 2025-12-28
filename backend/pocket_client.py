import asyncio
import logging
from pocketoptionapi_async import AsyncPocketOptionClient
from config import Config

logger = logging.getLogger("signal_bot")

class PocketOptionClient:
    def __init__(self):
        self.client = None
        self.connected = False
        
    async def connect(self):
        """Підключення до PocketOption"""
        try:
            ssid = Config.get_formatted_ssid()
            if not ssid:
                logger.error("❌ Немає SSID для підключення")
                return False
            
            logger.info("🔗 Ініціалізація клієнта PocketOption...")
            
            # Створюємо клієнт
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                demo=Config.POCKET_DEMO,
                uid=Config.POCKET_UID,
                enable_logging=True,
                timeout=10
            )
            
            # Підключаємося
            logger.info("🔄 Підключення до сервера...")
            connection_result = await self.client.connect()
            
            if connection_result:
                self.connected = True
                logger.info("✅ Успішно підключено до PocketOption")
                
                # Перевіряємо баланс
                try:
                    balance = await self.client.get_balance()
                    logger.info(f"💰 Баланс: {balance.balance} {balance.currency}")
                except:
                    logger.warning("⚠️ Не вдалося отримати баланс")
                
                return True
            else:
                logger.error("❌ Не вдалося підключитися")
                return False
                
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {str(e)}")
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок"""
        try:
            if not self.connected:
                logger.error("❌ Клієнт не підключений")
                return None
            
            logger.info(f"📊 Отримання свічок для {asset}...")
            candles = await self.client.get_candles(
                asset=asset,
                timeframe=timeframe,
                count=count
            )
            
            if candles and len(candles) > 0:
                logger.info(f"✅ Отримано {len(candles)} свічок")
                return candles
            else:
                logger.warning(f"⚠️ Не вдалося отримати свічки для {asset}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок: {str(e)}")
            return None
    
    async def disconnect(self):
        """Відключення"""
        try:
            if self.client and self.connected:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від PocketOption")
        except:
            pass
