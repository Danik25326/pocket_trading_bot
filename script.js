class SignalDisplay {
    constructor() {
        this.signalsUrl = 'data/signals.json';
        this.updateInterval = 30000; // Перевірка кожні 30 секунд
        this.language = localStorage.getItem('language') || 'uk';
        this.activeTimers = new Map();
        this.lastGenerationTime = localStorage.getItem('last_generation_time');
        this.STORAGE_KEY = 'trading_signals_v2'; // Ключ для localStorage
        
        this.translations = {
            uk: {
                title: "AI Trading Signals",
                subtitle: "Автоматичні сигнали для бінарних опціонів з використанням GPT-OSS-120b AI",
                updateEvery: "Оновлення:",
                minAccuracy: "Мін. точність:",
                model: "Модель:",
                lastUpdate: "Останнє оновлення",
                kievTime: "(Київський час)",
                activeSignals: "Активних сигналів",
                withConfidence: "з впевненістю >70%",
                totalStats: "Загальна статистика",
                signalsInHistory: "сигналів в історії",
                successRate: "Успішність",
                historicalAccuracy: "історична точність",
                currentSignals: "Актуальні сигнали",
                serverTime: "Поточний час:",
                loadingSignals: "Завантаження сигналів...",
                autoUpdate: "Сигнали оновлюються автоматично",
                noSignalsNow: "Наразі немає актуальних сигналів",
                waitForUpdate: "Очікуйте наступного оновлення",
                howItWorks: "Як працює система",
                aiAnalysis: "AI Аналіз:",
                aiAnalysisDesc: "GPT-OSS-120b для технічного аналізу",
                realTimeData: "Дані в реальному часі:",
                realTimeDataDesc: "Отримання з PocketOption API",
                filtering: "Фільтрація:",
                filteringDesc: "Тільки сигнали >70% та не старіші 5 хв",
                updates: "Оновлення:",
                updatesDesc: "Кожні 5 хвилин для нових сигналів",
                important: "Важливо!",
                disclaimer: "Торгівля містить високі ризики. Сигнали не є фінансовою рекомендацією.",
                createdWith: "Створено з використанням",
                technologies: "Технології:",
                updateBtn: "Оновити",
                searchBtn: "🔍 Пошук сигналів",
                refreshBtn: "🔄 Оновити",
                timeToEntry: "Час до входу:",
                tradeActive: "Тривалість угоди:",
                timeLeft: "Залишилось:",
                minutes: "хв",
                seconds: "сек",
                tradeCompleted: "Угода завершена",
                giveFeedback: "Оцінити сигнал",
                feedbackQuestion: "Сигнал був вірний?",
                feedbackYes: "✅ Так",
                feedbackNo: "❌ Ні",
                feedbackSkip: "⏭️ Пропустити",
                updateAvailable: "Можна оновити",
                updateCooldown: "Оновлення через:",
                searchInProgress: "🔍 Пошук сигналів...",
                generatingSignals: "Генеруються нові сигнали..."
            },
            ru: {
                title: "AI Торговые Сигналы",
                subtitle: "Автоматические сигналы для бинарных опционов с использованием GPT-OSS-120b AI",
                updateEvery: "Обновление:",
                minAccuracy: "Мин. точность:",
                model: "Модель:",
                lastUpdate: "Последнее обновление",
                kievTime: "(Киевское время)",
                activeSignals: "Активных сигналов",
                withConfidence: "с уверенностью >70%",
                totalStats: "Общая статистика",
                signalsInHistory: "сигналов в истории",
                successRate: "Успешность",
                historicalAccuracy: "историческая точность",
                currentSignals: "Актуальные сигналы",
                serverTime: "Текущее время:",
                loadingSignals: "Загрузка сигналов...",
                autoUpdate: "Сигналы обновляются автоматично",
                noSignalsNow: "В настоящее время нет актуальных сигналов",
                waitForUpdate: "Ожидайте следующего обновления",
                howItWorks: "Как работает система",
                aiAnalysis: "AI Анализ:",
                aiAnalysisDesc: "GPT-OSS-120b для технического анализа",
                realTimeData: "Данные в реальном времени:",
                realTimeDataDesc: "Получение из PocketOption API",
                filtering: "Фильтрация:",
                filteringDesc: "Только сигналы >70% и не старше 5 мин",
                updates: "Обновления:",
                updatesDesc: "Каждые 5 минут для новых сигналов",
                important: "Важно!",
                disclaimer: "Торговля содержит высокие риски. Сигналы не являются финансовой рекомендацией.",
                createdWith: "Создано с использованием",
                technologies: "Технологии:",
                updateBtn: "Обновить",
                searchBtn: "🔍 Поиск сигналов",
                refreshBtn: "🔄 Обновить",
                timeToEntry: "Время до входа:",
                tradeActive: "Длительность сделки:",
                timeLeft: "Осталось:",
                minutes: "мин",
                seconds: "сек",
                tradeCompleted: "Сделка завершена",
                giveFeedback: "Оценить сигнал",
                feedbackQuestion: "Сигнал был верным?",
                feedbackYes: "✅ Да",
                feedbackNo: "❌ Нет",
                feedbackSkip: "⏭️ Пропустить",
                updateAvailable: "Можно обновить",
                updateCooldown: "Обновление через:",
                searchInProgress: "🔍 Поиск сигналов...",
                generatingSignals: "Генерируются новые сигналы..."
            }
        };
        
        this.init();
    }

    async init() {
        await this.setupLanguage();
        await this.loadSignals();
        this.startAutoUpdate();
        this.updateKyivTime();
        setInterval(() => this.updateKyivTime(), 1000);
        this.setupRefreshButton();
        
        // Додаємо обробник для кнопки пошуку
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchSignals();
        });
    }

    async loadSignals(force = false) {
        try {
            // Пытаемся загрузить из localStorage в первую очередь
            const savedSignals = this.getSavedSignals();
            if (savedSignals && savedSignals.signals && savedSignals.signals.length > 0 && !force) {
                console.log('📂 Завантажено сигнали з localStorage');
                this.processSignals(savedSignals, force);
                return;
            }
            
            // Если в localStorage нет, загружаем с сервера
            const timestamp = new Date().getTime();
            const response = await fetch(`${this.signalsUrl}?t=${timestamp}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.processSignals(data, force);
            
            // Сохраняем в localStorage
            this.saveSignalsToStorage(data);
            
        } catch (error) {
            console.error('Помилка завантаження:', error);
            
            // Пробуем загрузить из localStorage как запасной вариант
            const savedSignals = this.getSavedSignals();
            if (savedSignals && savedSignals.signals && savedSignals.signals.length > 0) {
                console.log('⚠️ Використовую сигнали з localStorage (помилка сервера)');
                this.processSignals(savedSignals, force);
            } else {
                this.showError('Не вдалося завантажити сигнали. Спробуйте пізніше.');
            }
        }
    }

    getSavedSignals() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (!saved) return null;
            
            const data = JSON.parse(saved);
            
            // Проверяем актуальность сигналов (не старше 5 минут)
            const now = new Date();
            const fiveMinutesAgo = new Date(now.getTime() - 5 * 60000);
            
            if (data.last_update) {
                const lastUpdate = new Date(data.last_update);
                if (lastUpdate < fiveMinutesAgo) {
                    console.log('⚠️ Сигнали в localStorage застаріли (>5 хв)');
                    return null;
                }
            }
            
            return data;
        } catch (e) {
            console.error('Помилка читання з localStorage:', e);
            return null;
        }
    }

    saveSignalsToStorage(data) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            localStorage.setItem('last_signals_update', new Date().toISOString());
            console.log('💾 Сигнали збережено в localStorage');
        } catch (e) {
            console.error('Помилка збереження в localStorage:', e);
        }
    }

    clearSavedSignals() {
        try {
            localStorage.removeItem(this.STORAGE_KEY);
            localStorage.removeItem('last_signals_update');
            console.log('🧹 Сигнали видалено з localStorage');
        } catch (e) {
            console.error('Помилка очищення localStorage:', e);
        }
    }

    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-btn');
        const lastUpdate = localStorage.getItem('last_generation_time');
        
        if (!lastUpdate) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-redo"></i> ' + this.translate('refreshBtn');
            return;
        }
        
        const now = Date.now();
        const lastUpdateTime = parseInt(lastUpdate);
        const fiveMinutes = 5 * 60 * 1000;
        const timeSinceUpdate = now - lastUpdateTime;
        
        if (timeSinceUpdate < fiveMinutes) {
            refreshBtn.disabled = true;
            this.startRefreshCooldown(refreshBtn, fiveMinutes - timeSinceUpdate);
        } else {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-redo"></i> ' + this.translate('updateAvailable');
            refreshBtn.addEventListener('click', () => this.forceRefresh());
        }
    }

    startRefreshCooldown(button, remainingTime) {
        const updateCooldown = () => {
            remainingTime -= 1000;
            
            if (remainingTime <= 0) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-redo"></i> ' + this.translate('updateAvailable');
                button.addEventListener('click', () => this.forceRefresh());
                return;
            }
            
            const minutes = Math.floor(remainingTime / 60000);
            const seconds = Math.floor((remainingTime % 60000) / 1000);
            button.innerHTML = `<i class="fas fa-clock"></i> ${this.translate('updateCooldown')} ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            setTimeout(updateCooldown, 1000);
        };
        
        updateCooldown();
    }

    async searchSignals() {
        const searchBtn = document.getElementById('search-btn');
        const originalText = searchBtn.innerHTML;
        
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + this.translate('searchInProgress');
        
        try {
            // Запускаємо GitHub Actions workflow
            await this.triggerGitHubWorkflow();
            
            // Очікуємо 30 секунд на генерацію
            await this.wait(30000);
            
            // Оновлюємо сигнали
            await this.loadSignals(true);
            
            // Оновлюємо час останньої генерації
            localStorage.setItem('last_generation_time', Date.now().toString());
            this.setupRefreshButton();
            
        } catch (error) {
            console.error('Помилка пошуку сигналів:', error);
            this.showError('Не вдалося запустити пошук сигналів');
        } finally {
            searchBtn.disabled = false;
            searchBtn.innerHTML = originalText;
        }
    }

    async triggerGitHubWorkflow() {
        // Це потрібно налаштувати з вашим GitHub токеном
        // Заглушка - просто оновлюємо сторінку
        console.log('Запуск генерації сигналів...');
        
        // Спробуємо оновити сторінку через 30 секунд
        setTimeout(() => {
            console.log('Оновлення сторінки для завантаження нових сигналів...');
            window.location.reload();
        }, 30000);
        
        return Promise.resolve();
    }

    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    processSignals(data, force = false) {
        const container = document.getElementById('signals-container');
        const noSignals = document.getElementById('no-signals');
        const lastUpdate = document.getElementById('last-update');
        const activeSignalsElement = document.getElementById('active-signals');
        const totalSignalsElement = document.getElementById('total-signals');
        
        if (!data || !data.signals || data.signals.length === 0) {
            container.innerHTML = '';
            noSignals.style.display = 'block';
            lastUpdate.textContent = '--:--:--';
            activeSignalsElement.textContent = '0';
            totalSignalsElement.textContent = '0';
            return;
        }
        
        noSignals.style.display = 'none';
        
        // Оновлюємо час останнього оновлення
        if (data.last_update) {
            const updateDate = new Date(data.last_update);
            lastUpdate.textContent = this.formatTimeKyiv(updateDate, true);
        }
        
        // Фільтруємо сигнали
        const now = new Date();
        const fiveMinutesAgo = new Date(now.getTime() - 5 * 60000);
        
        let activeSignals = 0;
        let html = '';
        
        data.signals.forEach((signal, index) => {
            const confidencePercent = Math.round(signal.confidence * 100);
            if (confidencePercent < 70) return;
            
            const generatedAt = new Date(signal.generated_at);
            if (generatedAt < fiveMinutesAgo && !force) return;
            
            activeSignals++;
            
            const signalId = `signal-${index}`;
            html += this.createSignalHTML(signal, signalId);
        });
        
        activeSignalsElement.textContent = activeSignals;
        totalSignalsElement.textContent = data.signals.length;
        
        if (activeSignals === 0) {
            noSignals.style.display = 'block';
            container.innerHTML = '';
        } else {
            container.innerHTML = html;
            
            // Запускаємо таймери для всіх сигналів
            data.signals.forEach((signal, index) => {
                const signalId = `signal-${index}`;
                this.setupSignalTimer(signal, signalId);
            });
            
            // Сохраняем в localStorage
            this.saveSignalsToStorage(data);
        }
        
        // Зберігаємо час останньої генерації
        if (data.last_update) {
            localStorage.setItem('last_generation_time', Date.now().toString());
        }
    }

    createSignalHTML(signal, signalId) {
        const confidencePercent = Math.round(signal.confidence * 100);
        const confidenceClass = this.getConfidenceClass(confidencePercent);
        const directionClass = signal.direction.toLowerCase();
        
        // Використовуємо київський час для відображення
        const entryTime = signal.entry_time_kyiv || signal.entry_time || 'Не вказано';
        const duration = signal.duration || '2';
        
        // Конвертуємо час генерації в Київський
        let generatedTime = 'Не вказано';
        if (signal.generated_at) {
            const genDate = new Date(signal.generated_at);
            generatedTime = this.formatTimeKyiv(genDate, false);
        }
        
        return `
            <div class="signal-card ${directionClass}" id="${signalId}" data-asset="${signal.asset}">
                <div class="signal-header">
                    <div class="asset-info">
                        <div class="asset-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div>
                            <div class="asset-name">${signal.asset}</div>
                            <small>Тривалість: ${duration} хв | Київський час</small>
                        </div>
                    </div>
                    <div class="direction-badge">
                        ${signal.direction === 'UP' ? '📈 CALL' : '📉 PUT'}
                    </div>
                </div>
                
                <div class="signal-details">
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-bullseye"></i> Впевненість
                        </div>
                        <div class="value">
                            ${confidencePercent}%
                            <span class="confidence-badge ${confidenceClass}">
                                ${confidencePercent >= 80 ? 'Висока' : confidencePercent >= 70 ? 'Середня' : 'Низька'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="far fa-clock"></i> Час входу
                        </div>
                        <div class="value">
                            ${entryTime}
                            <small style="display: block; font-size: 0.8em; color: #666;">(Київ)</small>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-hourglass-half"></i> Тривалість
                        </div>
                        <div class="value">${duration} хв</div>
                    </div>
                    
                    <div class="detail-item">
                        <div class="label">
                            <i class="fas fa-calendar"></i> Створено
                        </div>
                        <div class="value">${generatedTime}</div>
                    </div>
                </div>
                
                <div class="signal-timer" id="timer-${signalId}">
                    <div class="timer-display">
                        <i class="fas fa-hourglass-start"></i> 
                        <span class="timer-text">${this.translate('timeToEntry')} --:--</span>
                    </div>
                </div>
                
                ${signal.reason ? `
                <div class="signal-reason">
                    <div class="reason-header">
                        <i class="fas fa-lightbulb"></i> Аналіз AI
                    </div>
                    <div class="reason-text">${signal.reason}</div>
                </div>
                ` : ''}
                
                <div class="signal-feedback" id="feedback-${signalId}" style="display: none;">
                    <div class="feedback-content">
                        <p>${this.translate('feedbackQuestion')}</p>
                        <div class="feedback-buttons">
                            <button class="feedback-btn feedback-yes" onclick="signalDisplay.giveFeedback('${signalId}', 'yes')">
                                ${this.translate('feedbackYes')}
                            </button>
                            <button class="feedback-btn feedback-no" onclick="signalDisplay.giveFeedback('${signalId}', 'no')">
                                ${this.translate('feedbackNo')}
                            </button>
                            <button class="feedback-btn feedback-skip" onclick="signalDisplay.giveFeedback('${signalId}', 'skip')">
                                ${this.translate('feedbackSkip')}
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="signal-footer">
                    <span><i class="fas fa-globe-europe"></i> Часова зона: Київ (UTC+2)</span>
                    <span><i class="fas fa-brain"></i> Модель: GPT-OSS-120b</span>
                </div>
            </div>
        `;
    }

    setupSignalTimer(signal, signalId) {
        // Останавливаем старый таймер, если есть
        const oldTimer = this.activeTimers.get(signalId);
        if (oldTimer) {
            clearInterval(oldTimer);
        }
        
        // Используем entry_time_utc или конвертируем entry_time
        let entryTimeUTC;
        
        if (signal.entry_time_utc) {
            entryTimeUTC = new Date(signal.entry_time_utc);
        } else {
            // Конвертируем киевское время в UTC (предполагаем, что это сегодня)
            const entryTime = signal.entry_time_kyiv || signal.entry_time || '00:00';
            const [hours, minutes] = entryTime.split(':').map(Number);
            const now = new Date();
            const todayUTC = new Date(Date.UTC(
                now.getUTCFullYear(),
                now.getUTCMonth(),
                now.getUTCDate(),
                hours - 2, // Киев UTC+2
                minutes,
                0
            ));
            entryTimeUTC = todayUTC;
        }
        
        const durationMs = (parseInt(signal.duration) || 2) * 60000;
        const endTimeUTC = new Date(entryTimeUTC.getTime() + durationMs);
        
        const updateTimer = () => {
            const nowUTC = new Date();
            const timerElement = document.querySelector(`#timer-${signalId} .timer-text`);
            const feedbackElement = document.getElementById(`feedback-${signalId}`);
            
            if (!timerElement) {
                // Если элемент удален, останавливаем таймер
                const timer = this.activeTimers.get(signalId);
                if (timer) {
                    clearInterval(timer);
                    this.activeTimers.delete(signalId);
                }
                return;
            }
            
            if (nowUTC < entryTimeUTC) {
                // Чекаємо на вхід
                const timeLeft = entryTimeUTC - nowUTC;
                const minutes = Math.floor(timeLeft / 60000);
                const seconds = Math.floor((timeLeft % 60000) / 1000);
                timerElement.textContent = `${this.translate('timeToEntry')} ${minutes}:${seconds.toString().padStart(2, '0')}`;
                timerElement.parentElement.querySelector('i').className = 'fas fa-hourglass-start';
                timerElement.parentElement.parentElement.classList.remove('active');
            } else if (nowUTC < endTimeUTC) {
                // Угода активна
                const timeLeft = endTimeUTC - nowUTC;
                const minutes = Math.floor(timeLeft / 60000);
                const seconds = Math.floor((timeLeft % 60000) / 1000);
                timerElement.textContent = `${this.translate('tradeActive')} ${minutes}:${seconds.toString().padStart(2, '0')}`;
                timerElement.parentElement.querySelector('i').className = 'fas fa-hourglass-half';
                timerElement.parentElement.parentElement.classList.add('active');
            } else if (nowUTC < endTimeUTC + 60000) {
                // Показуємо опитувальник (1 хвилина після завершення)
                timerElement.textContent = this.translate('tradeCompleted');
                timerElement.parentElement.querySelector('i').className = 'fas fa-check-circle';
                timerElement.parentElement.parentElement.classList.remove('active');
                
                if (feedbackElement) {
                    feedbackElement.style.display = 'block';
                    const signalCard = document.getElementById(signalId);
                    if (signalCard) {
                        signalCard.classList.add('feedback-active');
                    }
                }
            } else {
                // Видаляємо сигнал після опитувальника
                const signalElement = document.getElementById(signalId);
                if (signalElement) {
                    signalElement.remove();
                    this.updateSignalCount();
                }
                
                // Останавливаем таймер
                const timer = this.activeTimers.get(signalId);
                if (timer) {
                    clearInterval(timer);
                    this.activeTimers.delete(signalId);
                }
                return;
            }
        };
        
        // Запускаем таймер и сохраняем ID
        const timerId = setInterval(updateTimer, 1000);
        this.activeTimers.set(signalId, timerId);
        
        // Первое обновление
        updateTimer();
    }

    giveFeedback(signalId, feedback) {
        const signalElement = document.getElementById(signalId);
        if (!signalElement) return;
        
        const asset = signalElement.dataset.asset;
        console.log(`Feedback for ${asset}: ${feedback}`);
        
        // Видаляємо сигнал
        signalElement.remove();
        this.updateSignalCount();
    }

    updateSignalCount() {
        const container = document.getElementById('signals-container');
        const activeSignals = container.querySelectorAll('.signal-card').length;
        document.getElementById('active-signals').textContent = activeSignals;
        
        if (activeSignals === 0) {
            document.getElementById('no-signals').style.display = 'block';
        }
    }

    forceRefresh() {
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.classList.add('spinning');
        refreshBtn.disabled = true;
        
        // Очищаем сохраненные сигналы
        this.clearSavedSignals();
        
        this.loadSignals(true).finally(() => {
            setTimeout(() => {
                refreshBtn.classList.remove('spinning');
                this.setupRefreshButton();
            }, 1000);
        });
    }

    updateKyivTime() {
        const now = new Date();
        const timeElement = document.getElementById('server-time');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('uk-UA', {
                timeZone: 'Europe/Kiev',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    formatTimeKyiv(date, includeSeconds = false) {
        return date.toLocaleTimeString('uk-UA', {
            timeZone: 'Europe/Kiev',
            hour: '2-digit',
            minute: '2-digit',
            second: includeSeconds ? '2-digit' : undefined
        });
    }

    getConfidenceClass(percent) {
        if (percent >= 85) return 'confidence-high';
        if (percent >= 75) return 'confidence-medium';
        return 'confidence-low';
    }

    showError(message) {
        const container = document.getElementById('signals-container');
        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Помилка</h3>
                <p>${message}</p>
                <button onclick="signalDisplay.forceRefresh()" class="refresh-btn">
                    <i class="fas fa-redo"></i> Спробувати знову
                </button>
            </div>
        `;
    }

    startAutoUpdate() {
        // Оновлюємо дані кожні 30 секунд
        setInterval(() => {
            this.loadSignals();
        }, 30000);
        
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadSignals();
                this.updateKyivTime();
            }
        });
    }

    async setupLanguage() {
        this.applyLanguage(this.language);
        
        document.getElementById('lang-uk').addEventListener('click', () => {
            this.switchLanguage('uk');
        });
        
        document.getElementById('lang-ru').addEventListener('click', () => {
            this.switchLanguage('ru');
        });
    }

    switchLanguage(lang) {
        this.language = lang;
        localStorage.setItem('language', lang);
        this.applyLanguage(lang);
        
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
    }

    applyLanguage(lang) {
        const translations = this.translations[lang];
        if (!translations) return;
        
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
        
        // Оновлюємо кнопки
        const searchBtn = document.getElementById('search-btn');
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (searchBtn) {
            searchBtn.innerHTML = '<i class="fas fa-search"></i> ' + translations.searchBtn;
        }
        
        if (refreshBtn && !refreshBtn.disabled) {
            refreshBtn.innerHTML = '<i class="fas fa-redo"></i> ' + translations.refreshBtn;
        }
    }

    translate(key) {
        return this.translations[this.language][key] || key;
    }

    // Останавливаем все таймеры при разгрузке страницы
    stopAllTimers() {
        this.activeTimers.forEach((timerId, signalId) => {
            clearInterval(timerId);
        });
        this.activeTimers.clear();
    }
}

let signalDisplay;

document.addEventListener('DOMContentLoaded', () => {
    signalDisplay = new SignalDisplay();
    window.signalDisplay = signalDisplay;
});

// Останавливаем таймеры при закрытии страницы
window.addEventListener('beforeunload', () => {
    if (signalDisplay) {
        signalDisplay.stopAllTimers();
    }
});
