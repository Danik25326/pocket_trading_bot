import json
import logging
from groq import Groq
from datetime import datetime, timedelta
import pytz
from config import Config

logger = logging.getLogger("signal_bot")

class GroqAnalyzer:
    def __init__(self):
        # Перевіряємо наявність API ключа
        if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == 'your_groq_api_key_here':
            logger.error("❌ GROQ_API_KEY не налаштовано! Перевірте GitHub Secrets")
            self.client = None
        else:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info(f"✅ Groq AI ініціалізовано (модель: {Config.GROQ_MODEL})")
        
    def analyze_market(self, asset, candles_data):
        """
        Аналіз ринку через Groq AI
        Повертає сигнал та впевненість
        """
        # Перевіряємо, чи ініціалізовано клієнт
        if not self.client:
            logger.error("Groq AI не ініціалізовано. Пропускаємо аналіз.")
            return None
            
        # Форматуємо дані для AI
        candles_str = self._format_candles(candles_data)
        
        # Поточний час в UTC+2 (Київ)
        kyiv_tz = pytz.timezone('Europe/Kiev')
        now_kyiv = datetime.now(kyiv_tz)
        current_time_str = now_kyiv.strftime("%H:%M")
        
        prompt = f"""
        Ти експертний трейдер з бінарними опціонами. Проаналізуй наступні дані:
        
        Актив: {asset}
        Таймфрейм: 2 хвилини
        Останні 50 свічок:
        {candles_str}
        
        Проаналізуй:
        1. Загальний тренд
        2. Рівні підтримки та опору
        3. Ключові технічні індикатори (RSI, MACD, Stochastic тощо)
        4. Волатильність
        
        Дай прогноз на наступні 2-5 хвилин:
        - Напрямок (UP або DOWN)
        - Впевненість у % (від 70 до 95%)
        - Час входу в форматі HH:MM (за київським часом UTC+2)
        - Тривалість угоди (2 або 5 хвилин)
        - Причина
        
        Поточний київський час: {current_time_str}
        
        Відповідь дай у JSON форматі:
        {{
            "asset": "{asset}",
            "direction": "UP",
            "confidence": 0.85,
            "entry_time": "14:25",
            "duration": 2,
            "reason": "Короткий опис аналізу",
            "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}"
        }}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Ти професійний трейдер бінарних опціонів. Аналізуй технічні індикатори та дай чіткий сигнал."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            response = json.loads(completion.choices[0].message.content)
            return response
            
        except Exception as e:
            logger.error(f"Groq AI error: {e}")
            return None
    
    def _format_candles(self, candles):
        """Форматування свічок для AI"""
        if not candles:
            return "Немає даних"
            
        formatted = []
        for i, candle in enumerate(candles[-10:]):  # Беремо останні 10 свічок
            try:
                # Спроба отримати дані з об'єкта (якщо це об'єкт)
                if hasattr(candle, 'timestamp'):
                    timestamp = candle.timestamp
                    open_price = candle.open
                    high = candle.high
                    low = candle.low
                    close = candle.close
                    volume = getattr(candle, 'volume', 'N/A')
                elif isinstance(candle, (list, tuple)) and len(candle) >= 5:
                    # Якщо це список: [timestamp, open, high, low, close, volume?]
                    timestamp = candle[0]
                    open_price = candle[1]
                    high = candle[2]
                    low = candle[3]
                    close = candle[4]
                    volume = candle[5] if len(candle) > 5 else 'N/A'
                elif isinstance(candle, dict):
                    timestamp = candle.get('timestamp', 'N/A')
                    open_price = candle.get('open', 'N/A')
                    high = candle.get('high', 'N/A')
                    low = candle.get('low', 'N/A')
                    close = candle.get('close', 'N/A')
                    volume = candle.get('volume', 'N/A')
                else:
                    continue
                
                formatted.append(f"""
                Свічка {i+1}:
                Час: {timestamp}
                Open: {open_price}
                High: {high}
                Low: {low}
                Close: {close}
                Volume: {volume}
                """)
            except Exception as e:
                formatted.append(f"Свічка {i+1}: помилка форматування - {e}")
        
        return "\n".join(formatted) if formatted else "Немає коректних даних свічок"
