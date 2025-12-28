import json
import logging
from groq import Groq
from datetime import datetime, timedelta
import pytz
from config import Config

logger = logging.getLogger("signal_bot")

class GroqAnalyzer:
    def __init__(self):
        self.client = None
        self.initialize()
    
    def initialize(self):
        try:
            if not Config.GROQ_API_KEY:
                logger.error("❌ GROQ_API_KEY не знайдено!")
                return
            
            # Проста ініціалізація
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info(f"✅ Groq AI ініціалізовано (модель: {Config.GROQ_MODEL})")
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації Groq: {e}")
    
    def analyze_market(self, asset, candles_data):
        """Аналіз ринку через Groq AI - ОПТИМІЗОВАНО ДЛЯ LLaMA 3.3"""
        if not self.client:
            logger.error("❌ Groq AI не ініціалізовано")
            return None
        
        try:
            # Форматуємо свічки
            candles_str = self._format_candles_for_llama(candles_data)
            
            # Поточний час Київ
            kyiv_tz = pytz.timezone('Europe/Kiev')
            now_kyiv = datetime.now(kyiv_tz)
            entry_time = (now_kyiv + timedelta(minutes=1)).strftime('%H:%M')
            
            # Простий промпт для LLaMA 3.3
            prompt = f"""Аналіз ринку для бінарних опціонів:
            
Актив: {asset}
Час аналізу: {now_kyiv.strftime('%H:%M')} (Київ UTC+2)
Таймфрейм: 2 хвилини

Останні 15 свічок:
{candles_str}

Проаналізуй ринок та дай торговий сигнал для бінарного опціону на 2 хвилини.
Обґрунтуй аналіз і вкажи впевненість від 70 до 95%.

ФОРМАТ ВІДПОВІДІ (JSON):
{{
    "asset": "{asset}",
    "direction": "UP" або "DOWN",
    "confidence": число від 0.7 до 0.95,
    "entry_time": "{entry_time}",
    "duration": 2,
    "reason": "коротке обґрунтування технічного аналізу",
    "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}"
}}"""
            
            logger.info(f"🧠 Аналізую {asset} через LLaMA 3.3...")
            
            completion = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "Ти професійний трейдер бінарних опціонів. Даєш точні торгові сигнали з обґрунтуванням."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            response_text = completion.choices[0].message.content
            
            # Чистимо від markdown
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            response = json.loads(response_text)
            
            # Додаємо обов'язкові поля
            response['generated_at'] = now_kyiv.isoformat()
            
            # Перевіряємо впевненість
            confidence = response.get('confidence', 0)
            if confidence < Config.MIN_CONFIDENCE:
                logger.warning(f"⚠️ Низька впевненість: {confidence*100:.1f}%")
                return None
            
            # Перевіряємо напрямок
            direction = str(response.get('direction', '')).upper()
            if direction not in ['UP', 'DOWN']:
                logger.warning(f"⚠️ Невірний напрямок: {direction}")
                return None
            
            logger.info(f"✅ Сигнал: {direction} ({confidence*100:.1f}%)")
            return response
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Помилка парсингу JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Помилка AI: {e}")
            return None
    
    def _format_candles_for_llama(self, candles):
        """Форматування свічок для LLaMA 3.3"""
        if not candles:
            return "Немає даних"
        
        formatted = []
        # Беремо останні 15 свічок
        for i, candle in enumerate(candles[-15:]):
            try:
                # Спрощений парсинг
                if hasattr(candle, 'close'):
                    close = candle.close
                    open_price = candle.open
                    high = candle.high
                    low = candle.low
                elif isinstance(candle, dict):
                    close = candle.get('close', 0)
                    open_price = candle.get('open', 0)
                    high = candle.get('high', 0)
                    low = candle.get('low', 0)
                elif isinstance(candle, (list, tuple)) and len(candle) >= 5:
                    open_price = candle[1]
                    high = candle[2]
                    low = candle[3]
                    close = candle[4]
                else:
                    continue
                
                # Форматуємо
                formatted.append(
                    f"{i+1:2d}. O:{float(open_price):.5f} "
                    f"H:{float(high):.5f} L:{float(low):.5f} "
                    f"C:{float(close):.5f}"
                )
            except Exception:
                continue
        
        return "\n".join(formatted) if formatted else "Немає даних"
