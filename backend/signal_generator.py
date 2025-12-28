import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Додаємо шляхи для імпортів
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Імпорти після додавання шляхів
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
        """Генерація сигналу для одного активу - ТІЛЬКИ через AI"""
        try:
            logger.info(f"🔍 Аналіз активу: {asset}")
            
            # Перевірка підключення
            if not self.pocket_client.connected:
                logger.info("Підключаюся до PocketOption...")
                if not await self.pocket_client.connect():
                    logger.error(f"❌ Не вдалося підключитися для {asset}")
                    return None
            
            # Отримання свічок
            logger.info(f"📥 Отримую свічки для {asset}...")
            candles = await self.pocket_client.get_candles(
                asset=asset,
                timeframe=Config.TIMEFRAMES,
                count=30
            )
            
            if not candles:
                logger.error(f"❌ Не вдалося отримати свічки для {asset}")
                return None
            
            logger.info(f"📊 Отримано {len(candles)} свічок для {asset}")
            
            # Перевіряємо, чи є достатньо даних для аналізу
            if len(candles) < 10:
                logger.error(f"❌ Недостатньо свічок для аналізу {asset}: {len(candles)} < 10")
                return None
            
            # Аналіз ВИКЛЮЧНО через AI
            signal = self.analyzer.analyze_market(asset, candles)
            
            if signal:
                # Додаємо час генерації (Київ)
                signal['generated_at'] = Config.get_kyiv_time().isoformat()
                signal['asset'] = asset
                
                logger.info(f"✅ AI сигнал для {asset}: {signal['direction']} ({signal['confidence']*100:.1f}%)")
                return signal
            else:
                logger.warning(f"⚠️ AI не дав сигнал для {asset} (ринок нечіткий або критерії не виконані)")
                return None
            
        except Exception as e:
            logger.error(f"❌ КРИТИЧНА помилка генерації сигналу для {asset}: {e}")
            import traceback
            logger.error(f"Трейс помилки: {traceback.format_exc()}")
            return None
    
    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів - ТІЛЬКИ AI"""
        now_kyiv = Config.get_kyiv_time()
        
        logger.info("=" * 60)
        logger.info(f"🚀 ПОЧАТОК ГЕНЕРАЦІЇ СИГНАЛІВ")
        logger.info(f"📅 Час Київ: {now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⚙️ Конфігурація:")
        logger.info(f"  • Активи: {', '.join(Config.ASSETS)}")
        logger.info(f"  • Модель AI: {Config.GROQ_MODEL}")
        logger.info(f"  • Мін. впевненість: {Config.MIN_CONFIDENCE*100}%")
        logger.info(f"  • Таймфрейм: {Config.TIMEFRAMES} секунд")
        logger.info(f"  • Режим: ТІЛЬКИ AI (без резервів)")
        logger.info("=" * 60)
        
        # Перевірка ініціалізації AI
        if not self.analyzer.client:
            logger.error("❌ КРИТИЧНА ПОМИЛКА: Groq AI не ініціалізовано")
            logger.error("🚫 Система не може працювати без AI")
            return []
        
        all_signals = []
        
        try:
            # Підключення до PocketOption
            logger.info("🔗 Підключення до PocketOption...")
            if not await self.pocket_client.connect():
                logger.error("❌ КРИТИЧНА ПОМИЛКА: Не вдалося підключитися до PocketOption")
                return []
            
            # Генерація сигналів для кожного активу
            for asset in Config.ASSETS:
                logger.info(f"📈 Обробка активу: {asset}")
                signal = await self.generate_signal_for_asset(asset)
                if signal:
                    all_signals.append(signal)
                    logger.info(f"✅ Додано AI сигнал для {asset}")
                else:
                    logger.warning(f"⚠️ AI не дав сигнал для {asset}")
                
                # Невелика пауза між активами
                await asyncio.sleep(1)
            
            # Збереження сигналів (тільки якщо є)
            if all_signals:
                success = self.data_handler.save_signals(all_signals)
                if success:
                    logger.info(f"💾 Успішно збережено {len(all_signals)} AI сигналів")
                    
                    # Вивід інформації про сигнали
                    logger.info("📋 Згенеровані AI сигнали:")
                    for signal in all_signals:
                        logger.info(
                            f"   🤖 {signal['asset']}: {signal['direction']} "
                            f"({signal['confidence']*100:.1f}%) "
                            f"о {signal.get('entry_time', 'N/A')} "
                            f"[Київ: {now_kyiv.strftime('%H:%M')}]"
                        )
                else:
                    logger.error("❌ Не вдалося зберегти сигнали")
            else:
                logger.warning("⚠️ AI не згенерував жодного сигналу для всіх активів")
            
            # Відключення
            await self.pocket_client.disconnect()
            
            # Статистика
            stats = self.data_handler.get_statistics()
            logger.info(f"📈 Статистика: {stats.get('total_signals', 0)} AI сигналів в історії")
            
            return all_signals
            
        except Exception as e:
            logger.error(f"💥 КРИТИЧНА ПОМИЛКА: {e}")
            import traceback
            logger.error(f"Трейс помилки: {traceback.format_exc()}")
            
            # Намагаємося відключитися навіть при помилці
            try:
                await self.pocket_client.disconnect()
            except:
                pass
            
            return []

async def main():
    """Головна функція - ТІЛЬКИ AI"""
    generator = SignalGenerator()
    signals = await generator.generate_all_signals()
    
    if signals:
        print(f"\n🎯 ЗГЕНЕРОВАНО {len(signals)} AI СИГНАЛІВ:")
        for signal in signals:
            print(f"   🤖 {signal['asset']}: {signal['direction']} ({signal['confidence']*100:.1f}%) - {signal.get('entry_time', 'N/A')} Київ")
    else:
        print("\n⚠️ AI НЕ ЗНАЙШОВ ЖОДНОГО СИГНАЛУ")
        print("   Причина: ринок нечіткий або не виконані критерії")
    
    return signals

if __name__ == "__main__":
    asyncio.run(main())
