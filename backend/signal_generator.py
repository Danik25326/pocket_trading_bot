import asyncio
import logging
from datetime import datetime
import pytz
from config import Config
from pocket_client import PocketOptionClient
from groq_analyzer import GroqAnalyzer
from data_handler import DataHandler

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("signal_bot")

class SignalGenerator:
    def __init__(self):
        self.client = PocketOptionClient()
        self.analyzer = GroqAnalyzer()
        self.data_handler = DataHandler()
    
    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів"""
        logger.info("=" * 60)
        logger.info("🚀 ЗАПУСК ГЕНЕРАЦІЇ СИГНАЛІВ")
        
        # Валідація конфігурації
        if not Config.validate_config():
            return []
        
        kyiv_tz = pytz.timezone(Config.TIMEZONE)
        logger.info(f"📍 Часовий пояс: {Config.TIMEZONE}")
        logger.info(f"📍 Поточний час: {datetime.now(kyiv_tz).strftime('%H:%M %d.%m.%Y')}")
        
        try:
            # Підключення до PocketOption
            logger.info("🔗 Підключення до PocketOption...")
            if not await self.client.connect():
                logger.error("❌ Не вдалося підключитися")
                return []
            
            signals = []
            
            # Аналіз кожного активу
            for asset in Config.ASSETS[:Config.MAX_ACTIVE_SIGNALS]:
                logger.info(f"📊 Аналіз активу: {asset}")
                
                # Отримання свічок
                candles = await self.client.get_candles(
                    asset=asset,
                    timeframe=Config.TIMEFRAMES,
                    count=50
                )
                
                if not candles:
                    logger.warning(f"⚠️ Немає даних для {asset}")
                    continue
                
                # Аналіз через AI
                signal = self.analyzer.analyze_market(asset, candles)
                
                if signal and signal.get('confidence', 0) >= Config.MIN_CONFIDENCE:
                    signals.append(signal)
                    logger.info(f"✅ Сигнал знайдено: {asset} {signal['direction']} ({signal['confidence']*100:.0f}%)")
                elif signal:
                    logger.info(f"⚠️ Низька впевненість: {asset} ({signal['confidence']*100:.0f}%)")
                else:
                    logger.warning(f"❌ AI не дав сигнал для {asset}")
            
            # Збереження сигналів
            if signals:
                self.data_handler.save_signals(signals)
                logger.info(f"💾 Збережено {len(signals)} сигналів")
                
                # Вивід результатів
                for signal in signals:
                    logger.info(f"   ▶ {signal['asset']}: {signal['direction']} "
                               f"({signal['confidence']*100:.0f}%) "
                               f"вхід {signal['entry_time']} "
                               f"на {signal['duration']}хв")
            else:
                logger.warning("⚠️ Не знайдено жодного сигналу")
            
            # Відключення
            await self.client.disconnect()
            
            return signals
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

async def main():
    generator = SignalGenerator()
    await generator.generate_all_signals()

if __name__ == "__main__":
    asyncio.run(main())
