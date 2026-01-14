import asyncio
import logging
from datetime import datetime
from config import Config

# Відключаємо логування сторонніх бібліотек
logging.getLogger("pocketoptionapi_async").setLevel(logging.CRITICAL)

logger = logging.getLogger("signal_bot")

class PocketOptionClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._initialized = False
        self._connection_attempts = 0
        self._max_attempts = 2
    
    async def initialize(self):
        if self._initialized:
            return self
        
        try:
            ssid = Config.get_validated_ssid()
            if not ssid:
                logger.error("❌ Не вдалося отримати SSID!")
                return self
            
            logger.info("🔗 Ініціалізація клієнта...")
            
            from pocketoptionapi_async import AsyncPocketOptionClient
            
            # Тільки реальний рахунок
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                is_demo=False,  # Виключно реальний рахунок
                enable_logging=False
            )
            
            self._initialized = True
            logger.info("✅ Клієнт ініціалізовано")
            return self
        
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації: {e}")
            return self
    
    async def connect(self):
        """Підключення до реального рахунку"""
        self._connection_attempts += 1
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.client:
                logger.error("❌ Клієнт не ініціалізований")
                return False
            
            logger.info("🔗 Підключення до реального рахунку...")
            
            connection_result = await self.client.connect()
            
            if connection_result:
                logger.info("✅ Підключення успішне")
                await asyncio.sleep(1)
            else:
                logger.error("❌ Не вдалося підключитися")
                return False
            
            # Перевірка підключення через баланс
            try:
                logger.info("🔄 Отримання балансу...")
                balance = await self.client.get_balance()
                
                if balance and hasattr(balance, 'balance'):
                    self.connected = True
                    logger.info(f"💰 Баланс рахунку: ${balance.balance:,.2f} {balance.currency}")
                    
                    # Попередження про низький баланс
                    if balance.balance < 10:
                        logger.warning("⚠️ Баланс менше $10!")
                    elif balance.balance < 50:
                        logger.warning("⚠️ Баланс менше $50!")
                    
                    return True
                else:
                    logger.error("❌ Не вдалося отримати баланс")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Помилка отримання балансу: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Помилка підключення: {e}")
            self.connected = False
            
            error_msg = str(e)
            if "session" in error_msg:
                logger.error("💥 Токен прострочений або невірний!")
            elif "timeout" in error_msg:
                logger.error("⏱️ Таймаут підключення")
            elif "WebSocket" in error_msg:
                logger.error("🌐 Проблема з WebSocket з'єднанням")
            
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок"""
        try:
            asset_clean = asset.replace('/', '')
            
            if not self.connected:
                logger.warning(f"🔌 Не підключено для {asset_clean}")
                if not await self.connect():
                    logger.error(f"❌ Не вдалося підключитися")
                    return None
            
            logger.info(f"📊 Запит свічок для {asset_clean}...")
            
            candles = await self.client.get_candles(
                asset=asset_clean,
                timeframe=timeframe,
                count=count
            )
            
            if not candles:
                logger.warning(f"⚠️ Не отримано свічок для {asset_clean}")
                return None
            
            logger.info(f"✅ Отримано {len(candles)} свічок для {asset_clean}")
            return candles
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок: {e}")
            return None
    
    async def disconnect(self):
        if self.client:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від рахунку")
            except Exception as e:
                logger.warning(f"⚠️ Помилка відключення: {e}")
