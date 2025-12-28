import json
import logging
from groq import Groq
from datetime import datetime, timedelta
import pytz
from config import Config

logger = logging.getLogger("signal_bot")

class GroqAnalyzer:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            logger.error("❌ GROQ_API_KEY не налаштовано")
            self.client = None
        else:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info(f"✅ Groq AI ініціалізовано (модель: {Config.GROQ_MODEL})")
    
    def analyze_market(self, asset, candles_data):
        """Аналіз ринку через Groq AI"""
        if not self.client:
            return None
        
        candles_str = self._format_candles(candles_data)
        kyiv_tz = pytz.timezone(Config.TIMEZONE)
        now_kyiv = datetime.now(kyiv_tz)
        
        prompt = f"""
        АКТИВ: {asset}
        ЧАС АНАЛІЗУ: {now_kyiv.strftime('%H:%M %d.%m.%Y')} (Київ, UTC+2)
        
        ОСТАННІ 10 СВІЧОК (2-хвилинні):
        {candles_str}
        
        ТВОЄ ЗАВДАННЯ:
        1. Проаналізуй технічні індикатори (тренд, RSI, MACD, підтримка/опір)
        2. Визнач напрямок на наступні 2-5 хвилин
        3. Вкажи точний час входу (київський час)
        4. Вкажи тривалість угоди (2 або 5 хвилин)
        
        ВИМОГИ:
        - Напрямок: тільки UP або DOWN
        - Впевненість: 70-95%
        - Час входу: формат HH:MM (наступні 2-5 хвилин)
        - Тривалість: 2 або 5
        
        ВІДПОВІДЬ У JSON:
        {{
            "asset": "{asset}",
            "direction": "UP",
            "confidence": 0.85,
            "entry_time": "14:25",
            "duration": 2,
            "reason": "Коротка причина",
            "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}"
        }}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Ти професійний трейдер бінарних опціонів. Даєш чіткі сигнали з точним часом."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            response = json.loads(completion.choices[0].message.content)
            
            # Валідація відповіді
            if all(key in response for key in ['direction', 'confidence', 'entry_time', 'duration']):
                return response
            else:
                logger.error("❌ AI повернув неповну відповідь")
                return None
                
        except Exception as e:
            logger.error(f"❌ Помилка AI: {str(e)}")
            return None
    
    def _format_candles(self, candles):
        """Форматування свічок"""
        if not candles:
            return "Немає даних"
        
        formatted = []
        for i, candle in enumerate(candles[-10:]):
            if hasattr(candle, 'close'):
                # Об'єкт
                formatted.append(f"[{i+1}] O:{candle.open:.5f} H:{candle.high:.5f} L:{candle.low:.5f} C:{candle.close:.5f}")
            elif isinstance(candle, (list, tuple)) and len(candle) >= 5:
                # Список
                formatted.append(f"[{i+1}] O:{candle[1]:.5f} H:{candle[2]:.5f} L:{candle[3]:.5f} C:{candle[4]:.5f}")
        
        return "\n".join(formatted)
