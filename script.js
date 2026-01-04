class SignalDisplay {
    constructor() {
        this.signalsUrl = 'data/signals.json';
        this.historyUrl = 'data/history.json';
        this.feedbackUrl = 'data/feedback.json';
        this.kyivTZ = 'Europe/Kiev';
        this.language = localStorage.getItem('language') || 'uk';
        this.activeTimers = new Map();
        this.signalTimers = new Map();
        this.updateInterval = null;
        this.autoUpdateTimer = null;
        this.nextUpdateTime = null;
        
        this.translations = {
            uk: {
                title: "AI Trading Signals",
                subtitle: "Автоматичні сигнали для бінарних опціонів з використанням GPT OSS 120B AI",
                autoUpdate: "Оновлення:",
                every5min: "кожні 5 хв",
                minAccuracy: "Мін. точність:",
                model: "Модель:",
                entryDelay: "Вхід через:",
                nextUpdate: "Наступне оновлення:",
                lastUpdate: "Останнє оновлення",
                kievTime: "(Київський час)",
                activeSignals: "Активних сигналів",
                withConfidence: "з впевненістю >70%",
                totalSignals: "Всього сигналів",
                today: "сьогодні",
                successRate: "Точність AI",
                learning: "навчання активне",
                systemActive: "Система активна!",
                autoDescription: "Сигнали генеруються автоматично кожні 5 хвилин. AI аналізує ринок та вказує час входу через 1-2 хвилини для точнішого прогнозу.",
                currentSignals: "Актуальні сигнали",
                serverTime: "Київський час:",
                loadingSignals: "Завантаження сигналів...",
                firstLoad: "Перше оновлення через",
                noSignalsNow: "Наразі немає актуальних сигналів",
                nextAutoUpdate: "Наступне автоматичне оновлення через",
                howItWorks: "Як працює система",
                autoGeneration: "Автоматична генерація:",
                autoGenDesc: "кожні 5 хвилин",
                entryDelay2: "Затримка входу:",
                entryDelayDesc: "1-2 хвилини для точнішого прогнозу",
                aiLearning: "Навчання AI:",
                aiLearningDesc: "аналізує успішність сигналів",
                autoCleanup: "Автоочищення:",
                autoCleanupDesc: "сигнали зникають через 5 хвилин",
                tokenLimits: "Ліміти використання",
                tokenLimitsDesc: "Для економії токенів AI обмежено до 3 сигналів за раз. Система розрахована на тривалу роботу.",
                createdWith: "Створено з використанням",
                technologies: "Технології:",
                feedbackQuestion: "Сигнал був вірний?",
                feedbackYes: "Так, вірний",
                feedbackNo: "Ні, не вірний",
                feedbackSkip: "Пропустити",
                feedbackNote: "Ваша відповідь допомагає AI вчитися та покращувати точність",
                timeLeft: "Залишилось:",
                signalExpires: "Сигнал зникне через:",
                signalActive: "Сигнал активний",
                signalCompleted: "Сигнал завершено",
                entryTime: "Вхід о:",
                minutesShort: "хв",
                secondsShort: "сек",
                expiresIn: "Зникає через",
                analyzingMarket: "AI аналізує ринок...",
                signalGenerated: "Сигнал згенеровано",
                updateIn: "Оновлення через:",
                systemStatus: "Статус системи:",
                statusActive: "Активна",
                statusWaiting: "Очікування"
            },
            ru: {
                title: "AI Торговые Сигналы",
                subtitle: "Автоматические сигналы для бинарных опционов с использованием GPT OSS 120B AI",
                autoUpdate: "Обновление:",
                every5min: "каждые 5 мин",
                minAccuracy: "Мин. точность:",
                model: "Модель:",
                entryDelay: "Вход через:",
                nextUpdate: "Следующее обновление:",
                lastUpdate: "Последнее обновление",
                kievTime: "(Киевское время)",
                activeSignals: "Активных сигналов",
                withConfidence: "с уверенностью >70%",
                totalSignals: "Всего сигналов",
                today: "сегодня",
                successRate: "Точность AI",
                learning: "обучение активно",
                systemActive: "Система активна!",
                autoDescription: "Сигналы генерируются автоматически каждые 5 минут. AI анализирует рынок и указывает время входа через 1-2 минуты для более точного прогноза.",
                currentSignals: "Актуальные сигналы",
                serverTime: "Киевское время:",
                loadingSignals: "Загрузка сигналов...",
                firstLoad: "Первое обновление через",
                noSignalsNow: "В настоящее время нет актуальных сигналов",
                nextAutoUpdate: "Следующее автоматическое обновление через",
                howItWorks: "Как работает система",
                autoGeneration: "Автоматическая генерация:",
                autoGenDesc: "каждые 5 минут",
                entryDelay2: "Задержка входа:",
                entryDelayDesc: "1-2 минуты для более точного прогноза",
                aiLearning: "Обучение AI:",
                aiLearningDesc: "анализирует успешность сигналов",
                autoCleanup: "Автоочистка:",
                autoCleanupDesc: "сигналы исчезают через 5 минут",
                tokenLimits: "Лимиты использования",
                tokenLimitsDesc: "Для экономии токенов AI ограничено до 3 сигналов за раз. Система рассчитана на длительную работу.",
                createdWith: "Создано с использованием",
                technologies: "Технологии:",
                feedbackQuestion: "Сигнал был верным?",
                feedbackYes: "Да, верный",
                feedbackNo: "Нет, не верный",
                feedbackSkip: "Пропустить",
                feedbackNote: "Ваш ответ помогает AI учиться и улучшать точность",
                timeLeft: "Осталось:",
                signalExpires: "Сигнал исчезнет через:",
                signalActive: "Сигнал активен",
                signalCompleted: "Сигнал завершен",
                entryTime: "Вход в:",
                minutesShort: "мин",
                secondsShort: "сек",
                expiresIn: "Исчезает через",
                analyzingMarket: "AI анализирует рынок...",
                signalGenerated: "Сигнал сгенерирован",
                updateIn: "Обновление через:",
                systemStatus: "Статус системы:",
                statusActive: "Активна",
                statusWaiting: "Ожидание"
            }
        };
        
        this.init();
    }

    async init() {
        await this.setupLanguage();
        this.setupEventListeners();
        this.updateKyivTime();
        setInterval(() => this.updateKyivTime(), 1000);
        
        // Перше завантаження через 5 секунд
        setTimeout(() => {
            this.loadSignals();
            this.startAutoUpdate();
        }, 5000);
        
        this.startSignalCleanupCheck();
    }

    setupEventListeners() {
        document.getElementById('lang-uk').addEventListener('click', () => {
            this.switchLanguage('uk');
        });
        
        document.getElementById('lang-ru').addEventListener('click', () => {
            this.switchLanguage('ru');
        });
    }

    startAutoUpdate() {
        // Автоматичне оновлення кожні 5 хвилин (300 секунд)
        this.updateInterval = setInterval(() => {
            this.loadSignals();
        }, 300000); // 5 хвилин
        
        // Оновлюємо таймер наступного оновлення
        this.updateNextUpdateTimer();
        setInterval(() => this.updateNextUpdateTimer(), 1000);
    }

    updateNextUpdateTimer() {
        if (!this.nextUpdateTime) {
            this.nextUpdateTime = Date.now() + 300000; // 5 хвилин
        }
        
        const now = Date.now();
        const timeLeft = this.nextUpdateTime - now;
        
        if (timeLeft <= 0) {
            this.nextUpdateTime = now + 300000;
            return;
        }
        
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);
        
        document.getElementById('next-update-timer').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
        document.getElementById('next-auto-timer').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    async loadSignals() {
        try {
            const timestamp = new Date().getTime();
            const response = await fetch(`${this.signalsUrl}?t=${timestamp}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.processSignals(data);
            
            // Оновлюємо час наступного оновлення
            this.nextUpdateTime = Date.now() + 300000;
        } catch (error) {
            console.error('Помилка завантаження сигналів:', error);
        }
    }

    processSignals(data) {
        const container = document.getElementById('signals-container');
        const noSignals = document.getElementById('no-signals');
        const lastUpdate = document.getElementById('last-update');
        const activeSignalsElement = document.getElementById('active-signals');
        const totalSignalsElement = document.getElementById('total-signals');
        const successRateElement = document.getElementById('success-rate');
        
        if (!data || !data.signals || data.signals.length === 0) {
            container.innerHTML = this.getEmptyStateHTML();
            lastUpdate.textContent = '--:--:--';
            activeSignalsElement.textContent = '0';
            totalSignalsElement.textContent = '0';
            successRateElement.textContent = '0%';
            noSignals.style.display = 'block';
            return;
        }
        
        if (data.last_update) {
            const updateDate = new Date(data.last_update);
            lastUpdate.textContent = this.formatTime(updateDate, true);
        }
        
        // Статистика
        activeSignalsElement.textContent = data.active_signals || 0;
        totalSignalsElement.textContent = data.total_signals || data.signals.length;
        
        // Розрахунок успішності (заглушка)
        const successRate = this.calculateSuccessRate(data.signals);
        successRateElement.textContent = `${successRate}%`;
        
        // Відображення сигналів
        let html = '';
        let hasSignals = false;
        
        data.signals.forEach((signal, index) => {
            const confidencePercent = Math.round(signal.confidence * 100);
            if (confidencePercent < 70) return;
            
            const signalHTML = this.createSignalHTML(signal, index);
            if (signalHTML) {
                html += signalHTML;
                hasSignals = true;
            }
        });
        
        if (!hasSignals) {
            container.innerHTML = this.getNoSignalsHTML();
            noSignals.style.display = 'block';
        } else {
            container.innerHTML = html;
            noSignals.style.display = 'none';
            
            // Запускаємо таймери для кожного сигналу
            data.signals.forEach((signal, index) => {
                this.setupSignalTimer(signal, index);
            });
        }
    }

    createSignalHTML(signal, index) {
        const confidencePercent = Math.round(signal.confidence * 100);
        const confidenceClass = this.getConfidenceClass(confidencePercent);
        const directionClass = signal.direction.toLowerCase();
        const duration = signal.duration || 2;
        
        // Час генерації
        const generatedTime = signal.generated_at ? 
            this.convertToKyivTime(signal.generated_at) : '--:--';
        
        // Час входу (через 1-2 хвилини)
        const entryTime = signal.entry_time || '--:--';
        
        // Причина від AI
        let reason = signal.reason || '';
        if (this.language === 'ru' && signal.reason_ru) {
            reason = signal.reason_ru;
        }
        
        return `
            <div class="signal-card ${directionClass}" id="signal-${index}" 
                 data-generated="${signal.generated_at}" 
                 data-asset="${signal.asset}">
                <div class="signal-header">
                    <div class="asset-info">
                        <div class="asset-icon">
                            <i class="fas fa-${directionClass === 'up' ? 'chart-line' : 'chart-line'}"></i>
                        </div>
                        <div>
                            <div class="asset-name">${signal.asset.replace('_otc', '').replace('/', ' ')}</div>
                            <small>${this.translate('entryTime')} ${entryTime} | ${duration} ${this.translate('minutesShort')}</small>
                        </div>
                    </div>
                    <div class="direction-badge">
                        ${signal.direction === 'UP' ? '📈 CALL' : '📉 PUT'}
                        <span class="confidence-badge ${confidenceClass}">${confidencePercent}%</span>
                    </div>
                </div>
                
                <div class="signal-details">
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-brain"></i> ${this.translate('model')}
                        </div>
                        <div class="value">GPT OSS 120B</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-clock"></i> ${this.translate('entryTime')}
                        </div>
                        <div class="value">${entryTime} <small>(Київ)</small></div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-hourglass-half"></i> ${this.translate('timeLeft')}
                        </div>
                        <div class="value" id="timer-${index}">
                            <div class="loading-timer">${this.translate('analyzingMarket')}</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-calendar"></i> ${this.translate('lastUpdate')}
                        </div>
                        <div class="value">${generatedTime}</div>
                    </div>
                </div>
                
                ${reason ? `
                <div class="signal-reason">
                    <div class="reason-header">
                        <i class="fas fa-lightbulb"></i> ${this.translate('analyzingMarket')}
                    </div>
                    <div class="reason-text">${reason}</div>
                </div>
                ` : ''}
                
                <div class="signal-footer">
                    <div class="expiry-timer" id="expiry-${index}">
                        <i class="fas fa-hourglass-end"></i> 
                        ${this.translate('expiresIn')}: <span class="expiry-time">5:00</span>
                    </div>
                    <button class="feedback-trigger" onclick="signalDisplay.showFeedbackModal('${signal.asset}', '${index}')">
                        <i class="fas fa-check-circle"></i> ${this.translate('feedbackYes')}
                    </button>
                </div>
            </div>
        `;
    }

    setupSignalTimer(signal, index) {
        const timerElement = document.getElementById(`timer-${index}`);
        const expiryElement = document.getElementById(`expiry-${index}`);
        if (!timerElement || !expiryElement) return;
        
        const generatedTime = new Date(signal.generated_at);
        const expiryTime = new Date(generatedTime.getTime() + 5 * 60000); // 5 хвилин
        
        const updateTimer = () => {
            const now = new Date();
            const timeToExpiry = expiryTime - now;
            
            if (timeToExpiry <= 0) {
                // Час вийшов - видаляємо сигнал
                const signalElement = document.getElementById(`signal-${index}`);
                if (signalElement) {
                    signalElement.style.opacity = '0.5';
                    setTimeout(() => {
                        if (signalElement.parentNode) {
                            signalElement.remove();
                            this.updateSignalCount();
                        }
                    }, 1000);
                }
                
                // Очищаємо таймер
                if (this.signalTimers.has(index)) {
                    clearInterval(this.signalTimers.get(index));
                    this.signalTimers.delete(index);
                }
                return;
            }
            
            // Оновлюємо таймер
            const minutes = Math.floor(timeToExpiry / 60000);
            const seconds = Math.floor((timeToExpiry % 60000) / 1000);
            
            expiryElement.querySelector('.expiry-time').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Оновлюємо статус сигналу
            const entryTime = signal.entry_time;
            if (entryTime) {
                const [hours, mins] = entryTime.split(':').map(Number);
                const entryDate = new Date(generatedTime);
                entryDate.setHours(hours, mins, 0, 0);
                
                const timeToEntry = entryDate - now;
                if (timeToEntry > 0) {
                    const entryMinutes = Math.floor(timeToEntry / 60000);
                    const entrySeconds = Math.floor((timeToEntry % 60000) / 1000);
                    timerElement.innerHTML = `
                        <div class="timer-display">
                            <i class="fas fa-clock"></i>
                            <span class="timer-text">${entryMinutes}:${entrySeconds.toString().padStart(2, '0')}</span>
                        </div>
                        <small>${this.translate('signalActive')}</small>
                    `;
                } else {
                    timerElement.innerHTML = `
                        <div class="timer-display">
                            <i class="fas fa-check-circle"></i>
                            <span class="timer-text">${this.translate('signalCompleted')}</span>
                        </div>
                        <small>${this.translate('signalExpires')} ${minutes}:${seconds.toString().padStart(2, '0')}</small>
                    `;
                }
            }
        };
        
        // Запускаємо таймер
        updateTimer();
        const timerInterval = setInterval(updateTimer, 1000);
        this.signalTimers.set(index, timerInterval);
        
        // Запускаємо таймер зникнення
        setTimeout(() => {
            const signalElement = document.getElementById(`signal-${index}`);
            if (signalElement) {
                signalElement.remove();
                this.updateSignalCount();
            }
        }, 5 * 60000); // 5 хвилин
    }

    startSignalCleanupCheck() {
        // Перевірка кожну секунду для видалення старих сигналів
        setInterval(() => {
            const now = new Date();
            this.signalTimers.forEach((timer, index) => {
                const signalElement = document.getElementById(`signal-${index}`);
                if (!signalElement) {
                    clearInterval(timer);
                    this.signalTimers.delete(index);
                }
            });
        }, 1000);
    }

    updateSignalCount() {
        const container = document.getElementById('signals-container');
        const activeSignals = container.querySelectorAll('.signal-card').length;
        document.getElementById('active-signals').textContent = activeSignals;
        
        if (activeSignals === 0) {
            document.getElementById('no-signals').style.display = 'block';
        }
    }

    calculateSuccessRate(signals) {
        // Заглушка - в реальності потрібно брати дані з feedback.json
        const totalWithFeedback = signals.filter(s => s.has_feedback).length;
        if (totalWithFeedback === 0) return 0;
        
        const successful = signals.filter(s => s.feedback === 'yes').length;
        return Math.round((successful / totalWithFeedback) * 100);
    }

    showFeedbackModal(asset, index) {
        const modal = document.getElementById('feedback-modal');
        document.getElementById('feedback-asset').textContent = asset;
        modal.style.display = 'flex';
        
        // Зберігаємо індекс для подальшої обробки
        modal.dataset.signalIndex = index;
    }

    async submitFeedback(feedback) {
        const modal = document.getElementById('feedback-modal');
        const index = modal.dataset.signalIndex;
        const asset = document.getElementById('feedback-asset').textContent;
        
        try {
            // Відправляємо feedback на сервер
            const response = await fetch(this.feedbackUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    signal_id: index,
                    asset: asset,
                    feedback: feedback,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                this.showMessage('success', `${this.translate('feedbackYes')}! AI запам'ятає цей результат.`);
                
                // Приховуємо сигнал
                const signalElement = document.getElementById(`signal-${index}`);
                if (signalElement) {
                    signalElement.style.opacity = '0.3';
                    setTimeout(() => {
                        if (signalElement.parentNode) {
                            signalElement.remove();
                            this.updateSignalCount();
                        }
                    }, 500);
                }
            }
        } catch (error) {
            console.error('Помилка відправки feedback:', error);
            this.showMessage('error', 'Помилка відправки. Спробуйте ще раз.');
        }
        
        modal.style.display = 'none';
    }

    updateKyivTime() {
        const now = new Date();
        const timeElement = document.getElementById('server-time');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('uk-UA', {
                timeZone: this.kyivTZ,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    formatTime(date, includeSeconds = false) {
        return date.toLocaleTimeString('uk-UA', {
            timeZone: this.kyivTZ,
            hour: '2-digit',
            minute: '2-digit',
            second: includeSeconds ? '2-digit' : undefined
        });
    }

    convertToKyivTime(dateString) {
        if (!dateString) return '--:--';
        try {
            const date = new Date(dateString);
            return date.toLocaleTimeString('uk-UA', {
                timeZone: this.kyivTZ,
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return '--:--';
        }
    }

    getConfidenceClass(percent) {
        if (percent >= 85) return 'confidence-high';
        if (percent >= 75) return 'confidence-medium';
        return 'confidence-low';
    }

    getEmptyStateHTML() {
        return `
            <div class="loading-state">
                <div class="spinner">
                    <i class="fas fa-robot"></i>
                </div>
                <p>${this.translate('loadingSignals')}</p>
                <small>${this.translate('firstLoad')}</small>
            </div>
        `;
    }

    getNoSignalsHTML() {
        return `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <h3>${this.translate('noSignalsNow')}</h3>
                <p>${this.translate('nextAutoUpdate')} <span id="next-auto-timer">5:00</span></p>
            </div>
        `;
    }

    showMessage(type, text) {
        const messageContainer = document.getElementById('message-container') || 
            this.createMessageContainer();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${text}</span>
        `;
        
        messageContainer.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => messageDiv.remove(), 300);
        }, 5000);
    }

    createMessageContainer() {
        const container = document.createElement('div');
        container.id = 'message-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    async setupLanguage() {
        this.applyLanguage(this.language);
        
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === this.language);
        });
        
        // Додаємо обробники для feedback кнопок
        document.querySelectorAll('.feedback-yes').forEach(btn => {
            btn.addEventListener('click', () => this.submitFeedback('yes'));
        });
        document.querySelectorAll('.feedback-no').forEach(btn => {
            btn.addEventListener('click', () => this.submitFeedback('no'));
        });
        document.querySelectorAll('.feedback-skip').forEach(btn => {
            btn.addEventListener('click', () => this.submitFeedback('skip'));
        });
    }

    switchLanguage(lang) {
        this.language = lang;
        localStorage.setItem('language', lang);
        this.applyLanguage(lang);
        
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        
        this.loadSignals();
    }

    applyLanguage(lang) {
        const translations = this.translations[lang];
        if (!translations) return;
        
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[key];
                } else {
                    element.textContent = translations[key];
                }
            }
        });
    }

    translate(key) {
        return this.translations[this.language][key] || key;
    }
}

// Додаємо стилі для анімацій
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .message {
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .message.success {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
    }
    
    .message.error {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
    }
    
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1001;
    }
    
    .modal-content {
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 400px;
        width: 90%;
        text-align: center;
    }
`;
document.head.appendChild(style);

// Ініціалізація
let signalDisplay;

document.addEventListener('DOMContentLoaded', () => {
    signalDisplay = new SignalDisplay();
    window.signalDisplay = signalDisplay;
    
    // Глобальні функції для feedback
    window.showFeedbackModal = (asset, index) => signalDisplay.showFeedbackModal(asset, index);
    window.submitFeedback = (feedback) => signalDisplay.submitFeedback(feedback);
});
