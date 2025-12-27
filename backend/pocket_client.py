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
                logger.error("❌ SSID не знайдено! Перевірте GitHub Secrets")
                return None
            
            logger.info(f"🔗 Підключення до PocketOption (demo={Config.POCKET_DEMO})...")
            
            # Використовуємо SSID безпосередньо
            ssid = Config.POCKET_SSID
            logger.info(f"SSID довжина: {len(ssid)} символів")
            
            # ВИДАЛИ параметр timeout!
            self.client = AsyncPocketOptionClient(
                ssid=ssid,
                is_demo=Config.POCKET_DEMO,
                enable_logging=True
                # timeout=30  # <-- ВИДАЛИ ЦЕЙ РЯДОК
            )
            
            connection_result = await self.client.connect()
            
            if connection_result:
                logger.info("✅ Успішно підключено до PocketOption!")
                self.connected = True
                
                try:
                    balance = await self.client.get_balance()
                    logger.info(f"💰 Баланс: {balance.balance} {balance.currency}")
                except Exception as e:
                    logger.warning(f"Не вдалося отримати баланс: {e}")
                
                return self
            else:
                logger.error("❌ Не вдалося підключитися до PocketOption")
                self.connected = False
                return None
                
        except Exception as e:
            logger.error(f"❌ Критична помилка підключення: {e}")
            self.connected = False
            return None
    
    # ... решта коду залишається без змін ...
