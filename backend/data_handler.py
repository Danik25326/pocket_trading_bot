import json
import os
from datetime import datetime, timedelta
from config import Config

class DataHandler:
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.signals_file = Config.SIGNALS_FILE
        self.history_file = Config.HISTORY_FILE
        self.feedback_file = Config.FEEDBACK_FILE
        self.lessons_file = Config.LESSONS_FILE
        self.create_data_dir()
    
    def create_data_dir(self):
        """Створення директорій для даних"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Створюємо всі необхідні файли
        if not os.path.exists(self.signals_file):
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_update": None,
                    "signals": [],
                    "timezone": "Europe/Kiev (UTC+2)",
                    "total_signals": 0,
                    "active_signals": 0
                }, f, indent=2, ensure_ascii=False)
    
    def save_signals(self, signals):
        """Збереження сигналів - НАЙПРОСТІША ВЕРСІЯ"""
        try:
            if not signals:
                print("⚠️ Немає сигналів для збереження")
                return False
            
            # Фільтруємо сигнали з достатньою впевненістю
            valid_signals = []
            for signal in signals:
                confidence = signal.get('confidence', 0)
                if confidence >= Config.MIN_CONFIDENCE:
                    valid_signals.append(signal)
            
            if not valid_signals:
                print("⚠️ Немає сигналів з достатньою впевненістю")
                return False
            
            # Додаємо просту часову мітку (без часових зон!)
            now = datetime.now()
            for signal in valid_signals:
                signal['generated_at'] = now.isoformat()
                signal['id'] = f"{signal.get('asset', 'unknown')}_{now.strftime('%Y%m%d%H%M%S')}"
            
            # Створюємо новий файл КОЖЕН РАЗ (не додаємо до старих)
            data = {
                "last_update": now.isoformat(),
                "signals": valid_signals,
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": len(valid_signals),
                "active_signals": len(valid_signals)  # Всі нові сигнали вважаємо активними
            }
            
            # Зберігаємо
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Додаємо в історію
            self._add_to_history(valid_signals)
            
            print(f"✅ Збережено {len(valid_signals)} сигналів")
            return True
            
        except Exception as e:
            print(f"❌ Помилка збереження сигналів: {e}")
            import traceback
            print(f"Деталі: {traceback.format_exc()}")
            return False
    
    def load_signals(self):
        """Завантаження сигналів з файлу - ПРОСТА ВЕРСІЯ"""
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Перевіряємо, чи сигнали ще актуальні (не старіші 5 хвилин)
                    if 'signals' in data:
                        current_time = datetime.now()
                        valid_signals = []
                        
                        for signal in data['signals']:
                            # Якщо є час генерації
                            if 'generated_at' in signal:
                                try:
                                    gen_time = datetime.fromisoformat(signal['generated_at'])
                                    # Різниця в хвилинах
                                    diff_minutes = (current_time - gen_time).total_seconds() / 60
                                    
                                    if diff_minutes <= 5:  # До 5 хвилин
                                        valid_signals.append(signal)
                                except:
                                    valid_signals.append(signal)
                        
                        data['signals'] = valid_signals
                        data['active_signals'] = len(valid_signals)
                        data['total_signals'] = len(valid_signals)
                    
                    return data
            return {
                "last_update": None,
                "signals": [],
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": 0,
                "active_signals": 0
            }
        except Exception as e:
            print(f"❌ Помилка завантаження сигналів: {e}")
            return {
                "last_update": None,
                "signals": [],
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": 0,
                "active_signals": 0
            }
    
    def _add_to_history(self, signals):
        """Додавання сигналів до історії"""
        try:
            if not signals:
                return
            
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            now = datetime.now()
            for signal in signals:
                history_entry = signal.copy()
                history_entry['saved_to_history_at'] = now.isoformat()
                history.append(history_entry)
            
            # Обмежуємо історію (100 записів)
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False, default=str)
                
            print(f"📚 Додано {len(signals)} сигналів до історії")
                
        except Exception as e:
            print(f"❌ Помилка додавання в історію: {e}")
