import json
import logging
import os
from groq import Groq
from datetime import datetime, timedelta
import pytz
from config import Config

logger = logging.getLogger("signal_bot")

class GroqAnalyzer:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            logger.error("❌ GROQ_API_KEY не налаштовано!")
            self.client = None
        else:
            proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
            for var in proxy_vars:
                os.environ.pop(var, None)
            
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info(f"✅ Groq AI ініціалізовано (модель: {Config.GROQ_MODEL})")
    
    def calculate_volatility(self, candles):
        """Розрахунок волатильності"""
        if len(candles) < 10:
            return 0.0
        
        recent_candles = candles[-10:]
        closes = [candle.close for candle in recent_candles]
        
        if not closes:
            return 0.0
        
        max_price = max(closes)
        min_price = min(closes)
        avg_price = sum(closes) / len(closes)
        
        if avg_price == 0:
            return 0.0
        
        volatility = ((max_price - min_price) / avg_price) * 100
        return round(volatility, 4)
    
    def get_technical_indicators(self, candles):
        """Розрахунок технічних індикаторів"""
        if len(candles) < 10:
            return {}
        
        closes = [candle.close for candle in candles]
        
        sma_5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1]
        sma_10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else closes[-1]
        
        trend = "NEUTRAL"
        if sma_5 > sma_10:
            trend = "UP"
        elif sma_5 < sma_10:
            trend = "DOWN"
        
        current_price = closes[-1] if closes else 0
        
        return {
            "sma_5": round(sma_5, 5),
            "sma_10": round(sma_10, 5),
            "trend": trend,
            "current_price": round(current_price, 5)
        }
    
    def analyze_market(self, asset, candles_data, language='uk'):
        """
        Аналіз ринку через GPT OSS 120B AI з підтримкою мов
        """
        if not self.client:
            logger.error("Groq AI не ініціалізовано.")
            return None
        
        if not candles_data or len(candles_data) < 10:
            logger.error(f"Недостатньо даних для {asset}")
            return None
        
        technical_indicators = self.get_technical_indicators(candles_data)
        volatility = self.calculate_volatility(candles_data)
        
        now_kyiv = Config.get_kyiv_time()
        
        # Розрахунок волатильності для тривалості
        volatility = self.calculate_volatility(candles_data)
        
        # Визначення тривалості за волатильністю (2-3 хвилини)
        if volatility > 0.5:
            duration = 2  # Висока волатильність -> 2 хвилини
        elif volatility > 0.2:
            duration = 3  # Середня волатильність -> 3 хвилини
        else:
            duration = 3  # Низька волатильність -> 3 хвилини
        
        # Час входу точно через 2 хвилини
        entry_time_dt = now_kyiv + timedelta(minutes=2)
        entry_time = entry_time_dt.strftime('%H:%M')
        
        candles_str = ""
        for i, candle in enumerate(candles_data[-20:]):
            if hasattr(candle, 'timestamp'):
                time_str = candle.timestamp.strftime('%H:%M')
            else:
                time_str = f"{i+1}"
            
            candles_str += f"{time_str}: O={candle.open:.5f} H={candle.high:.5f} L={candle.low:.5f} C={candle.close:.5f}\n"
        
        if language == 'ru':
            prompt = f"""
Ты экспертный трейдер с 10-летним опытом торговли бинарными опционами.

АКТИВ: {asset}
ТАЙМФРЕЙМ: 1 минута
ТЕКУЩЕЕ ВРЕМЯ (Киев): {now_kyiv.strftime('%H:%M:%S')}

ПРОАНАЛИЗИРУЙ СЛЕДУЮЩИЕ ИНДИКАТОРЫ:
1. RSI (14) - перекупленность/перепроданность
2. MACD - момент и тренд
3. Bollinger Bands %B - волатильность
4. EMA 9/21 - кроссовер
5. Stochastic - перекупленность/перепроданность
6. Тренд последних 5 свечей
7. Паттерны свечей (поглощение, молот, доджи и т.д.)

ДАННЫЕ ПОСЛЕДНИХ 20 СВЕЧЕЙ (1 минута):
{candles_str}

ВАЖНЫЕ ПРАВИЛА АНАЛИЗА:
1. Сигнал должен быть четким с минимальной уверенностью 75%
2. Если тренд неясен (флет) - НЕ давай сигнал
3. Анализируй все 7 указанных индикаторов комплексно
4. Чекни свечные паттерны на разворотах/продолжении
5. Учти уровни поддержки/сопротивления

ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ:
- Волатильность: {volatility:.4f}%
- Время экспирации: {duration} мин (рассчитано по волатильности)
- Время входа: точно через 2 минуты ({entry_time})

ДАЙ ПРОГНОЗ НА {duration} МИНУТ ВПЕРЕД:

ОТВЕТ В СТРОГОМ JSON ФОРМАТЕ:
{{
    "asset": "{asset}",
    "direction": "UP или DOWN",
    "confidence": 0.85 (от 0.75 до 0.95),
    "entry_time": "{entry_time}",
    "duration": {duration},
    "technical_analysis": {{
        "rsi_analysis": "анализ RSI",
        "macd_analysis": "анализ MACD", 
        "bb_analysis": "анализ Bollinger Bands",
        "ema_cross": "анализ EMA 9/21",
        "stochastic_analysis": "анализ Stochastic",
        "candle_trend": "тренд 5 свечей",
        "candle_patterns": "обнаруженные паттерны"
    }},
    "reason": "Краткое обоснование сигнала на русском",
    "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}"
}}
"""
        else:
            prompt = f"""
Ти експертний трейдер з бінарними опціонами з 10-річним досвідом.

АКТИВ: {asset}
ТАЙМФРЕЙМ: 1 хвилина
ПОТОЧНИЙ ЧАС (Київ): {now_kyiv.strftime('%H:%M:%S')}

ПРОАНАЛІЗУЙ НАСТУПНІ ІНДИКАТОРИ:
1. RSI (14) - перекупленість/перепроданість
2. MACD - моментум та тренд
3. Bollinger Bands %B - волатильність
4. EMA 9/21 - кросовер
5. Stochastic - перекупленість/перепроданість
6. Тренд останніх 5 свічок
7. Патерни свічок (поглинання, молот, доджі тощо)

ДАНІ ОСТАННІХ 20 СВІЧОК (1 хвилина):
{candles_str}

ВАЖЛИВІ ПРАВИЛА АНАЛІЗУ:
1. Сигнал має бути чітким з мінімальною впевненістю 75%
2. Якщо тренд неясний (флет) - НЕ давай сигнал
3. Аналізуй всі 7 вказаних індикаторів комплексно
4. Перевір свічкові патерни на розворотах/продовженні
5. Врахуй рівні підтримки/опору

ТЕХНІЧНІ ПАРАМЕТРИ:
- Волатильність: {volatility:.4f}%
- Час експірації: {duration} хв (розраховано за волатильністю)
- Час входу: точно через 2 хвилини ({entry_time})

ДАЙ ПРОГНОЗ НА {duration} ХВИЛИН ВПЕРЕД:

ВІДПОВІДЬ У СУВОРОМУ JSON ФОРМАТІ:
{{
    "asset": "{asset}",
    "direction": "UP або DOWN",
    "confidence": 0.85 (від 0.75 до 0.95),
    "entry_time": "{entry_time}",
    "duration": {duration},
    "technical_analysis": {{
        "rsi_analysis": "аналіз RSI",
        "macd_analysis": "аналіз MACD",
        "bb_analysis": "аналіз Bollinger Bands", 
        "ema_cross": "аналіз EMA 9/21",
        "stochastic_analysis": "аналіз Stochastic",
        "candle_trend": "тренд 5 свічок",
        "candle_patterns": "виявлені патерни"
    }},
    "reason": "Коротке обґрунтування сигналу українською",
    "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}"
}}
"""
        
        try:
            logger.info(f"🧠 Аналіз через {Config.GROQ_MODEL} для {asset}...")
            
            completion = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "Ти професійний трейдер бінарних опціонів. Використовуй технічний аналіз. Відповідай ТІЛЬКИ у JSON форматі."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            logger.debug(f"AI відповідь: {response_text[:200]}...")
            
            response = json.loads(response_text)
            
            required_fields = ['asset', 'direction', 'confidence', 'entry_time', 'duration']
            for field in required_fields:
                if field not in response:
                    logger.error(f"⚠️ Відповідь AI не містить поле {field}")
                    return None
            
            response['generated_at'] = now_kyiv.isoformat()
            response['volatility'] = volatility
            response['id'] = f"{asset}_{now_kyiv.strftime('%Y%m%d%H%M%S')}"
            
            confidence = response.get('confidence', 0)
            if confidence < Config.MIN_CONFIDENCE:
                logger.warning(f"⚠️ Сигнал для {asset} має низьку впевненість: {confidence*100:.1f}% < {Config.MIN_CONFIDENCE*100}%")
                return None
            
            duration_value = response.get('duration', duration)
            if duration_value > Config.MAX_DURATION:
                response['duration'] = Config.MAX_DURATION
                logger.warning(f"⚠️ Обмежено тривалість для {asset}: {duration_value} → {Config.MAX_DURATION}")
            
            logger.info(f"✅ AI повернув сигнал для {asset}: {response['direction']} ({confidence*100:.1f}%)")
            return response
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Не вдалося розпарсити JSON від AI: {e}")
            logger.error(f"Текст відповіді: {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"❌ Groq AI error: {e}")
            
            try:
                logger.info("🔄 Створення простого сигналу через резервний метод...")
                return self._create_simple_signal(asset, technical_indicators, volatility, entry_time, duration, now_kyiv, language)
            except Exception as e2:
                logger.error(f"❌ Резервний метод теж не працює: {e2}")
                return None
    
    def _create_simple_signal(self, asset, indicators, volatility, entry_time, duration, now_kyiv, language='uk'):
        """Резервний метод створення простого сигналу"""
        trend = indicators.get('trend', 'NEUTRAL')
        sma_5 = indicators.get('sma_5', 0)
        sma_10 = indicators.get('sma_10', 0)
        
        if trend == "UP":
            direction = "UP"
            confidence = 0.75
            if language == 'ru':
                reason = f"Тренд вверх. SMA5 ({sma_5:.5f}) > SMA10 ({sma_10:.5f}). Волатильность: {volatility:.2f}%"
            else:
                reason = f"Тренд вгору. SMA5 ({sma_5:.5f}) > SMA10 ({sma_10:.5f}). Волатильність: {volatility:.2f}%"
        elif trend == "DOWN":
            direction = "DOWN"
            confidence = 0.75
            if language == 'ru':
                reason = f"Тренд вниз. SMA5 ({sma_5:.5f}) < SMA10 ({sma_10:.5f}). Волатильность: {volatility:.2f}%"
            else:
                reason = f"Тренд вниз. SMA5 ({sma_5:.5f}) < SMA10 ({sma_10:.5f}). Волатильність: {volatility:.2f}%"
        else:
            return None
        
        if volatility > 0.5:
            duration = 2
        elif volatility > 0.2:
            duration = 3
        else:
            duration = 3
        
        return {
            "asset": asset,
            "direction": direction,
            "confidence": confidence,
            "entry_time": entry_time,
            "duration": duration,
            "reason": reason,
            "timestamp": now_kyiv.strftime('%Y-%m-%d %H:%M:%S'),
            "generated_at": now_kyiv.isoformat(),
            "volatility": volatility,
            "id": f"{asset}_{now_kyiv.strftime('%Y%m%d%H%M%S')}"
        }
