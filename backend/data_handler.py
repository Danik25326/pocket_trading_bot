import json
import os
from datetime import datetime, timedelta
import pytz
from config import Config

class DataHandler:
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.signals_file = Config.SIGNALS_FILE
        self.history_file = Config.HISTORY_FILE
        self.create_directories()
    
    def create_directories(self):
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_signals(self):
        """Завантаження сигналів"""
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "last_update": None,
            "signals": [],
            "statistics": {
                "total_generated": 0,
                "high_confidence": 0
            }
        }
    
    def save_signals(self, new_signals):
        """Збереження сигналів"""
        try:
            data = self.load_signals()
            kyiv_tz = pytz.timezone(Config.TIMEZONE)
            
            # Додаємо нові сигнали
            for signal in new_signals:
                signal['id'] = f"{signal['asset']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                signal['generated_at'] = datetime.now(kyiv_tz).isoformat()
                data['signals'].append(signal)
            
            # Фільтруємо старі сигнали (старіші 10 хвилин)
            current_time = datetime.now(kyiv_tz)
            data['signals'] = [
                s for s in data['signals'] 
                if self._is_signal_active(s, current_time)
            ]
            
            # Обмежуємо кількість (останні 20)
            data['signals'] = data['signals'][-20:]
            
            # Оновлюємо статистику
            data['last_update'] = current_time.isoformat()
            data['statistics']['total_generated'] += len(new_signals)
            data['statistics']['high_confidence'] = len([
                s for s in data['signals'] 
                if s.get('confidence', 0) >= Config.MIN_CONFIDENCE
            ])
            
            # Зберігаємо
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Додаємо в історію
            self._add_to_history(new_signals)
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка збереження: {str(e)}")
            return False
    
    def _is_signal_active(self, signal, current_time):
        """Перевірка чи сигнал активний"""
        try:
            entry_time_str = signal.get('entry_time')
            if not entry_time_str:
                return False
            
            # Парсимо час входу
            entry_hour, entry_minute = map(int, entry_time_str.split(':'))
            entry_date = current_time.replace(
                hour=entry_hour, 
                minute=entry_minute, 
                second=0, 
                microsecond=0
            )
            
            # Якщо час входу вже минув
            if entry_date < current_time:
                # Перевіряємо чи не старіше 10 хвилин
                time_diff = current_time - entry_date
                return time_diff <= timedelta(minutes=Config.SIGNAL_LIFETIME_MINUTES)
            
            # Якщо час входу в майбутньому
            return True
            
        except:
            return False
    
    def get_active_signals(self):
        """Отримання активних сигналів"""
        data = self.load_signals()
        kyiv_tz = pytz.timezone(Config.TIMEZONE)
        current_time = datetime.now(kyiv_tz)
        
        active_signals = [
            s for s in data['signals']
            if self._is_signal_active(s, current_time)
        ]
        
        return {
            "last_update": data['last_update'],
            "signals": active_signals,
            "count": len(active_signals)
        }
    
    def _add_to_history(self, signals):
        """Додавання до історії"""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            kyiv_tz = pytz.timezone(Config.TIMEZONE)
            for signal in signals:
                signal['saved_at'] = datetime.now(kyiv_tz).isoformat()
                history.append(signal)
            
            # Обмежуємо історію
            if len(history) > 1000:
                history = history[-1000:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except:
            pass
