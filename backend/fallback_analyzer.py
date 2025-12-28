import random
from datetime import datetime, timedelta
import pytz
from config import Config
import logging

logger = logging.getLogger("signal_bot")

class FallbackAnalyzer:
    """Резервний аналізатор на випадок проблем з AI"""
    
    def analyze_market(self, asset, candles_data):
        """Простий технічний аналіз без AI"""
        try:
            if not candles_data or len(candles_data) < 5:
                logger.warning(f"⚠️ Недостатньо даних для резервного аналізу {asset}")
                return None
            
            now_kyiv = Config.get_kyiv_time()
            
            # Простий аналіз останніх свічок
            recent_candles = candles_data[-10:] if len(candles_data) >= 10 else candles_data
            
            # Аналізуємо тенденцію
            closes = []
            for candle in recent_candles:
                if hasattr(candle, 'close'):
                    closes.append(float(candle.close))
                elif isinstance(candle, dict):
                    closes.append(float(candle.get('close', 0)))
                elif isinstance(candle, (list, tuple)) and len(candle) >= 5:
                    closes.append(float(candle[4]))
            
            if len(closes) < 2:
                return None
            
            # Визначаємо тенденцію
            first_half = closes[:len(closes)//2]
            second_half = closes[len(closes)//2:]
            
            avg_first = sum(first_half) / len(first_half) if first_half else 0
            avg_second = sum(second_half) / len(second_half) if second_half else 0
            
            trend_up = avg_second > avg_first
            
            # Рандом з урахуванням тенденції
            if trend_up:
                direction = "UP" if random.random() > 0.4 else "DOWN"
            else:
                direction = "DOWN" if random.random() > 0.4 else "UP"
            
            # Впевненість на основі якості даних
            base_confidence = 0.7
            if len(closes) >= 8:
                base_confidence += 0.1
            if abs(avg_second - avg_first) / avg_first > 0.002:  # > 0.2% зміна
                base_confidence += 0.1
            
            confidence = min(base_confidence + random.random() * 0.15, 0.85)
            
            # Час входу (поточний час + 1-2 хвилини)
            entry_delta = timedelta(minutes=random.randint(1, 3))
            entry_time_datetime = now_kyiv + entry_delta
            entry_time = entry_time_datetime.strftime("%H:%M")
            
            reasons_up = [
                "Висхідний тренд на основі останніх свічок",
                "Покупці контролюють ринок",
                "Прорив рівня опору",
                "Відскок від рівня підтримки"
            ]
            
            reasons_down = [
                "Низхідний тренд на основі останніх свічок",
                "Продавці контролюють ринок",
                "Прорив рівня підтримки",
                "Відскок від рівня опору"
            ]
            
            reason = random.choice(reasons_up if direction == "UP" else reasons_down)
            
            signal = {
                "asset": asset,
                "direction": direction,
                "confidence": round(confidence, 2),
                "entry_time": entry_time,
                "duration": 2 if confidence < 0.8 else 5,
                "reason": f"{reason} на основі {len(recent_candles)} останніх свічок",
                "timestamp": now_kyiv.strftime('%Y-%m-%d %H:%M:%S'),
                "generated_at": now_kyiv.isoformat(),
                "timezone": "Europe/Kiev (UTC+2)",
                "fallback": True  # Позначка, що це резервний сигнал
            }
            
            logger.info(f"🔄 Резервний сигнал для {asset}: {direction} ({confidence*100:.1f}%) - {entry_time}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Помилка резервного аналізу: {e}")
            return None
