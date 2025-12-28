import json
import logging
from groq import Groq
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
            
            # Створюємо клієнта БЕЗ зайвих параметрів
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info(f"✅ Groq AI ініціалізовано (модель: {Config.GROQ_MODEL})")
            
            # Додаємо тест запиту для перевірки підключення
            try:
                test_response = self.client.chat.completions.create(
                    model=Config.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "Тест підключення"},
                        {"role": "user", "content": "Привіт"}
                    ],
                    max_tokens=10
                )
                logger.info("✅ Успішне підключення до Groq AI")
            except Exception as test_error:
                logger.warning(f"⚠️ Проблема з підключенням до Groq: {test_error}")
                
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації Groq: {e}")
            logger.error("Попробуйте перевірити API ключ або мережеве підключення")
    
    def analyze_market(self, asset, candles_data):
        """Аналіз ринку через Groq AI"""
        if not self.client:
            logger.error("Groq AI не ініціалізовано")
            return None
        
        # Форматуємо дані
        candles_str = self._format_candles_for_analysis(candles_data)
        
        # Поточний час Київ
        now_kyiv = Config.get_kyiv_time()
        
        prompt = f"""
        Ти - професійний трейдер бінарних опціонів з 10-річним досвідом.
        
        ЗАВДАННЯ: Проаналізуй наступні дані та дай торговий сигнал.
        
        АКТИВ: {asset}
        ТАЙМФРЕЙМ: 2 хвилини (120 секунд)
        ПОТОЧНИЙ ЧАС (Київ UTC+2): {now_kyiv.strftime('%H:%M')}
        ДАТА (Київ): {now_kyiv.strftime('%Y-%m-%d')}
        
        ОСТАННІ 20 СВІЧОК (формат: Час | Open | High | Low | Close):
        {candles_str}
        
        ПРОАНАЛІЗУЙ:
        1. ТРЕНД: Визнач загальний тренд (вгору/вниз/флет)
        2. КЛЮЧОВІ РІВНІ: Знайди рівні підтримки та опору
        3. ТЕХНІЧНІ ІНДИКАТОРИ: RSI, MACD, Stochastic
        4. ПАТЕРНИ: Шукай японські свічкові паттерни
        5. ВОЛАТИЛЬНІСТЬ: Оціни амплітуду коливань
        
        ДАЙ СИГНАЛ:
        - Напрямок: ТОЛЬКИ "UP" або "DOWN"
        - Впевненість: від 70 до 95% (десятичний дріб)
        - Час входу: поточний час + 1-2 хвилини (формат HH:MM) ВИКОРИСТОВУЙ КИЇВСЬКИЙ ЧАС
        - Тривалість: 2 або 5 хвилин
        - Причина: коротке обґрунтування
        
        ВАЖЛИВО:
        - Якщо тренд неясний - не давай сигнал
        - Мінімальна впевненість: 70%
        - Використовуй ТІЛЬКИ київський час (UTC+2)
        
        ФОРМАТ ВІДПОВІДІ (JSON):
        {{
            "asset": "{asset}",
            "direction": "UP",
            "confidence": 0.85,
            "entry_time": "{now_kyiv.strftime('%H:%M')}",
            "duration": 2,
            "reason": "Чіткий паттерн поглинання на рівні підтримки. RSI показує перепроданість з розворотом вгору.",
            "timestamp": "{now_kyiv.strftime('%Y-%m-%d %H:%M:%S')}",
            "timezone": "Europe/Kiev (UTC+2)"
        }}
        """
        
        try:
            logger.info(f"🧠 Аналізую {asset} через Groq AI...")
            
            completion = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Ти експертний трейдер бінарних опціонів. Даєш тільки чіткі, обґрунтовані сигнали. Використовуй київський час (UTC+2)."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            response = json.loads(completion.choices[0].message.content)
            
            # Додаємо asset, якщо його немає
            if 'asset' not in response:
                response['asset'] = asset
            
            # Додаємо часовий пояс
            response['timezone'] = 'Europe/Kiev (UTC+2)'
            
            # Перевіряємо впевненість
            confidence = response.get('confidence', 0)
            if confidence >= Config.MIN_CONFIDENCE:
                logger.info(f"✅ Отримано сигнал для {asset}: {response['direction']} ({confidence*100:.1f}%)")
                return response
            else:
                logger.warning(f"⚠️ Сигнал для {asset} має низьку впевненість: {confidence*100:.1f}%")
                return None
            
        except Exception as e:
            logger.error(f"❌ Помилка Groq AI для {asset}: {e}")
            return None
    
    def _format_candles_for_analysis(self, candles):
        """Форматування свічок для аналізу"""
        if not candles:
            return "Немає даних"
        
        formatted = []
        # Беремо останні 20 свічок для аналізу
        for i, candle in enumerate(candles[-20:]):
            try:
                # Обробляємо різні формати свічок
                if hasattr(candle, 'close'):
                    close = candle.close
                    open_price = candle.open
                    high = candle.high
                    low = candle.low
                    timestamp = getattr(candle, 'timestamp', 'N/A')
                elif isinstance(candle, dict):
                    close = candle.get('close', 0)
                    open_price = candle.get('open', 0)
                    high = candle.get('high', 0)
                    low = candle.get('low', 0)
                    timestamp = candle.get('timestamp', 'N/A')
                elif isinstance(candle, (list, tuple)) and len(candle) >= 5:
                    timestamp = candle[0]
                    open_price = candle[1]
                    high = candle[2]
                    low = candle[3]
                    close = candle[4]
                else:
                    continue
                
                # Форматуємо
                formatted.append(
                    f"{i+1:2d}. {timestamp} | "
                    f"O:{float(open_price):.5f} "
                    f"H:{float(high):.5f} "
                    f"L:{float(low):.5f} "
                    f"C:{float(close):.5f}"
                )
            except Exception:
                continue
        
        return "\n".join(formatted) if formatted else "Немає коректних даних свічок"
