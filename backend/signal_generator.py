import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from config import Config
from pocket_client import PocketOptionClient
from groq_analyzer import GroqAnalyzer
from data_handler import DataHandler

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
        
        # Отримуємо свічки
        logger.info(f"📊 Запит свічок для {asset}...")
        candles = await self.pocket_client.get_candles(
            asset=asset,
            timeframe=Config.TIMEFRAMES,
            count=50
        )
        
        if not candles or len(candles) == 0:
            logger.error(f"❌ Не вдалося отримати свічки для {asset}")
            return None

        logger.info(f"✅ Отримано {len(candles)} свічок для {asset}")
        
        # ПЕРЕВІРКА: Якщо остання свічка старіша за 5 хвилин - ПРОПУСКАЄМО
        if hasattr(candles[-1], 'timestamp'):
            last_candle_time = candles[-1].timestamp
            current_time = datetime.now()
            
            # Якщо свічка має часовий пояс, видаляємо його для порівняння
            if last_candle_time.tzinfo is not None:
                last_candle_time = last_candle_time.replace(tzinfo=None)
            
            time_diff = (current_time - last_candle_time).total_seconds()
            
            if time_diff > 300:  # 5 хвилин
                logger.error(f"❌ Свічки для {asset} ЗАСТАРІЛІ: {time_diff:.0f} сек ({time_diff/60:.1f} хв)")
                logger.error(f"   Час останньої свічки: {last_candle_time}")
                logger.error(f"   Поточний час: {current_time}")
                logger.error(f"   Пропускаємо актив {asset}")
                return None

    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів - одноразово"""
        logger.info("=" * 60)
        logger.info(f"🚀 ПОЧАТОК ГЕНЕРАЦІЇ СИГНАЛІВ")
        logger.info(f"🕐 Час: {Config.get_kyiv_time().strftime('%Y-%m-%d %H:%M:%S')} (Київ)")
        logger.info("=" * 60)

        try:
            # Виводимо конфігурацію
            logger.info(f"⚙️ Конфігурація:")
            logger.info(f"  - Демо режим: {Config.POCKET_DEMO}")
            logger.info(f"  - Активи: {Config.ASSETS}")
            logger.info(f"  - Таймфрейм: {Config.TIMEFRAMES} сек ({Config.TIMEFRAMES/60} хв)")
            logger.info(f"  - Мін. впевненість: {Config.MIN_CONFIDENCE*100}%")
            logger.info(f"  - Макс. тривалість: {Config.MAX_DURATION} хв")
            logger.info(f"  - Модель AI: {Config.GROQ_MODEL}")
            logger.info(f"  - Часовий пояс: Київ (UTC+2)")
            
            # Перевірка останнього оновлення
            existing_data = self.data_handler.load_signals()
            last_update = existing_data.get('last_update')
            
            if last_update:
                try:
                    last_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    time_diff = (datetime.utcnow() - last_time).total_seconds()
                    
                    if time_diff < Config.SIGNAL_INTERVAL:
                        logger.info(f"⏳ Ще не пройшло 5 хвилин з останньої генерації ({time_diff:.0f} сек)")
                        logger.info(f"   Останнє оновлення: {last_time.strftime('%H:%M:%S')} UTC")
                        return []  # Повертаємо порожній список
                except Exception as e:
                    logger.warning(f"⚠️ Помилка перевірки часу: {e}")
            
            # Підключення до PocketOption
            logger.info("🔗 Підключення до PocketOption...")
            logger.info(f"   Режим: {'DEMO' if Config.POCKET_DEMO else 'REAL'}")
            
            connection_result = await self.pocket_client.connect()
            
            if not connection_result:
                logger.error("❌ Не вдалося підключитися до PocketOption")
                logger.info("⏸️ Пропускаю генерацію сигналів...")
                return []  # Повертаємо порожній список
            
            logger.info("✅ Підключення успішне!")
            logger.info("🎯 Генерую сигнали для активів...")
            
            valid_signals = []
            failed_assets = []
            
            for asset in Config.ASSETS:
                logger.info(f"\n{'='*30}")
                logger.info(f"💰 Обробка активу: {asset}")
                logger.info(f"{'='*30}")
                
                signal = await self.generate_signal(asset)
                if signal:
                    valid_signals.append(signal)
                    logger.info(f"✅ Сигнал для {asset} успішно створений")
                else:
                    logger.warning(f"⚠️ Не створено сигнал для {asset}")
                    failed_assets.append(asset)

            # Зберігаємо сигнали
            if valid_signals:
                logger.info(f"\n💾 Збереження {len(valid_signals)} сигналів...")
                save_result = self.data_handler.save_signals(valid_signals)
                
                if save_result:
                    logger.info(f"✅ Збережено {len(valid_signals)} сигналів")
                    
                    # Виводимо детальну інформацію
                    logger.info(f"\n🎯 ЗГЕНЕРОВАНО {len(valid_signals)} СИГНАЛІВ:")
                    for i, signal in enumerate(valid_signals, 1):
                        logger.info(f"   {i}. {signal['asset']}: {signal['direction']} ({signal['confidence']*100:.1f}%)")
                        logger.info(f"      Вхід: {signal.get('entry_time', 'N/A')}, Тривалість: {signal.get('duration', 'N/A')} хв")
                        logger.info(f"      Волатильність: {signal.get('volatility', 0):.4f}%")
                else:
                    logger.error("❌ Помилка збереження сигналів")
            else:
                logger.warning("⚠️  Не створено жодного сигналу")
                
                if failed_assets:
                    logger.info(f"📉 Активи без сигналів: {', '.join(failed_assets)}")

            # Відключаємося
            logger.info("🔌 Відключення від PocketOption...")
            await self.pocket_client.disconnect()
            logger.info("✅ Відключено від PocketOption")
            
            # Підсумок
            logger.info(f"\n⏱️  Час виконання: {Config.get_kyiv_time().strftime('%H:%M:%S')}")
            logger.info(f"📊 Підсумок: {len(valid_signals)} сигналів з {len(Config.ASSETS)} активів")
            logger.info("=" * 60)
            
            return valid_signals

        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            import traceback
            logger.error(f"📋 Трейс: {traceback.format_exc()}")
            return []

async def main():
    """Головна функція - запускається ТІЛЬКИ ОДИН РАЗ"""
    print("\n" + "="*60)
    print(f"🚀 ЗАПУСК ГЕНЕРАЦІЇ СИГНАЛІВ - {Config.get_kyiv_time().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Ініціалізація логування
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    generator = SignalGenerator()
    signals = await generator.generate_all_signals()
    
    if signals:
        print(f"\n🎯 ЗГЕНЕРОВАНО {len(signals)} СИГНАЛІВ:")
        for signal in signals:
            print(f"   • {signal['asset']}: {signal['direction']} ({signal.get('confidence', 0)*100:.1f}%) - {signal.get('entry_time', 'N/A')}")
    else:
        print("\n⚠️  СИГНАЛІВ НЕ ЗНАЙДЕНО")
    
    print(f"\n✅ Генерація сигналів завершена о {Config.get_kyiv_time().strftime('%H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
