import asyncio
import json
import schedule
import time
from datetime import datetime
from config import Config
from pocket_client import PocketOptionClient
from groq_analyzer import GroqAnalyzer

class SignalGenerator:
    def __init__(self):
        self.pocket_client = PocketOptionClient()
        self.analyzer = GroqAnalyzer()
        self.signals = []
        
    async def generate_signal(self, asset):
        """Генерація одного сигналу"""
        try:
            # Отримуємо свічки
            candles = await self.pocket_client.get_candles(
                asset=asset,
                timeframe=Config.TIMEFRAMES,
                count=50
            )
            
            if not candles:
                return None
            
            # Аналізуємо через AI
            signal = self.analyzer.analyze_market(asset, candles)
            
            if signal and signal.get('confidence', 0) >= Config.MIN_CONFIDENCE:
                signal['generated_at'] = datetime.now().isoformat()
                return signal
                
        except Exception as e:
            print(f"Error generating signal for {asset}: {e}")
            
        return None
    
    async def generate_all_signals(self):
        """Генерація сигналів для всіх активів"""
        print(f"[{datetime.now()}] Генерація сигналів...")
        
        await self.pocket_client.connect()
        
        valid_signals = []
        for asset in Config.ASSETS:
            signal = await self.generate_signal(asset)
            if signal:
                valid_signals.append(signal)
                print(f"✅ Сигнал для {asset}: {signal['direction']} з впевненістю {signal['confidence']*100:.1f}%")
        
        await self.pocket_client.disconnect()
        
        # Зберігаємо сигнали
        self.save_signals(valid_signals)
        return valid_signals
    
    def save_signals(self, signals):
        """Збереження сигналів у JSON файл"""
        try:
            data = {
                'last_update': datetime.now().isoformat(),
                'signals': signals
            }
            
            with open(Config.SIGNALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Сигнали збережено: {len(signals)} шт.")
            
        except Exception as e:
            print(f"Error saving signals: {e}")
    
    def run_scheduler(self):
        """Запуск планувальника (кожні 5 хвилин)"""
        schedule.every(Config.SIGNAL_INTERVAL).seconds.do(
            lambda: asyncio.run(self.generate_all_signals())
        )
        
        print(f"🚀 Сервіс запущено! Сигнали генеруються кожні {Config.SIGNAL_INTERVAL/60} хвилин")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

async def main():
    generator = SignalGenerator()
    
    # Тестовий запуск
    print("🧪 Тестовий запуск...")
    await generator.generate_all_signals()
    
    # Запуск планувальника
    print("⏰ Запуск планувальника...")
    generator.run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
