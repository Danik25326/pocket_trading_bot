import asyncio
import json
import logging
from datetime import datetime, timedelta
import pytz
from config import Config
from pocket_client import PocketOptionClient
from groq_analyzer import GroqAnalyzer
from data_handler import DataHandler

# Налаштування логування
logger = logging.getLogger("signal_bot")

class SignalGenerator:
    def __init__(self):
        self.pocket_client = PocketOptionClient()
        self.analyzer = GroqAnalyzer()
        self.data_handler = DataHandler()
        self.signals = []
        
    async def generate_signal(self, asset):
        """Генерація одного сигналу"""
        try:
            logger.info(f"📈 Аналіз активу: {asset}")
            
            # Перевіряємо чи є клієнт
            if not hasattr(self.pocket_client, 'client'):
                logger.error("PocketOptionClient не ініціалізований")
                return None
            
            # Підключаємося
            if not self.pocket_client.connected:
                logger.info(f"Спробую підключитися для {asset}...")
                await self.pocket_client.connect()
                
                if not self.pocket_client.connected:
                    logger.error(f"Не вдалося підключитися для {asset}")
                    return None
            
            # Отримуємо свічки
            candles = await self.pocket_client.get_candles(
                asset=asset,
                timeframe=Config.TIMEFRAMES,
                count=50
            )
            
            if not candles:
                logger.warning(f"Не вдалося отримати свічки для {asset}")
                return None
            
            logger.info(f"✅ Отримано {len(candles)} свічок для {asset}")
            
            # Аналізуємо через AI
            signal = self.analyzer.analyze_market(asset, candles)
            
            if signal and signal.get('confidence', 0) >= Config.MIN_CONFIDENCE:
                # Додаємо час генерації в UTC+2 (Київ)
                kyiv_tz = pytz.timezone('Europe/Kiev')
                generated_at = datetime.now(kyiv_tz).isoformat()
                signal['generated_at'] = generated_at
                signal['asset'] = asset
                logger.info(f"✅ Створено сигнал для {asset}: {signal['direction']} ({signal['confidence']*100:.1f}%)")
                return signal
            elif signal:
                logger.warning(f"Сигнал для {asset} має низьку впевненість: {signal.get('confidence', 0)*100:.1f}%")
            else:
                logger.warning(f"AI не повернув сигнал для {asset}")
                
        except Exception as e:
            logger.error(f"Помилка генерації сигналу для {asset}: {e}")
            
        return None
    
    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів"""
        logger.info("=" * 50)
        logger.info(f"🚀 Початок генерації сигналів - {datetime.now()}")
        
        try:
            # Виводимо конфігурацію
            logger.info(f"⚙️ Конфігурація:")
            logger.info(f"  - Демо режим: {Config.POCKET_DEMO}")
            logger.info(f"  - Активи: {Config.ASSETS}")
            logger.info(f"  - Таймфрейм: {Config.TIMEFRAMES} сек")
            logger.info(f"  - Мін. впевненість: {Config.MIN_CONFIDENCE*100}%")
            
            # Підключаємося
            logger.info("🔗 Підключення до PocketOption...")
            await self.pocket_client.connect()
            
            if not self.pocket_client.connected:
                logger.error("❌ Не вдалося підключитися до PocketOption")
                return []
            
            logger.info("✅ Успішно підключено!")
            
            valid_signals = []
            for asset in Config.ASSETS:
                signal = await self.generate_signal(asset)
                if signal:
                    valid_signals.append(signal)
                else:
                    logger.warning(f"Не створено сигнал для {asset}")
            
            # Зберігаємо сигнали
            if valid_signals:
                self.data_handler.save_signals(valid_signals)
                logger.info(f"💾 Збережено {len(valid_signals)} сигналів")
                
                # Виводимо інформацію про сигнали
                for signal in valid_signals:
                    logger.info(f"   📊 {signal['asset']}: {signal['direction']} ({signal['confidence']*100:.1f}%) - {signal.get('reason', '')[:50]}...")
            else:
                logger.warning("⚠️  Не створено жодного сигналу")
            
            await self.pocket_client.disconnect()
            
            # Оновлюємо статистику
            stats = self.data_handler.get_statistics()
            logger.info(f"📈 Статистика: {stats.get('total_signals', 0)} сигналів, "
                       f"Успішність: {stats.get('success_rate', 0)*100:.1f}%")
            
            return valid_signals
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            import traceback
            logger.error(f"Трейс: {traceback.format_exc()}")
            return []

async def main():
    generator = SignalGenerator()
    await generator.generate_all_signals()

if __name__ == "__main__":
    asyncio.run(main())
