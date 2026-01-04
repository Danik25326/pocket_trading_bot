import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.parent
USAGE_FILE = BASE_DIR / 'data' / 'usage.json'

class UsageLimits:
    def __init__(self):
        self.max_tokens_per_day = int(os.getenv('MAX_TOKENS_PER_DAY', 200000))
        self.max_requests_per_day = int(os.getenv('MAX_REQUESTS_PER_DAY', 1000))
        self.usage_data = self.load_usage()
    
    def load_usage(self):
        """Завантаження даних про використання"""
        if USAGE_FILE.exists():
            with open(USAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Створюємо новий файл
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            "date": today,
            "tokens_used": 0,
            "requests_used": 0,
            "last_reset": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "daily_history": []
        }
    
    def save_usage(self):
        """Збереження даних про використання"""
        USAGE_FILE.parent.mkdir(exist_ok=True)
        with open(USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
    
    def reset_if_new_day(self):
        """Скидання лічильників на новий день"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.usage_data['date'] != today:
            # Зберігаємо історію попереднього дня
            if 'daily_history' not in self.usage_data:
                self.usage_data['daily_history'] = []
            
            self.usage_data['daily_history'].append({
                "date": self.usage_data['date'],
                "tokens_used": self.usage_data['tokens_used'],
                "requests_used": self.usage_data['requests_used']
            })
            
            # Обмежуємо історію останніми 30 днями
            if len(self.usage_data['daily_history']) > 30:
                self.usage_data['daily_history'] = self.usage_data['daily_history'][-30:]
            
            # Скидаємо лічильники
            self.usage_data['date'] = today
            self.usage_data['tokens_used'] = 0
            self.usage_data['requests_used'] = 0
            self.usage_data['last_reset'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_usage()
            print(f"🔄 Лічильники скинуто на новий день: {today}")
    
    def can_generate(self, estimated_tokens=8000, estimated_requests=3):
        """Перевірка, чи можна генерувати сигнали"""
        self.reset_if_new_day()
        
        tokens_remaining = self.max_tokens_per_day - self.usage_data['tokens_used']
        requests_remaining = self.max_requests_per_day - self.usage_data['requests_used']
        
        # Перевіряємо, чи вистачає ресурсів на цю генерацію
        can_generate = (tokens_remaining >= estimated_tokens and 
                       requests_remaining >= estimated_requests)
        
        # Вивід для GitHub Actions outputs
        print(f"::set-output name=can_generate::{str(can_generate).lower()}")
        print(f"::set-output name=tokens_used::{self.usage_data['tokens_used']}")
        print(f"::set-output name=requests_used::{self.usage_data['requests_used']}")
        print(f"::set-output name=tokens_remaining::{tokens_remaining}")
        print(f"::set-output name=requests_remaining::{requests_remaining}")
        
        return can_generate
    
    def record_usage(self, tokens_used, requests_used):
        """Запис використання ресурсів"""
        self.usage_data['tokens_used'] += tokens_used
        self.usage_data['requests_used'] += requests_used
        self.save_usage()
        
        print(f"📊 Використано: {tokens_used} токенів, {requests_used} запитів")
        print(f"📈 Загалом за день: {self.usage_data['tokens_used']}/{self.max_tokens_per_day} токенів, "
              f"{self.usage_data['requests_used']}/{self.max_requests_per_day} запитів")

if __name__ == "__main__":
    limits = UsageLimits()
    
    # Оцінка використання для однієї генерації
    # 3 активи * ~2500 токенів на запит = ~7500 токенів
    # 3 запити до AI
    can_generate = limits.can_generate(estimated_tokens=8000, estimated_requests=3)
    
    if not can_generate:
        print("❌ Досягнуто денних лімітів. Генерацію пропущено.")
        sys.exit(1)
    else:
        print("✅ Ліміти дозволяють генерацію")
        sys.exit(0)
