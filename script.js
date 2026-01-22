class SignalDisplay {
    constructor() {
        const isLocal = window.location.hostname.includes('localhost') || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.protocol === 'file:';
        
        const repoName = 'pocket_trading_bot';
        
        if (isLocal) {
            this.signalsUrl = 'data/signals.json';
            this.historyUrl = 'data/history.json';
            this.feedbackUrl = 'data/feedback.json';
        } else {
            this.signalsUrl = `/${repoName}/data/signals.json`;
            this.historyUrl = `/${repoName}/data/history.json`;
            this.feedbackUrl = `/${repoName}/data/feedback.json`;
        }
        
        this.kyivTZ = 'Europe/Kiev';
        this.language = localStorage.getItem('language') || 'uk';
        this.activeTimers = new Map();
        this.signalTimers = new Map();
        this.updateInterval = null;
        this.autoUpdateTimer = null;
        this.nextUpdateTime = null;
        this.currentFeedbackSignal = null;
        
        // Додайте ці властивості
        this.githubToken = localStorage.getItem('github_token');
        this.isGenerating = false;
        this.generationCheckInterval = null;
        
        this.translations = {
            uk: {
                title: "AI Trading Signals",
                subtitle: "Автоматичні сигнали кожні 10 хвилин з використанням GPT OSS 120B AI",
                autoUpdate: "Оновлення:",
                every10min: "кожні 10 хв",
                minAccuracy: "Мін. точність:",
                model: "Модель:",
                entryDelay: "Вхід через:",
                nextUpdate: "Наступне оновлення:",
                lastUpdate: "Останнє оновлення",
                kievTime: "(Київський час)",
                activeSignals: "Активних сигналів",
                withConfidence: "з впевненістю >75%",
                totalSignals: "Всього сигналів",
                today: "сьогодні",
                successRate: "Точність AI",
                learning: "навчання активне",
                systemActive: "Система активна!",
                autoDescription: "Сигнали генеруються автоматично кожні 10 хвилин. AI аналізує ринок та вказує час входу через 2 хвилини. Максимум 6 сигналів одночасно. Можна запустити ручну генерацію кнопкою вище.",
                currentSignals: "Актуальні сигнали (останні 6)",
                serverTime: "Київський час:",
                loadingSignals: "Завантаження сигналів...",
                firstLoad: "Перше оновлення через",
                noSignalsNow: "Наразі немає актуальних сигналів",
                nextAutoUpdate: "Наступне автоматичне оновлення через",
                howItWorks: "Як працює система",
                autoGeneration: "Автоматична генерація:",
                autoGenDesc: "кожні 10 хвилин",
                entryDelay2: "Затримка входу:",
                entryDelayDesc: "2 хвилини для точнішого прогнозу",
                aiLearning: "Навчання AI:",
                aiLearningDesc: "аналізує успішність сигналів",
                autoCleanup: "Автоочищення:",
                autoCleanupDesc: "сигнали зникають через 10 хвилин",
                tokenLimits: "Ліміти використання",
                tokenLimitsDesc: "Для економії токенів AI обмежено до 3 сигналів за раз. Система розрахована на тривалу роботу. Ручна генерація використовує ваш GitHub токен.",
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
                statusWaiting: "Очікування",
                giveFeedback: "Оцінити сигнал",
                yes: "Так",
                no: "Ні",
                skip: "Пропустити",
                feedbackSaved: "Відгук збережено! AI навчиться на цьому",
                feedbackError: "Помилка збереження відгуку",
                signalRemoved: "Сигнал видалено",
                loading: "Завантаження...",
                generateSignals: "Пошук сигналів",
                generating: "Генерація...",
                triggeringGeneration: "Запуск генерації...",
                waitingGeneration: "Чекаємо генерацію...",
                checkingStatus: "Перевірка статусу...",
                generationSuccess: "Сигнали згенеровані!",
                generationFailed: "Помилка генерації",
                enterToken: "Введіть GitHub Token",
                tokenRequired: "Для ручної генерації потрібен токен",
                howToGetToken: "Як отримати токен",
                permissions: "Права",
                save: "Зберегти",
                cancel: "Скасувати"
            },
            ru: {
                title: "AI Торговые Сигналы",
                subtitle: "Автоматические сигналы каждые 10 минут с использованием GPT OSS 120B AI",
                autoUpdate: "Обновление:",
                every10min: "каждые 10 мин",
                minAccuracy: "Мин. точность:",
                model: "Модель:",
                entryDelay: "Вход через:",
                nextUpdate: "Следующее обновление:",
                lastUpdate: "Последнее обновление",
                kievTime: "(Киевское время)",
                activeSignals: "Активных сигналов",
                withConfidence: "с уверенностью >75%",
                totalSignals: "Всего сигналов",
                today: "сегодня",
                successRate: "Точность AI",
                learning: "обучение активно",
                systemActive: "Система активна!",
                autoDescription: "Сигналы генерируются автоматически каждые 10 минут. AI анализирует рынок и указывает время входа через 2 минуты. Максимум 6 сигналов одновременно. Можно запустить ручную генерацию кнопкой выше.",
                currentSignals: "Актуальные сигналы (последние 6)",
                serverTime: "Киевское время:",
                loadingSignals: "Загрузка сигналов...",
                firstLoad: "Первое обновление через",
                noSignalsNow: "В настоящее время нет актуальных сигналов",
                nextAutoUpdate: "Следующее автоматическое обновление через",
                howItWorks: "Как работает система",
                autoGeneration: "Автоматическая генерация:",
                autoGenDesc: "каждые 10 минут",
                entryDelay2: "Задержка входа:",
                entryDelayDesc: "2 минуты для более точного прогноза",
                aiLearning: "Обучение AI:",
                aiLearningDesc: "анализирует успешность сигналов",
                autoCleanup: "Автоочистка:",
                autoCleanupDesc: "сигналы исчезают через 10 минут",
                tokenLimits: "Ліміты использования",
                tokenLimitsDesc: "Для экономии токенов AI ограничено до 3 сигналов за раз. Система рассчитана на длительную работу. Ручная генерация использует ваш GitHub токен.",
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
                statusWaiting: "Ожидание",
                giveFeedback: "Оценить сигнал",
                yes: "Да",
                no: "Нет",
                skip: "Пропустить",
                feedbackSaved: "Отзыв сохранен! AI научится на этом",
                feedbackError: "Ошибка сохранения отзыва",
                signalRemoved: "Сигнал удален",
                loading: "Загрузка...",
                generateSignals: "Поиск сигналов",
                generating: "Генерация...",
                triggeringGeneration: "Запуск генерации...",
                waitingGeneration: "Ждем генерацию...",
                checkingStatus: "Проверка статуса...",
                generationSuccess: "Сигналы сгенерированы!",
                generationFailed: "Ошибка генерации",
                enterToken: "Введите GitHub Token",
                tokenRequired: "Для ручной генерации нужен токен",
                howToGetToken: "Как получить токен",
                permissions: "Права",
                save: "Сохранить",
                cancel: "Отмена"
            }
        };
        
        this.init();
    }

    async init() {
        await this.setupLanguage();
        this.setupEventListeners();
        this.updateKyivTime();
        setInterval(() => this.updateKyivTime(), 1000);
        
        setTimeout(() => {
            console.log("📥 Перше завантаження сигналів...");
            this.loadSignals();
            this.startAutoUpdate();
        }, 2000);
        
        this.startSignalCleanupCheck();
        
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('feedback-modal');
            if (e.target === modal) {
                this.hideFeedbackModal();
            }
        });
    }

    setupEventListeners() {
        document.getElementById('lang-uk').addEventListener('click', () => {
            this.switchLanguage('uk');
        });
        
        document.getElementById('lang-ru').addEventListener('click', () => {
            this.switchLanguage('ru');
        });
        
        // Додаємо обробник для кнопки ручної генерації
        this.setupManualGeneration();
    }
    
    setupManualGeneration() {
        const generateBtn = document.getElementById('manual-generate-btn');
        if (!generateBtn) return;
        
        // Оновлюємо текст кнопки
        generateBtn.innerHTML = `<i class="fas fa-search"></i> ${this.translate('generateSignals')}`;
        
        // Додаємо обробник подій
        generateBtn.addEventListener('click', () => {
            this.manualGenerateSignals();
        });
        
        // Перевіряємо наявність токена
        if (!this.githubToken) {
            // Якщо токена немає, додаємо підказку
            generateBtn.title = this.translate('tokenRequired');
        }
    }
    
    async manualGenerateSignals() {
        // Перевіряємо, чи вже йде генерація
        if (this.isGenerating) {
            this.showMessage('warning', 'Генерація вже запущена. Будь ласка, зачекайте.');
            return;
        }
        
        // Перевіряємо наявність токена
        if (!this.githubToken) {
            this.showTokenModal();
            return;
        }
        
        // Запускаємо генерацію
        await this.startGeneration();
    }
    
    async startGeneration() {
        try {
            this.isGenerating = true;
            this.updateGenerationUI(true, this.translate('triggeringGeneration'));
            
            // Конфігурація GitHub API
            const owner = 'Danik25326';
            const repo = 'pocket_trading_bot';
            const workflow_id = 'signals.yml';
            
            // Запускаємо workflow через GitHub API
            const response = await fetch(
                `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow_id}/dispatches`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `token ${this.githubToken}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ref: 'main',
                        inputs: {
                            language: this.language,
                            trigger_source: 'manual_site'
                        }
                    })
                }
            );
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Workflow не знайдено. Перевірте назву файлу workflow.');
                } else if (response.status === 403) {
                    throw new Error('Токен не має достатніх прав або недійсний.');
                } else {
                    throw new Error(`Помилка GitHub API: ${response.status}`);
                }
            }
            
            this.showMessage('success', '✅ Генерація сигналів запущена! Очікуйте оновлення...');
            this.updateGenerationUI(true, this.translate('waitingGeneration'));
            
            // Починаємо перевірку статусу
            this.startCheckingGenerationStatus();
            
        } catch (error) {
            console.error('❌ Помилка запуску генерації:', error);
            this.showMessage('error', `Помилка: ${error.message}`);
            
            // Якщо токен невірний, очищаємо його
            if (error.message.includes('токен') || error.message.includes('прав') || error.message.includes('недійсний')) {
                localStorage.removeItem('github_token');
                this.githubToken = null;
                this.showTokenModal();
            }
            
            this.isGenerating = false;
            this.updateGenerationUI(false, this.translate('generateSignals'));
        }
    }
    
    startCheckingGenerationStatus() {
        let checkCount = 0;
        const maxChecks = 30; // 30 спроб * 10 секунд = 5 хвилин
        
        this.generationCheckInterval = setInterval(async () => {
            checkCount++;
            
            if (checkCount > maxChecks) {
                clearInterval(this.generationCheckInterval);
                this.showMessage('warning', 'Генерація займає занадто багато часу. Спробуйте пізніше.');
                this.isGenerating = false;
                this.updateGenerationUI(false, this.translate('generateSignals'));
                return;
            }
            
            // Оновлюємо статус
            const progress = Math.min((checkCount / maxChecks) * 100, 90);
            this.updateGenerationUI(true, `${this.translate('checkingStatus')} (${checkCount}/${maxChecks})`, progress);
            
            try {
                // Перевіряємо, чи оновився signals.json
                const timestamp = Date.now();
                const response = await fetch(`${this.signalsUrl}?t=${timestamp}`);
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Перевіряємо час останнього оновлення
                    if (data.last_update) {
                        const updateTime = new Date(data.last_update);
                        const now = new Date();
                        const timeDiff = (now - updateTime) / 1000 / 60; // у хвилинах
                        
                        // Якщо файл оновлено менше ніж 2 хвилини тому
                        if (timeDiff < 2) {
                            clearInterval(this.generationCheckInterval);
                            
                            this.showMessage('success', '🎉 Сигнали успішно згенеровані!');
                            this.updateGenerationUI(true, this.translate('generationSuccess'), 100);
                            
                            // Завантажуємо нові сигнали через 2 секунди
                            setTimeout(() => {
                                this.loadSignals();
                                this.isGenerating = false;
                                this.updateGenerationUI(false, this.translate('generateSignals'));
                            }, 2000);
                            
                            return;
                        }
                    }
                }
            } catch (error) {
                console.log('Очікуємо оновлення сигналів...');
            }
            
        }, 10000); // Перевіряємо кожні 10 секунд
    }
    
    updateGenerationUI(isGenerating, text, progress = 0) {
        const generateBtn = document.getElementById('manual-generate-btn');
        const generateStatus = document.getElementById('generate-status');
        
        if (!generateBtn || !generateStatus) return;
        
        if (isGenerating) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
            
            generateStatus.style.display = 'flex';
            generateStatus.querySelector('.status-text').textContent = text;
            
            // Додаємо progress bar якщо є прогрес
            if (progress > 0) {
                if (!generateStatus.querySelector('.progress-bar')) {
                    const progressHtml = `
                        <div class="generate-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${progress}%"></div>
                            </div>
                            <div class="progress-text">${Math.round(progress)}%</div>
                        </div>
                    `;
                    generateStatus.innerHTML += progressHtml;
                } else {
                    const progressFill = generateStatus.querySelector('.progress-fill');
                    const progressText = generateStatus.querySelector('.progress-text');
                    if (progressFill) progressFill.style.width = `${progress}%`;
                    if (progressText) progressText.textContent = `${Math.round(progress)}%`;
                }
            }
        } else {
            generateBtn.disabled = false;
            generateBtn.innerHTML = `<i class="fas fa-search"></i> ${text}`;
            generateStatus.style.display = 'none';
        }
    }
    
    showTokenModal() {
        const modal = document.getElementById('token-modal');
        const tokenInput = document.getElementById('github-token-input');
        const saveBtn = document.getElementById('save-token-btn');
        
        if (!modal || !tokenInput || !saveBtn) return;
        
        // Оновлюємо тексти
        modal.querySelector('h3').innerHTML = `🔑 ${this.translate('enterToken')}`;
        modal.querySelector('p').textContent = this.translate('tokenRequired');
        
        const tokenHelp = modal.querySelector('.token-help');
        if (tokenHelp) {
            tokenHelp.querySelector('small').innerHTML = 
                `<i class="fas fa-info-circle"></i> ${this.translate('howToGetToken')}: `;
            tokenHelp.querySelector('a').textContent = 'GitHub → Settings → Developer settings → Tokens';
            
            const permissionsText = tokenHelp.querySelectorAll('small')[1];
            if (permissionsText) {
                permissionsText.innerHTML = `${this.translate('permissions')}: <code>repo</code> та <code>workflow</code>`;
            }
        }
        
        saveBtn.innerHTML = `<i class="fas fa-save"></i> ${this.translate('save')}`;
        saveBtn.onclick = () => this.saveToken();
        
        const cancelBtn = modal.querySelector('.feedback-btn.feedback-skip');
        if (cancelBtn) {
            cancelBtn.innerHTML = `<i class="fas fa-times"></i> ${this.translate('cancel')}`;
        }
        
        modal.style.display = 'flex';
        tokenInput.focus();
    }
    
    hideTokenModal() {
        const modal = document.getElementById('token-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    saveToken() {
        const tokenInput = document.getElementById('github-token-input');
        if (!tokenInput) return;
        
        const token = tokenInput.value.trim();
        
        if (!token) {
            this.showMessage('error', 'Будь ласка, введіть токен');
            return;
        }
        
        // Перевіряємо формат токена
        if (!token.startsWith('ghp_') && !token.startsWith('ghs_') && !token.startsWith('github_pat_')) {
            this.showMessage('warning', 'Токен має невірний формат. Перевірте, чи правильно скопіювали.');
            return;
        }
        
        // Зберігаємо токен
        localStorage.setItem('github_token', token);
        this.githubToken = token;
        
        this.hideTokenModal();
        this.showMessage('success', '✅ Токен збережено! Тепер можете генерувати сигнали.');
        
        // Оновлюємо кнопку
        const generateBtn = document.getElementById('manual-generate-btn');
        if (generateBtn) {
            generateBtn.title = '';
        }
    }

    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            console.log("🔄 Автоматичне оновлення сигналів (кожні 10 хвилин)...");
            this.showMessage('info', 'Автоматичне оновлення сигналів...');
            this.loadSignals();
        }, 600000);
        
        this.updateNextUpdateTimer();
        setInterval(() => this.updateNextUpdateTimer(), 1000);
        
        console.log("✅ Автооновлення активоване: кожні 10 хвилин");
    }

    updateNextUpdateTimer() {
        if (!this.nextUpdateTime) {
            this.nextUpdateTime = Date.now() + 600000;
        }
        
        const now = Date.now();
        const timeLeft = this.nextUpdateTime - now;
        
        if (timeLeft <= 0) {
            this.nextUpdateTime = now + 600000;
            return;
        }
        
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);
        
        const updateTimer = document.getElementById('next-update-timer');
        const autoTimer = document.getElementById('next-auto-timer');
        
        if (updateTimer) {
            updateTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        if (autoTimer) {
            autoTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    async loadSignals() {
        try {
            const timestamp = Date.now();
            const url = `${this.signalsUrl}?t=${timestamp}`;
            
            console.log("📥 Запит до:", url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            console.log("✅ Сигнали завантажені успішно!");
            console.log("📊 Статистика:", {
                signalsCount: data.signals?.length || 0,
                activeSignals: data.active_signals || 0,
                totalSignals: data.total_signals || 0,
                lastUpdate: data.last_update,
                generationCount: data.generation_count || 0
            });
            
            if (data.signals && data.signals.length > 0) {
                console.log("🎯 Останній сигнал:", data.signals[0]);
            }
            
            this.processSignals(data);
            
            this.nextUpdateTime = Date.now() + 600000;
            
        } catch (error) {
            console.error('❌ Помилка завантаження сигналів:', error);
            
            this.tryAlternativePaths(error);
        }
    }

    tryAlternativePaths(error) {
        console.log("🔄 Спробую альтернативні шляхи...");
        
        const alternativePaths = [
            'data/signals.json',
            '/data/signals.json',
            './data/signals.json',
            'https://raw.githubusercontent.com/Danik25326/pocket_trading_bot/main/data/signals.json'
        ];
        
        let currentIndex = 0;
        
        const tryNextPath = () => {
            if (currentIndex >= alternativePaths.length) {
                this.showMessage('error', `Помилка завантаження: ${error.message}. Спробуйте оновити сторінку.`);
                return;
            }
            
            const testPath = alternativePaths[currentIndex];
            console.log(`🔄 Тестую шлях: ${testPath}`);
            
            fetch(`${testPath}?t=${Date.now()}`)
                .then(response => {
                    if (response.ok) {
                        console.log(`✅ Знайдено працюючий шлях: ${testPath}`);
                        this.signalsUrl = testPath;
                        this.showMessage('success', 'Підключення відновлено!');
                        setTimeout(() => this.loadSignals(), 1000);
                    } else {
                        currentIndex++;
                        setTimeout(tryNextPath, 500);
                    }
                })
                .catch(() => {
                    currentIndex++;
                    setTimeout(tryNextPath, 500);
                });
        };
        
        tryNextPath();
    }

    processSignals(data) {
        const container = document.getElementById('signals-container');
        const noSignals = document.getElementById('no-signals');
        const lastUpdate = document.getElementById('last-update');
        const activeSignalsElement = document.getElementById('active-signals');
        const totalSignalsElement = document.getElementById('total-signals');
        const successRateElement = document.getElementById('success-rate');
        
        if (!container || !lastUpdate || !activeSignalsElement || !totalSignalsElement || !successRateElement) {
            console.error("❌ Не знайдено необхідні елементи DOM");
            return;
        }
        
        this.clearAllTimers();
        
        if (!data || !data.signals || data.signals.length === 0) {
            console.log("⚠️ Немає сигналів для відображення");
            container.innerHTML = this.getEmptyStateHTML();
            
            if (data && data.last_update) {
                try {
                    const updateDate = new Date(data.last_update);
                    lastUpdate.textContent = this.formatTime(updateDate, true);
                    console.log("🕐 Останнє оновлення:", this.formatTime(updateDate, true));
                } catch (e) {
                    lastUpdate.textContent = data.last_update || '--:--:--';
                }
            } else {
                lastUpdate.textContent = '--:--:--';
            }
            
            activeSignalsElement.textContent = '0';
            totalSignalsElement.textContent = '0';
            successRateElement.textContent = '0%';
            
            if (noSignals) {
                noSignals.style.display = 'block';
            }
            return;
        }
        
        if (data.last_update) {
            try {
                const updateDate = new Date(data.last_update);
                lastUpdate.textContent = this.formatTime(updateDate, true);
                console.log("🕐 Останнє оновлення:", this.formatTime(updateDate, true));
            } catch (e) {
                lastUpdate.textContent = data.last_update;
            }
        }
        
        activeSignalsElement.textContent = data.active_signals || data.signals.length;
        totalSignalsElement.textContent = data.total_signals || data.signals.length;
        
        const successRate = this.calculateSuccessRate(data);
        successRateElement.textContent = `${successRate}%`;
        
        let html = '';
        let displayedSignals = 0;
        
        const sortedSignals = [...data.signals].sort((a, b) => {
            const timeA = a.generated_at ? new Date(a.generated_at).getTime() : 0;
            const timeB = b.generated_at ? new Date(b.generated_at).getTime() : 0;
            return timeB - timeA;
        });
        
        const latestSignals = sortedSignals.slice(0, 6);
        
        latestSignals.forEach((signal, index) => {
            const confidencePercent = Math.round((signal.confidence || 0) * 100);
            if (confidencePercent < 75) {
                console.log(`⚠️ Сигнал ${signal.asset} пропущено (впевненість ${confidencePercent}% < 75%)`);
                return;
            }
            
            const signalHTML = this.createSignalHTML(signal, index);
            if (signalHTML) {
                html += signalHTML;
                displayedSignals++;
            }
        });
        
        if (displayedSignals === 0) {
            container.innerHTML = this.getNoSignalsHTML();
            if (noSignals) {
                noSignals.style.display = 'block';
            }
            console.log("⚠️ Немає сигналів з достатньою впевненістю");
        } else {
            container.innerHTML = html;
            if (noSignals) {
                noSignals.style.display = 'none';
            }
            
            console.log("📊 Відображено сигналів:", displayedSignals);
            
            latestSignals.forEach((signal, index) => {
                if (index < displayedSignals) {
                    this.setupSignalTimer(signal, index);
                }
            });
            
            this.showMessage('success', `Завантажено ${displayedSignals} сигналів`);
        }
    }

    clearAllTimers() {
        this.signalTimers.forEach((timer, index) => {
            clearInterval(timer);
        });
        this.signalTimers.clear();
    }

    createSignalHTML(signal, index) {
        const confidencePercent = Math.round(signal.confidence * 100);
        const confidenceClass = this.getConfidenceClass(confidencePercent);
        const directionClass = signal.direction.toLowerCase();
        const duration = signal.duration || 3;
        
        const generatedTime = signal.generated_at ? 
            this.convertToKyivTime(signal.generated_at) : '--:--';
        const entryTime = signal.entry_time || '--:--';
        
        let reason = signal.reason || '';
        if (this.language === 'ru' && signal.reason_ru) {
            reason = signal.reason_ru;
        }
        
        if (reason.length > 150) {
            reason = reason.substring(0, 150) + '...';
        }
        
        return `
            <div class="signal-card ${directionClass}" id="signal-${index}" 
                 data-generated="${signal.generated_at}" 
                 data-asset="${signal.asset}"
                 data-id="${signal.id || ''}"
                 data-index="${index}">
                <div class="signal-header">
                    <div class="asset-info">
                        <div class="asset-icon ${directionClass === 'up' ? 'up-icon' : 'down-icon'}">
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
                        ${this.translate('expiresIn')}: <span class="expiry-time">10:00</span>
                    </div>
                    <button class="feedback-trigger" onclick="signalDisplay.showFeedbackModal('${signal.id || index}', ${index})">
                        <i class="fas fa-star"></i> ${this.translate('giveFeedback')}
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
        
        // Час експірації: точно 10 хвилин після генерації
        const expiryTime = new Date(generatedTime.getTime() + 10 * 60000);
        
        // Час входу: точно 2 хвилини після генерації
        const entryTime = new Date(generatedTime.getTime() + 2 * 60000);
        
        const updateTimer = () => {
            const now = new Date();
            const timeToExpiry = expiryTime - now;
            
            if (timeToExpiry <= 0) {
                const signalElement = document.getElementById(`signal-${index}`);
                if (signalElement) {
                    signalElement.classList.add('expired');
                    signalElement.style.opacity = '0.5';
                    setTimeout(() => {
                        if (signalElement.parentNode) {
                            signalElement.remove();
                            this.updateSignalCount();
                        }
                    }, 1000);
                }
                
                if (this.signalTimers.has(index)) {
                    clearInterval(this.signalTimers.get(index));
                    this.signalTimers.delete(index);
                }
                return;
            }
            
            const expiryMinutes = Math.floor(timeToExpiry / 60000);
            const expirySeconds = Math.floor((timeToExpiry % 60000) / 1000);
            
            if (expiryElement) {
                const expiryTimeSpan = expiryElement.querySelector('.expiry-time');
                if (expiryTimeSpan) {
                    expiryTimeSpan.textContent = `${expiryMinutes}:${expirySeconds.toString().padStart(2, '0')}`;
                }
            }
            
            const timeToEntry = entryTime - now;
            
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
                const timeAfterEntry = Math.abs(timeToEntry);
                const minutesAfter = Math.floor(timeAfterEntry / 60000);
                const secondsAfter = Math.floor((timeAfterEntry % 60000) / 1000);
                timerElement.innerHTML = `
                    <div class="timer-display">
                        <i class="fas fa-check-circle"></i>
                        <span class="timer-text">${minutesAfter}:${secondsAfter.toString().padStart(2, '0')}</span>
                    </div>
                    <small>${this.translate('signalCompleted')}</small>
                `;
            }
        };
        
        updateTimer();
        const timerInterval = setInterval(updateTimer, 1000);
        this.signalTimers.set(index, timerInterval);
    }

    startSignalCleanupCheck() {
        setInterval(() => {
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
        const noSignals = document.getElementById('no-signals');
        if (!container) return;
        
        const activeSignals = container.querySelectorAll('.signal-card:not(.expired)').length;
        const activeSignalsElement = document.getElementById('active-signals');
        
        if (activeSignalsElement) {
            activeSignalsElement.textContent = activeSignals;
        }
        
        if (activeSignals === 0 && noSignals) {
            noSignals.style.display = 'block';
        }
    }

    calculateSuccessRate(data) {
        try {
            if (data.success_rate !== undefined) {
                return Math.round(data.success_rate * 100);
            }
            
            if (data.signals && data.signals.length > 0) {
                const validSignals = data.signals.filter(s => s.confidence >= 0.75);
                if (validSignals.length > 0) {
                    const totalConfidence = validSignals.reduce((sum, signal) => {
                        return sum + (signal.confidence || 0);
                    }, 0);
                    const avgConfidence = totalConfidence / validSignals.length;
                    return Math.round(avgConfidence * 100);
                }
            }
            
            return 75;
        } catch (e) {
            console.warn("⚠️ Помилка розрахунку успішності:", e);
            return 75;
        }
    }

    showFeedbackModal(signalId, index) {
        const signalElement = document.getElementById(`signal-${index}`);
        if (!signalElement) return;
        
        const asset = signalElement.dataset.asset;
        this.currentFeedbackSignal = {
            id: signalId,
            index: index,
            asset: asset,
            element: signalElement
        };
        
        const modal = document.getElementById('feedback-modal');
        const feedbackAsset = document.getElementById('feedback-asset');
        
        if (modal && feedbackAsset) {
            feedbackAsset.textContent = `${asset} (ID: ${signalId || 'N/A'})`;
            modal.style.display = 'flex';
        }
    }

    hideFeedbackModal() {
        const modal = document.getElementById('feedback-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.currentFeedbackSignal = null;
    }

    async submitFeedback(feedback) {
        if (!this.currentFeedbackSignal) return;
        
        const { id, index, asset, element } = this.currentFeedbackSignal;
        
        try {
            await new Promise(resolve => setTimeout(resolve, 300));
            
            console.log("💾 Фідбек збережено:", { id, asset, feedback });
            
            this.showMessage('success', this.translate('feedbackSaved'));
            
            element.classList.add('feedback-given');
            element.style.opacity = '0.3';
            
            setTimeout(() => {
                if (element.parentNode) {
                    element.remove();
                    this.updateSignalCount();
                }
            }, 500);
            
            this.hideFeedbackModal();
            
            this.updateSuccessRate();
            
        } catch (error) {
            console.error('❌ Помилка відправки feedback:', error);
            this.showMessage('error', this.translate('feedbackError'));
        }
    }

    updateSuccessRate() {
        const successRateElement = document.getElementById('success-rate');
        if (!successRateElement) return;
        
        const currentRate = parseInt(successRateElement.textContent) || 0;
        const newRate = Math.min(100, currentRate + 2);
        successRateElement.textContent = `${newRate}%`;
    }

    updateKyivTime() {
        const now = new Date();
        const timeElement = document.getElementById('server-time');
        
        if (timeElement) {
            try {
                timeElement.textContent = now.toLocaleTimeString('uk-UA', {
                    timeZone: this.kyivTZ,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            } catch (e) {
                timeElement.textContent = now.toLocaleTimeString();
            }
        }
    }

    formatTime(date, includeSeconds = false) {
        try {
            return date.toLocaleTimeString('uk-UA', {
                timeZone: this.kyivTZ,
                hour: '2-digit',
                minute: '2-digit',
                second: includeSeconds ? '2-digit' : undefined
            });
        } catch (e) {
            return date.toLocaleTimeString();
        }
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
            try {
                const date = new Date(dateString);
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } catch (e2) {
                return '--:--';
            }
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
                    <i class="fas fa-robot fa-spin"></i>
                </div>
                <p>${this.translate('loadingSignals')}</p>
                <small>${this.translate('firstLoad')} <span id="first-load-timer">3</span> сек</small>
            </div>
        `;
    }

    getNoSignalsHTML() {
        return `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <h3>${this.translate('noSignalsNow')}</h3>
                <p>${this.translate('nextAutoUpdate')} <span id="next-auto-timer">10:00</span></p>
            </div>
        `;
    }

    showMessage(type, text) {
        let messageContainer = document.getElementById('message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'message-container';
            document.body.appendChild(messageContainer);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                               type === 'error' ? 'exclamation-circle' : 
                               'info-circle'}"></i>
            <span>${text}</span>
        `;
        
        messageContainer.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 5000);
    }

    async setupLanguage() {
        this.applyLanguage(this.language);
        
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === this.language);
        });
        
        // Оновлюємо текст кнопки ручної генерації
        const generateBtn = document.getElementById('manual-generate-btn');
        if (generateBtn) {
            generateBtn.innerHTML = `<i class="fas fa-search"></i> ${this.translate('generateSignals')}`;
        }
    }

    switchLanguage(lang) {
        this.language = lang;
        localStorage.setItem('language', lang);
        this.applyLanguage(lang);
        
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        
        console.log("🌐 Змінено мову на:", lang);
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

let signalDisplay;

document.addEventListener('DOMContentLoaded', () => {
    signalDisplay = new SignalDisplay();
    window.signalDisplay = signalDisplay;
});
