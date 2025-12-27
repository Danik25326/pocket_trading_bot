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
        """Підключення до Pocket Option"""
        try:
            if not Config.POCKET_SSID:
                logger.error("❌ SSID не знайдено!")
                self.connected = False
                return self  # Всегда возвращаем self, даже при ошибке
            
            logger.info(f"🔗 Підключення до PocketOption (demo={Config.POCKET_DEMO})...")
            
            # Создаем клиент
            self.client = AsyncPocketOptionClient(
                ssid=Config.POCKET_SSID,
                is_demo=Config.POCKET_DEMO,
                enable_logging=True
            )
            
            # Подключаемся
            connection_result = await self.client.connect()
            
            if connection_result:
                logger.info("✅ Успішно підключено до PocketOption!")
                self.connected = True
                
                # Тестируем соединение
                try:
                    balance = await self.client.get_balance()
                    logger.info(f"💰 Баланс: {balance.balance} {balance.currency}")
                except Exception as e:
                    logger.warning(f"Баланс не отримано: {e}")
            else:
                logger.error("❌ Не вдалося підключитися до PocketOption")
                self.connected = False
            
            return self  # ВАЖНО: всегда возвращаем self
            
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            self.connected = False
            return self  # Все равно возвращаем self
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок"""
        try:
            # Если не подключены, пытаемся подключиться
            if not self.connected:
                logger.warning(f"Спробую підключитися для {asset}...")
                await self.connect()
                
                if not self.connected or not self.client:
                    logger.error(f"Не вдалося підключитися для {asset}")
                    return None
            
            logger.info(f"📊 Запит свічок: {asset}")
            
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
    
    async def get_balance(self):
        """Отримання балансу"""
        try:
            if not self.connected:
                await self.connect()
            
            if self.connected and self.client:
                balance = await self.client.get_balance()
                logger.info(f"Баланс: {balance.balance} {balance.currency}")
                return balance
            return None
            
        except Exception as e:
            logger.error(f"Помилка отримання балансу: {e}")
            return None
    
    async def disconnect(self):
        """Відключення"""
        try:
            if self.client and self.connected:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від PocketOption")
        except Exception as e:
            logger.warning(f"Помилка відключення: {e}")
