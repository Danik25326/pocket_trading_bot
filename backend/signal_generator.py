import asyncio
import logging
from datetime import datetime
from config import Config
from pocket_client import PocketOptionClient
from groq_analyzer import GroqAnalyzer
from data_handler import DataHandler

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("signal_bot")

class SignalGenerator:
    def __init__(self):
        self.pocket_client = PocketOptionClient()
        self.analyzer = GroqAnalyzer()
        self.data_handler = DataHandler()
    
    async def generate_signal_for_asset(self, asset):
        """Генерація сигналу для одного активу"""
        try:
            logger.info(f"🔍 Аналіз: {asset}")
            
            # Отримання свічок
            candles = await self.pocket_client.get_candles(
                asset=asset,
                timeframe=Config.TIMEFRAMES,
                count=20
            )
            
            if not candles or len(candles) < 10:
                logger.warning(f"⚠️ Недостатньо даних для {asset}")
                return None
            
            # Аналіз через AI
            signal = self.analyzer.analyze_market(asset, candles)
            
            if signal:
                logger.info(f"✅ Сигнал для {asset}: {signal.get('direction')}")
                return signal
            else:
                logger.warning(f"AI не дав сигнал для {asset}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Помилка для {asset}: {e}")
            return None
    
    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів"""
        logger.info("=" * 50)
        logger.info(f"🚀 Генерація сигналів - {datetime.now().strftime('%H:%M')}")
        logger.info(f"📊 Активи: {', '.join(Config.ASSETS)}")
        logger.info(f"🧠 Модель: {Config.GROQ_MODEL}")
        logger.info("=" * 50)
        
        all_signals = []
        
        try:
            # Генерація для кожного активу
            for asset in Config.ASSETS:
                signal = await self.generate_signal_for_asset(asset)
                if signal:
                    all_signals.append(signal)
                    logger.info(f"✅ Додано сигнал для {asset}")
                else:
                    logger.warning(f"⚠️ Немає сигналу для {asset}")
                
                await asyncio.sleep(1)
            
            # Збереження
            if all_signals:
                success = self.data_handler.save_signals(all_signals)
                if success:
                    logger.info(f"💾 Збережено {len(all_signals)} сигналів")
                else:
                    logger.error("❌ Не вдалося зберегти")
            else:
                logger.warning("⚠️ Немає жодного сигналу")
            
            # Відключення
            await self.pocket_client.disconnect()
            
            return all_signals
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            import traceback
            logger.error(f"Трейс: {traceback.format_exc()}")
            return []

async def main():
    """Головна функція"""
    generator = SignalGenerator()
    signals = await generator.generate_all_signals()
    
    if signals:
        print(f"\n🎯 Згенеровано {len(signals)} сигналів:")
        for signal in signals:
            print(f"   • {signal['asset']}: {signal['direction']} ({signal.get('confidence', 0)*100:.1f}%)")
    else:
        print("\n⚠️ Сигналів не знайдено")
    
    return signals

if __name__ == "__main__":
    asyncio.run(main())
