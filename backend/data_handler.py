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
        self.kyiv_tz = pytz.timezone('Europe/Kiev')
        self.create_data_dir()
    
    def create_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_signals(self):
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"last_update": None, "signals": []}
        except Exception as e:
            print(f"Error loading signals: {e}")
            return {"last_update": None, "signals": []}
    
    def save_signals(self, signals):
        # Київський час
        kyiv_time = datetime.now(self.kyiv_tz)
        
        data = {
            "last_update": kyiv_time.isoformat(),
            "last_update_str": kyiv_time.strftime('%Y-%m-%d %H:%M:%S'),
            "timezone": "Europe/Kiev (UTC+2)",
            "signals": signals
        }
        
        try:
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.add_to_history(signals)
            
            # Очищаємо застарілі сигнали (старіші 1 години)
            self.clean_old_signals(hours=1)
            
            return True
        except Exception as e:
            print(f"Error saving signals: {e}")
            return False
    
    def add_to_history(self, signals):
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            kyiv_time = datetime.now(self.kyiv_tz)
            for signal in signals:
                signal_with_time = {
                    **signal,
                    "saved_at": kyiv_time.isoformat(),
                    "saved_at_str": kyiv_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                history.append(signal_with_time)
            
            if len(history) > 1000:
                history = history[-1000:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error adding to history: {e}")
    
    def clean_old_signals(self, hours=1):
        try:
            data = self.load_signals()
            if not data.get("signals"):
                return
            
            current_time = datetime.now(self.kyiv_tz)
            filtered_signals = []
            
            for signal in data["signals"]:
                signal_time_str = signal.get("generated_at") or signal.get("timestamp")
                if not signal_time_str:
                    continue
                
                try:
                    signal_time = datetime.fromisoformat(signal_time_str)
                    if signal_time.tzinfo is None:
                        signal_time = self.kyiv_tz.localize(signal_time)
                    
                    if current_time - signal_time <= timedelta(hours=hours):
                        filtered_signals.append(signal)
                except:
                    continue
            
            data["signals"] = filtered_signals
            
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error cleaning old signals: {e}")
    
    def get_active_signals(self, max_minutes_old=10):
        """Повертає сигнали, які не старіші за max_minutes_old хвилин"""
        try:
            data = self.load_signals()
            signals = data.get("signals", [])
            
            current_time = datetime.now(self.kyiv_tz)
            
            active_signals = []
            for signal in signals:
                entry_time_str = signal.get("entry_time")
                if not entry_time_str:
                    continue
                
                try:
                    today = current_time.date()
                    entry_time = datetime.strptime(entry_time_str, "%H:%M").time()
                    entry_datetime = self.kyiv_tz.localize(datetime.combine(today, entry_time))
                    
                    time_diff = current_time - entry_datetime
                    if time_diff <= timedelta(minutes=max_minutes_old) and time_diff >= timedelta(minutes=0):
                        active_signals.append(signal)
                    elif time_diff < timedelta(minutes=0):
                        active_signals.append(signal)
                except Exception as e:
                    print(f"Error parsing entry_time {entry_time_str}: {e}")
                    continue
            
            return active_signals
        except Exception as e:
            print(f"Error getting active signals: {e}")
            return []
    
    def get_statistics(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                if not history:
                    return {"total_signals": 0, "success_rate": 0}
                
                total = len(history)
                successful = sum(1 for s in history if s.get("actual_result") == "win")
                
                return {
                    "total_signals": total,
                    "successful_signals": successful,
                    "success_rate": successful / total if total > 0 else 0,
                    "last_week_count": len([s for s in history if self.is_recent(s.get("saved_at"), days=7)])
                }
            return {"total_signals": 0, "success_rate": 0}
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {"total_signals": 0, "success_rate": 0}
    
    def is_recent(self, timestamp, days=7):
        try:
            if not timestamp:
                return False
            signal_time = datetime.fromisoformat(timestamp)
            return (datetime.now() - signal_time).days <= days
        except:
            return False
