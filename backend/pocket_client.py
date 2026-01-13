import asyncio
import logging
from datetime import datetime, timedelta
from config import Config

# ВІДКЛЮЧИТИ всі логи pocketoptionapi_async для реального рахунку
logging.getLogger("pocketoptionapi_async").setLevel(logging.CRITICAL)
logging.getLogger("pocketoptionapi_async.websocket_client").setLevel(logging.CRITICAL)
logging.getLogger("pocketoptionapi_async.client").setLevel(logging.CRITICAL)

logger = logging.getLogger("signal_bot")

class PocketOptionClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._initialized = False
        self._connection_attempts = 0
        self._max_attempts = 2  # Тільки 2 спроби для реального рахунку
    
    async def initialize(self):
        if self._initialized:
            return self
        
        try:
            ssid = Config.get_validated_ssid()
            if not ssid:
                logger.error("❌ Не вдалося отримати валідний SSID для реального рахунку!")
                return self
            
            logger.info("🔗 Ініціалізація клієнта для РЕАЛЬНОГО рахунку...")
            
            # Перевірка isDemo в SSID
            if 'isDemo":1' in ssid:
                logger.error("❌ КРИТИЧНА ПОМИЛКА: SSID містить isDemo:1 для реального рахунку!")
                logger.error("❌ Отримай новий токен з реального рахунку (не демо!)")
                return self
            
            from pocketoptionapi_async import AsyncPocketOptionClient
            
            # ВАЖЛИВО: is_demo=False для реального рахунку
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                is_demo=False,  # ← false для реального
                enable_logging=False  # Вимкнути логування для безпеки
            )
            
            self._initialized = True
            logger.info("✅ Клієнт ініціалізовано для РЕАЛЬНОГО рахунку")
            return self
        
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації для реального рахунку: {e}")
            return self
    
    async def connect(self):
        """Підключення до РЕАЛЬНОГО рахунку PocketOption"""
        self._connection_attempts += 1
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.client:
                logger.error("❌ Клієнт не ініціалізований")
                return False
            
            logger.info("🔗 Підключення до РЕАЛЬНОГО рахунку PocketOption...")
            logger.warning("⚠️  УВАГА: Використовується РЕАЛЬНИЙ рахунок!")
            logger.warning("⚠️  Усі операції будуть з реальними грошима!")
            
            # Спроба підключення
            connection_result = await self.client.connect()
            
            if connection_result:
                logger.info("✅ Виклик connect() успішний")
                await asyncio.sleep(1)
            else:
                logger.error("❌ Не вдалося підключитися (connect() повернув False)")
                return False
            
            # Перевірка балансу
            try:
                logger.info("🔄 Перевірка підключення через баланс...")
                balance = await self.client.get_balance()
                
                if balance and hasattr(balance, 'balance'):
                    self.connected = True
                    
                    # Критично важливо: перевіряємо чи це реальний рахунок
                    if hasattr(balance, 'is_demo') and balance.is_demo:
                        logger.error("❌ КРИТИЧНА ПОМИЛКА: Підключено до ДЕМО рахунку!")
                        logger.error("❌ Перевірте токен та режим підключення")
                        return False
                    
                    logger.info("🎉 УСПІШНО підключено до РЕАЛЬНОГО рахунку!")
                    logger.info(f"💰 РЕАЛЬНИЙ баланс: ${balance.balance:,.2f} {balance.currency}")
                    
                    # Попередження про низький баланс
                    if balance.balance < 10:
                        logger.warning("⚠️  УВАГА: Реальний баланс менше $10!")
                    elif balance.balance < 50:
                        logger.warning("⚠️  УВАГА: Реальний баланс менше $50!")
                    
                    return True
                else:
                    logger.error("❌ Не вдалося отримати баланс")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Помилка отримання балансу: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Помилка підключення до реального рахунку: {e}")
            self.connected = False
            
            # Детальна інформація про помилки
            error_msg = str(e)
            if "session" in error_msg:
                logger.error("💥 Токен прострочений або невірний!")
                logger.error("💥 Отримай НОВИЙ токен з реального рахунку")
            elif "timeout" in error_msg:
                logger.error("⏱️  Таймаут підключення")
            elif "WebSocket" in error_msg:
                logger.error("🌐 Проблема з WebSocket з'єднанням")
            
            return False
    
    async def get_candles(self, asset, timeframe, count=50):
        """Отримання свічок для реального рахунку"""
        try:
            asset_clean = asset.replace('/', '')
            
            if not self.connected:
                logger.warning(f"🔌 Не підключено для {asset_clean}, спробую підключитися...")
                if not await self.connect():
                    logger.error(f"❌ Не вдалося підключитися для реального рахунку {asset_clean}")
                    return None  # НЕ повертаємо тестові дані для реального рахунку
            
            logger.info(f"📊 Запит РЕАЛЬНИХ свічок для {asset_clean}...")
            
            candles = await self.client.get_candles(
                asset=asset_clean,
                timeframe=timeframe,
                count=count
            )
            
            if not candles:
                logger.warning(f"⚠️ Не отримано свічок для реального рахунку {asset_clean}")
                return None  # НЕ повертаємо тестові дані
            
            if len(candles) > 0:
                first_candle = candles[0]
                if hasattr(first_candle, 'close'):
                    if first_candle.close == 0 or first_candle.open == 0:
                        logger.warning(f"⚠️ Отримані нульові дані для реального рахунку {asset_clean}")
                        return None
            
            logger.info(f"✅ Отримано {len(candles)} РЕАЛЬНИХ свічок для {asset_clean}")
            
            # Додаткова інформація для реального рахунку
            if len(candles) > 0:
                last_candle = candles[-1]
                logger.info(f"📈 Остання свічка: {last_candle.close}")
            
            return candles
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання свічок для реального рахунку {asset}: {e}")
            return None  # НЕ повертаємо тестові дані
    
    async def disconnect(self):
        if self.client:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("✅ Відключено від РЕАЛЬНОГО рахунку PocketOption")
            except Exception as e:
                logger.warning(f"⚠️ Помилка відключення: {e}")
        else:
            logger.info("ℹ️ Не було активного підключення")
