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
        self.feedback_file = Config.FEEDBACK_FILE
        self.lessons_file = Config.LESSONS_FILE
        self.kyiv_tz = pytz.timezone('Europe/Kiev')
        self.create_data_dir()
    
    def create_data_dir(self):
        """Створення директорій для даних"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Створюємо всі необхідні файли, якщо їх немає
        if not os.path.exists(self.signals_file):
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_update": None,
                    "signals": [],
                    "timezone": "Europe/Kiev (UTC+2)",
                    "total_signals": 0,
                    "active_signals": 0,
                    "generation_count": 0
                }, f, indent=2, ensure_ascii=False)
        
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
                
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "feedback_history": [],
                    "success_count": 0,
                    "total_feedback": 0,
                    "accuracy_percentage": 0
                }, f, indent=2, ensure_ascii=False)
        
        if not os.path.exists(self.lessons_file):
            with open(self.lessons_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "lessons": [],
                    "last_learning": None,
                    "learned_patterns": []
                }, f, indent=2, ensure_ascii=False)
    
    def save_signals(self, signals):
        """Збереження сигналів з обмеженням до 6 останніх"""
        try:
            if not signals:
                print("⚠️ Немає сигналів для збереження")
                return False
            
            # Фільтруємо сигнали з достатньою впевненістю
            valid_signals = []
            for signal in signals:
                confidence = signal.get('confidence', 0)
                if confidence >= Config.MIN_CONFIDENCE:
                    # Переконуємося, що є всі необхідні поля
                    if 'asset' not in signal or 'direction' not in signal:
                        continue
                    
                    # Додаємо ID, якщо немає
                    if 'id' not in signal:
                        now_kyiv = Config.get_kyiv_time()
                        signal['id'] = f"{signal['asset']}_{now_kyiv.strftime('%Y%m%d%H%M%S')}"
                    
                    # Додаємо час зникнення (10 хвилин після генерації)
                    if 'generated_at' in signal:
                        gen_time = self._parse_datetime(signal['generated_at'])
                        if gen_time:
                            expiry_time = gen_time + timedelta(minutes=10)
                            signal['expires_at'] = expiry_time.isoformat()
                    
                    valid_signals.append(signal)
            
            if not valid_signals:
                print("⚠️ Немає сигналів з достатньою впевненістю для збереження")
                return False
            
            now_kyiv = Config.get_kyiv_time()
            
            # Завантажуємо існуючі сигнали
            existing_data = self.load_signals()
            existing_signals = existing_data.get('signals', [])
            
            # Фільтруємо старі сигнали (старіші 10 хвилин)
            current_signals = []
            for signal in existing_signals:
                try:
                    gen_time_str = signal.get('generated_at')
                    if gen_time_str:
                        gen_time = self._parse_datetime(gen_time_str)
                        if gen_time and (now_kyiv - gen_time <= timedelta(minutes=10)):
                            current_signals.append(signal)
                except:
                    continue
            
            # Додаємо нові сигнали
            all_signals = current_signals + valid_signals
            
            # Обмежуємо загальну кількість сигналів (максимум 6)
            if len(all_signals) > Config.MAX_SIGNALS_ON_SITE:
                # Залишаємо тільки найновіші 6 сигналів
                all_signals = sorted(
                    all_signals, 
                    key=lambda x: self._parse_datetime(x.get('generated_at', '') or ''),
                    reverse=True
                )[:Config.MAX_SIGNALS_ON_SITE]
            
            # Рахуємо активні сигнали
            active_count = 0
            for signal in all_signals:
                if self._is_signal_active(signal):
                    active_count += 1
            
            # Оновлюємо дані
            data = {
                "last_update": now_kyiv.isoformat(),
                "signals": all_signals,
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": len(all_signals),
                "active_signals": active_count,
                "generation_count": existing_data.get('generation_count', 0) + 1
            }
            
            # Зберігаємо
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Додаємо в історію
            self._add_to_history(valid_signals)
            
            # Оновлюємо статистику навчання
            self.update_learning_stats()
            
            print(f"💾 Збережено {len(valid_signals)} сигналів. Активних: {active_count}")
            return True
            
        except Exception as e:
            print(f"❌ Помилка збереження сигналів: {e}")
            import traceback
            print(f"Деталі: {traceback.format_exc()}")
            return False
    
    def _parse_datetime(self, datetime_str):
        """Парсинг datetime з рядка з обробкою різних форматів"""
        if not datetime_str:
            return None
        
        try:
            # Спроба парсингу ISO формату
            if 'Z' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(datetime_str)
            
            # Якщо немає часового поясу, додаємо UTC
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            
            # Конвертуємо в Київський час
            return dt.astimezone(self.kyiv_tz)
            
        except Exception as e:
            print(f"⚠️ Помилка парсингу часу '{datetime_str}': {e}")
            return None
    
    def load_signals(self):
        """Завантаження сигналів з файлу"""
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Переконуємося, що є всі обов'язкові поля
                    if 'signals' not in data:
                        data['signals'] = []
                    if 'total_signals' not in data:
                        data['total_signals'] = len(data.get('signals', []))
                    if 'active_signals' not in data:
                        data['active_signals'] = len([s for s in data.get('signals', []) if self._is_signal_active(s)])
                    if 'generation_count' not in data:
                        data['generation_count'] = 0
                    
                    return data
            return {
                "last_update": None,
                "signals": [],
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": 0,
                "active_signals": 0,
                "generation_count": 0
            }
        except Exception as e:
            print(f"❌ Помилка завантаження сигналів: {e}")
            return {
                "last_update": None,
                "signals": [],
                "timezone": "Europe/Kiev (UTC+2)",
                "total_signals": 0,
                "active_signals": 0,
                "generation_count": 0
            }
    
    def _is_signal_active(self, signal):
        """Перевірка чи сигнал ще активний (до 10 хвилин після генерації)"""
        try:
            now_kyiv = Config.get_kyiv_time()
            
            # Час генерації сигналу
            gen_time_str = signal.get('generated_at')
            if not gen_time_str:
                return True  # ✅ ЗМІНА: якщо немає часу, вважаємо активним
            
            generated_at = self._parse_datetime(gen_time_str)
            if not generated_at:
                return True  # ✅ ЗМІНА: при помилці парсингу вважаємо активним
            
            # Сигнал активний тільки 10 хвилин з моменту генерації
            time_since_generation = now_kyiv - generated_at
            is_active = time_since_generation <= timedelta(minutes=10)
            
            # ✅ ВИДАЛЕНО зайве логування
            return is_active
            
        except Exception as e:
            print(f"⚠️ Помилка перевірки активності сигналу: {e}")
            return True  # ✅ ЗМІНА: при помилці вважаємо активним
    
    def _add_to_history(self, signals):
        """Додавання сигналів до історії з обмеженням"""
        try:
            if not signals:
                return
            
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            now_kyiv = Config.get_kyiv_time()
            for signal in signals:
                # Створюємо копію сигналу для історії
                history_entry = signal.copy()
                history_entry['saved_at'] = now_kyiv.isoformat()
                history_entry['history_id'] = f"{signal.get('asset', 'unknown')}_{now_kyiv.strftime('%Y%m%d%H%M%S')}"
                history_entry['status'] = 'saved'
                history.append(history_entry)
            
            # Обмежуємо історію (останні 100 записів)
            if len(history) > Config.MAX_SIGNALS_HISTORY:
                history = history[-Config.MAX_SIGNALS_HISTORY:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False, default=str)
                
            print(f"📚 Додано {len(signals)} сигналів до історії")
                
        except Exception as e:
            print(f"❌ Помилка додавання в історію: {e}")
    
    def save_feedback(self, signal_id, success, user_comment=""):
        """Збереження відгуку про результат угоди для навчання AI"""
        try:
            if not Config.FEEDBACK_ENABLED:
                return False
            
            # Завантажуємо існуючі feedback
            feedback_data = {}
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback_data = json.load(f)
            
            feedback_history = feedback_data.get('feedback_history', [])
            
            now_kyiv = Config.get_kyiv_time()
            feedback_entry = {
                'signal_id': signal_id,
                'success': success,
                'user_comment': user_comment,
                'feedback_at': now_kyiv.isoformat(),
                'learned': False
            }
            
            feedback_history.append(feedback_entry)
            
            # Оновлюємо статистику
            total_feedback = len(feedback_history)
            success_count = len([f for f in feedback_history if f.get('success', False)])
            accuracy = (success_count / total_feedback * 100) if total_feedback > 0 else 0
            
            feedback_data.update({
                'feedback_history': feedback_history,
                'success_count': success_count,
                'total_feedback': total_feedback,
                'accuracy_percentage': round(accuracy, 2)
            })
            
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Запускаємо навчання AI на основі feedback
            self.learn_from_feedback()
            
            print(f"💾 Збережено відгук для сигналу {signal_id}: {'✅ Успіх' if success else '❌ Невдача'}")
            print(f"📊 Нова точність AI: {accuracy:.2f}% ({success_count}/{total_feedback})")
            return True
            
        except Exception as e:
            print(f"❌ Помилка збереження відгуку: {e}")
            return False
    
    def learn_from_feedback(self):
        """Навчання ШІ на основі feedback (аналіз чому сигнал був правильний/неправильний)"""
        try:
            if not os.path.exists(self.feedback_file):
                return []
            
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedback_data = json.load(f)
            
            feedback = feedback_data.get('feedback_history', [])
            
            unlearned = [fb for fb in feedback if not fb.get('learned', False)]
            
            if not unlearned:
                return []
            
            # Завантажуємо уроки
            lessons_data = {}
            if os.path.exists(self.lessons_file):
                with open(self.lessons_file, 'r', encoding='utf-8') as f:
                    lessons_data = json.load(f)
            
            lessons = lessons_data.get('lessons', [])
            
            now_kyiv = Config.get_kyiv_time()
            new_lessons = []
            
            for fb in unlearned:
                # Аналізуємо чому сигнал був правильний/неправильний
                lesson = {
                    'signal_id': fb.get('signal_id', ''),
                    'success': fb.get('success', False),
                    'feedback_at': fb.get('feedback_at', ''),
                    'learned_at': now_kyiv.isoformat(),
                    'asset': fb.get('signal_id', '').split('_')[0] if '_' in fb.get('signal_id', '') else '',
                    'patterns': self._extract_patterns(fb),
                    'analysis': self._analyze_feedback(fb)  # Аналіз причин
                }
                new_lessons.append(lesson)
                
                fb['learned'] = True
            
            # Оновлюємо feedback файл
            feedback_data['feedback_history'] = feedback
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Додаємо нові уроки
            all_lessons = lessons + new_lessons
            
            # Оновлюємо уроки
            lessons_data.update({
                'lessons': all_lessons,
                'last_learning': now_kyiv.isoformat(),
                'learned_patterns': self._update_learned_patterns(all_lessons)
            })
            
            with open(self.lessons_file, 'w', encoding='utf-8') as f:
                json.dump(lessons_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"🧠 ШІ навчився на {len(new_lessons)} нових прикладах")
            return new_lessons
            
        except Exception as e:
            print(f"❌ Помилка навчання ШІ: {e}")
            return []
    
    def _extract_patterns(self, feedback_entry):
        """Витягнення шаблонів з feedback (заглушка)"""
        return []
    
    def _analyze_feedback(self, feedback_entry):
        """Аналіз причин успіху/невдачі сигналу"""
        signal_id = feedback_entry.get('signal_id', '')
        success = feedback_entry.get('success', False)
        
        analysis = {
            'reason': 'success' if success else 'failure',
            'learned_at': datetime.now().isoformat(),
            'recommendation': 'Повторити подібні умови' if success else 'Уникати подібних умов'
        }
        
        return analysis
    
    def _update_learned_patterns(self, all_lessons):
        """Оновлення вивчених шаблонів (заглушка)"""
        return []
    
    def update_learning_stats(self):
        """Оновлення статистики навчання"""
        pass
    
    def auto_cleanup_old_signals(self):
        """Автоматичне очищення сигналів старіших 10 хвилин"""
        try:
            print("🧹 Автоматичне очищення старих сигналів...")
            
            data = self.load_signals()
            signals = data.get('signals', [])
            
            if len(signals) == 0:
                return
            
            now_kyiv = Config.get_kyiv_time()
            active_signals = []
            removed_count = 0
            
            for signal in signals:
                try:
                    gen_time_str = signal.get('generated_at')
                    if gen_time_str:
                        gen_time = self._parse_datetime(gen_time_str)
                        if gen_time and (now_kyiv - gen_time <= timedelta(minutes=10)):
                            active_signals.append(signal)
                        else:
                            removed_count += 1
                            print(f"🗑️ Видаляємо старий сигнал: {signal.get('asset')}")
                except:
                    continue
            
            # Оновлюємо файл
            data['signals'] = active_signals
            data['total_signals'] = len(active_signals)
            data['active_signals'] = len([s for s in active_signals if self._is_signal_active(s)])
            
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ Автоочищення: видалено {removed_count} старих сигналів, залишено {len(active_signals)} актуальних")
            
        except Exception as e:
            print(f"❌ Помилка автоочищення: {e}")
