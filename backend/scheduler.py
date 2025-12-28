import schedule
import time
import asyncio
import threading
from datetime import datetime
from config import Config
from signal_generator import SignalGenerator

class Scheduler:
    def __init__(self):
        self.generator = SignalGenerator()
        self.running = False
        self.thread = None
    
    def job(self):
        """Завдання для планувальника"""
        kyiv_time = Config.get_kyiv_time()
        print(f"[{kyiv_time.strftime('%Y-%m-%d %H:%M:%S')} Київ] Запуск генерації сигналів за розкладом")
        try:
            asyncio.run(self.generator.generate_all_signals())
        except Exception as e:
            print(f"Помилка в запланованому завданні: {e}")
    
    def run_scheduler(self):
        """Запуск планувальника в окремому потоці"""
        self.running = True
        
        # Запускаємо одразу при старті
        kyiv_time = Config.get_kyiv_time()
        print(f"[INIT] Перший запуск генерації сигналів о {kyiv_time.strftime('%H:%M:%S')} Київ...")
        self.job()
        
        # Налаштовуємо розклад (кожні 5 хвилин)
        schedule.every(5).minutes.do(self.job)
        
        print(f"[SCHEDULER] Планувальник запущено. Наступне оновлення: {schedule.next_run()}")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Запуск планувальника в окремому потоці"""
        if not self.running:
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            print("[SCHEDULER] Планувальник запущено в окремому потоці")
    
    def stop(self):
        """Зупинка планувальника"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[SCHEDULER] Планувальник зупинено")

# Для локального тестування
if __name__ == "__main__":
    scheduler = Scheduler()
    
    try:
        scheduler.start()
        # Тримаємо головний потік активним
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SCHEDULER] Отримано сигнал зупинки...")
        scheduler.stop()
