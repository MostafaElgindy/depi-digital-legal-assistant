/**
 * Al-Dustour AI - Frontend Application
 * ======================================
 * تطبيق JavaScript للتعامل مع واجهة المستخدم.
 * يستخدم صيغة TOON للتواصل مع الخادم.
 */

// ==================== TOON Parser/Serializer ====================

const TOON = {
    /**
     * تحويل كائن JavaScript إلى نص TOON
     */
    stringify(obj, indent = '') {
        let lines = [];
        
        for (const [key, value] of Object.entries(obj)) {
            if (value === null || value === undefined) continue;
            
            if (typeof value === 'string') {
                const escaped = value.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
                lines.push(`${indent}${key} = "${escaped}"`);
            } else if (typeof value === 'number') {
                lines.push(`${indent}${key} = ${value}`);
            } else if (typeof value === 'boolean') {
                lines.push(`${indent}${key} = ${value}`);
            } else if (Array.isArray(value)) {
                if (value.length === 0) {
                    lines.push(`${indent}${key} = []`);
                } else if (typeof value[0] !== 'object') {
                    const items = value.map(v => typeof v === 'string' ? `"${v}"` : v).join(', ');
                    lines.push(`${indent}${key} = [${items}]`);
                } else {
                    value.forEach(item => {
                        lines.push(`\n[[${key}]]`);
                        lines.push(this.stringify(item, ''));
                    });
                }
            } else if (typeof value === 'object') {
                lines.push(`\n[${key}]`);
                lines.push(this.stringify(value, ''));
            }
        }
        
        return lines.join('\n');
    },

    /**
     * تحليل نص TOON إلى كائن JavaScript
     */
    parse(toonString) {
        const result = {};
        let currentSection = result;
        let currentArrayName = null;
        
        const lines = toonString.split('\n');
        
        for (let line of lines) {
            line = line.trim();
            if (!line || line.startsWith('#')) continue;
            
            // Array table [[array]]
            if (line.startsWith('[[') && line.endsWith(']]')) {
                const arrayName = line.slice(2, -2).trim();
                if (!result[arrayName]) result[arrayName] = [];
                const newItem = {};
                result[arrayName].push(newItem);
                currentSection = newItem;
                currentArrayName = arrayName;
                continue;
            }
            
            // Section [section]
            if (line.startsWith('[') && line.endsWith(']')) {
                const sectionName = line.slice(1, -1).trim();
                const parts = sectionName.split('.');
                currentSection = this._ensurePath(result, parts);
                currentArrayName = null;
                continue;
            }
            
            // Key = Value
            const eqIndex = line.indexOf('=');
            if (eqIndex > 0) {
                const key = line.slice(0, eqIndex).trim();
                let value = line.slice(eqIndex + 1).trim();
                currentSection[key] = this._parseValue(value);
            }
        }
        
        return result;
    },

    _parseValue(value) {
        // String
        if (value.startsWith('"') && value.endsWith('"')) {
            return value.slice(1, -1)
                .replace(/\\n/g, '\n')
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '\\');
        }
        // Number
        if (/^-?\d+\.?\d*$/.test(value)) return parseFloat(value);
        // Boolean
        if (value === 'true') return true;
        if (value === 'false') return false;
        // Array
        if (value.startsWith('[') && value.endsWith(']')) {
            const inner = value.slice(1, -1).trim();
            if (!inner) return [];
            return inner.split(',').map(item => this._parseValue(item.trim()));
        }
        return value;
    },

    _ensurePath(obj, path) {
        let current = obj;
        for (const key of path) {
            if (!current[key]) current[key] = {};
            current = current[key];
        }
        return current;
    }
};

// ==================== API Client ====================

const API = {
    baseUrl: '',
    contentType: 'application/toon',

    async post(endpoint, data) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'POST',
                headers: { 'Content-Type': this.contentType },
                body: TOON.stringify(data)
            });
            const text = await response.text();
            return { ok: response.ok, status: response.status, data: TOON.parse(text) };
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async get(endpoint) {
        try {
            const response = await fetch(this.baseUrl + endpoint);
            const text = await response.text();
            return { ok: response.ok, status: response.status, data: TOON.parse(text) };
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        for (const [key, value] of Object.entries(additionalData)) {
            formData.append(key, value);
        }
        
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'POST',
            body: formData
        });
        const text = await response.text();
        return { ok: response.ok, status: response.status, data: TOON.parse(text) };
    }
};

// ==================== App State ====================

const AppState = {
    currentSection: 'chat',
    isLoading: false,
    chatHistory: [],
    queryHistory: JSON.parse(localStorage.getItem('queryHistory') || '[]'),
    theme: localStorage.getItem('theme') || 'light',
    settings: {
        showSources: true,
        numSources: 5
    }
};

// ==================== DOM Elements ====================

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const Elements = {
    // Loading
    loadingOverlay: $('#loadingOverlay'),
    
    // Sidebar
    sidebar: $('#sidebar'),
    sidebarToggle: $('#sidebarToggle'),
    mobileMenuBtn: $('#mobileMenuBtn'),
    navItems: $$('.nav-item'),
    systemStatus: $('#systemStatus'),
    
    // Header
    sectionTitle: $('#sectionTitle'),
    themeToggle: $('#themeToggle'),
    
    // Sections
    chatSection: $('#chatSection'),
    uploadSection: $('#uploadSection'),
    historySection: $('#historySection'),
    settingsSection: $('#settingsSection'),
    
    // Chat
    welcomeCard: $('#welcomeCard'),
    chatMessages: $('#chatMessages'),
    chatForm: $('#chatForm'),
    queryInput: $('#queryInput'),
    sendBtn: $('#sendBtn'),
    showSources: $('#showSources'),
    numSources: $('#numSources'),
    exampleChips: $$('.example-chip'),
    
    // Upload
    uploadForm: $('#uploadForm'),
    dropZone: $('#dropZone'),
    fileInput: $('#fileInput'),
    selectedFileName: $('#selectedFileName'),
    removeFile: $('#removeFile'),
    docName: $('#docName'),
    uploadSubmitBtn: $('#uploadSubmitBtn'),
    uploadProgress: $('#uploadProgress'),
    progressFill: $('#progressFill'),
    progressText: $('#progressText'),
    initBtn: $('#initBtn'),
    documentsList: $('#documentsList'),
    
    // History
    historyList: $('#historyList'),
    historyEmpty: $('#historyEmpty'),
    clearHistoryBtn: $('#clearHistoryBtn'),
    
    // Settings
    themeButtons: $$('.theme-btn'),
    defaultSources: $('#defaultSources'),
    autoShowSources: $('#autoShowSources'),
    infoStatus: $('#infoStatus'),
    infoDocuments: $('#infoDocuments'),
    
    // Toast
    toastContainer: $('#toastContainer')
};

// ==================== Utilities ====================

function formatTime(date = new Date()) {
    return date.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(date = new Date()) {
    return date.toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info', duration = 4000) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close">×</button>
    `;
    
    Elements.toastContainer.appendChild(toast);
    
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => removeToast(toast));
    
    setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
    toast.style.animation = 'slideIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
}

// ==================== Theme ====================

function setTheme(theme) {
    AppState.theme = theme;
    localStorage.setItem('theme', theme);
    
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
    
    // Update buttons
    Elements.themeButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
}

// ==================== Navigation ====================

function switchSection(sectionName) {
    AppState.currentSection = sectionName;
    
    // Update nav items
    Elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.section === sectionName);
    });
    
    // Update sections
    $$('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const sectionMap = {
        'chat': Elements.chatSection,
        'upload': Elements.uploadSection,
        'history': Elements.historySection,
        'settings': Elements.settingsSection
    };
    
    const titles = {
        'chat': 'استشارة قانونية',
        'upload': 'رفع وثيقة',
        'history': 'سجل الاستشارات',
        'settings': 'الإعدادات'
    };
    
    if (sectionMap[sectionName]) {
        sectionMap[sectionName].classList.add('active');
        Elements.sectionTitle.textContent = titles[sectionName];
    }
    
    // Close mobile sidebar
    Elements.sidebar.classList.remove('open');
    
    // Load section data
    if (sectionName === 'history') loadHistory();
    if (sectionName === 'upload') loadDocuments();
    if (sectionName === 'settings') loadSystemInfo();
}

// ==================== System Status ====================

async function checkSystemStatus() {
    try {
        const response = await API.get('/api/health');
        const statusDot = Elements.systemStatus.querySelector('.status-dot');
        const statusLabel = Elements.systemStatus.querySelector('.status-label');
        
        if (response.ok && response.data.status === 'healthy') {
            statusDot.className = 'status-dot online';
            statusLabel.textContent = `${response.data.documents_loaded || 0} وثيقة`;
            Elements.infoStatus.textContent = 'يعمل';
            Elements.infoDocuments.textContent = response.data.documents_loaded || 0;
        } else {
            statusDot.className = 'status-dot offline';
            statusLabel.textContent = 'غير متصل';
            Elements.infoStatus.textContent = 'غير متصل';
        }
    } catch (error) {
        const statusDot = Elements.systemStatus.querySelector('.status-dot');
        const statusLabel = Elements.systemStatus.querySelector('.status-label');
        statusDot.className = 'status-dot offline';
        statusLabel.textContent = 'خطأ في الاتصال';
    }
}

// ==================== Chat ====================

function addMessage(type, content, metadata = {}) {
    Elements.welcomeCard.classList.add('hidden');
    
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.id = `msg-${generateId()}`;
    
    const avatar = type === 'user' ? '👤' : '⚖️';
    const sender = type === 'user' ? 'أنت' : 'المستشار القانوني';
    
    let sourcesHtml = '';
    if (metadata.sources && metadata.sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <button class="sources-toggle" onclick="toggleSources(this)">
                    <span>📂</span>
                    <span>المصادر الدستورية (${metadata.sources.length})</span>
                    <span class="arrow">▼</span>
                </button>
                <div class="sources-list">
                    ${metadata.sources.map((source, i) => `
                        <div class="source-item">
                            <div class="source-header">
                                <span>المصدر ${i + 1}</span>
                                <span>صفحة ${(source.page_number || 0) + 1}</span>
                            </div>
                            <div class="source-text">${escapeHtml(source.content || '')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    let metaHtml = '';
    if (type === 'assistant' && metadata.model) {
        metaHtml = `
            <div class="message-meta">
                <span class="meta-item">🤖 ${metadata.model}</span>
                ${metadata.time ? `<span class="meta-item">⏱️ ${metadata.time}ث</span>` : ''}
            </div>
        `;
    }
    
    message.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${sender}</span>
                <span class="message-time">${formatTime()}</span>
            </div>
            <div class="message-text">${type === 'loading' ? '<div class="typing-indicator"><span></span><span></span><span></span></div> جاري التفكير...' : escapeHtml(content)}</div>
            ${metaHtml}
            ${sourcesHtml}
        </div>
    `;
    
    Elements.chatMessages.appendChild(message);
    Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
    
    return message.id;
}

function updateMessage(messageId, content, metadata = {}) {
    const message = $(`#${messageId}`);
    if (!message) return;
    
    message.classList.remove('loading');
    
    const textEl = message.querySelector('.message-text');
    textEl.innerHTML = escapeHtml(content);
    
    // Add metadata
    if (metadata.model) {
        const metaHtml = `
            <div class="message-meta">
                <span class="meta-item">🤖 ${metadata.model}</span>
                ${metadata.time ? `<span class="meta-item">⏱️ ${metadata.time}ث</span>` : ''}
            </div>
        `;
        const contentEl = message.querySelector('.message-content');
        contentEl.insertAdjacentHTML('beforeend', metaHtml);
    }
    
    // Add sources
    if (metadata.sources && metadata.sources.length > 0) {
        const sourcesHtml = `
            <div class="message-sources">
                <button class="sources-toggle" onclick="toggleSources(this)">
                    <span>📂</span>
                    <span>المصادر الدستورية (${metadata.sources.length})</span>
                    <span class="arrow">▼</span>
                </button>
                <div class="sources-list">
                    ${metadata.sources.map((source, i) => `
                        <div class="source-item">
                            <div class="source-header">
                                <span>المصدر ${i + 1}</span>
                                <span>صفحة ${(source.page_number || 0) + 1}</span>
                            </div>
                            <div class="source-text">${escapeHtml(source.content || '')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        const contentEl = message.querySelector('.message-content');
        contentEl.insertAdjacentHTML('beforeend', sourcesHtml);
    }
    
    Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
}

function removeMessage(messageId) {
    const message = $(`#${messageId}`);
    if (message) message.remove();
}

function toggleSources(button) {
    button.classList.toggle('open');
    const sourcesList = button.nextElementSibling;
    sourcesList.classList.toggle('open');
}

async function sendQuery(query) {
    if (AppState.isLoading || !query.trim()) return;
    
    AppState.isLoading = true;
    Elements.sendBtn.classList.add('loading');
    Elements.sendBtn.disabled = true;
    
    // Add user message
    addMessage('user', query);
    
    // Add loading message
    const loadingId = addMessage('loading', '');
    const loadingMsg = $(`#${loadingId}`);
    loadingMsg.classList.add('loading');
    
    try {
        const response = await API.post('/api/query/ask', {
            query: query,
            num_results: parseInt(Elements.numSources.value),
            include_sources: Elements.showSources.checked
        });
        
        removeMessage(loadingId);
        
        if (response.ok && response.data.success) {
            addMessage('assistant', response.data.answer, {
                model: response.data.model_used,
                time: response.data.processing_time,
                sources: response.data.sources
            });
            
            // Save to history
            saveToHistory(query, response.data);
            
        } else {
            addMessage('assistant', `عذراً، حدث خطأ: ${response.data.error_message || 'خطأ غير معروف'}`, {});
            showToast(response.data.error_message || 'حدث خطأ', 'error');
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('assistant', 'عذراً، لا يمكن الاتصال بالخادم. تأكد من تشغيل الخادم وحاول مرة أخرى.', {});
        showToast('خطأ في الاتصال بالخادم', 'error');
    } finally {
        AppState.isLoading = false;
        Elements.sendBtn.classList.remove('loading');
        Elements.sendBtn.disabled = false;
        Elements.queryInput.focus();
    }
}

// ==================== History ====================

function saveToHistory(query, response) {
    const historyItem = {
        id: generateId(),
        query: query,
        answer: response.answer,
        model: response.model_used,
        time: response.processing_time,
        sources: response.sources,
        timestamp: new Date().toISOString()
    };
    
    AppState.queryHistory.unshift(historyItem);
    
    // Keep only last 50 items
    if (AppState.queryHistory.length > 50) {
        AppState.queryHistory = AppState.queryHistory.slice(0, 50);
    }
    
    localStorage.setItem('queryHistory', JSON.stringify(AppState.queryHistory));
}

function loadHistory() {
    Elements.historyList.innerHTML = '';
    
    if (AppState.queryHistory.length === 0) {
        Elements.historyEmpty.classList.remove('hidden');
        return;
    }
    
    Elements.historyEmpty.classList.add('hidden');
    
    AppState.queryHistory.forEach(item => {
        const date = new Date(item.timestamp);
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-query">${escapeHtml(item.query)}</div>
            <div class="history-answer">${escapeHtml(item.answer)}</div>
            <div class="history-meta">
                <span>📅 ${formatDate(date)}</span>
                <span>🕐 ${formatTime(date)}</span>
                ${item.time ? `<span>⏱️ ${item.time}ث</span>` : ''}
            </div>
        `;
        
        historyItem.addEventListener('click', () => {
            switchSection('chat');
            Elements.queryInput.value = item.query;
            Elements.queryInput.focus();
        });
        
        Elements.historyList.appendChild(historyItem);
    });
}

function clearHistory() {
    if (!confirm('هل أنت متأكد من مسح سجل الاستشارات؟')) return;
    
    AppState.queryHistory = [];
    localStorage.removeItem('queryHistory');
    loadHistory();
    showToast('تم مسح السجل بنجاح', 'success');
}

// ==================== Upload ====================

async function loadDocuments() {
    try {
        const response = await API.get('/api/documents/list');
        
        if (response.ok && response.data.success) {
            const files = response.data.uploaded_files || [];
            const totalChunks = response.data.total_chunks || 0;
            
            if (files.length === 0 && totalChunks === 0) {
                Elements.documentsList.innerHTML = '<div class="no-documents">لا توجد وثائق محملة</div>';
            } else {
                let html = '';
                
                if (totalChunks > 0) {
                    html += `<div class="document-item">
                        <span class="doc-icon">📚</span>
                        <span class="doc-name">قاعدة البيانات (${totalChunks} جزء)</span>
                    </div>`;
                }
                
                files.forEach(file => {
                    html += `<div class="document-item">
                        <span class="doc-icon">📄</span>
                        <span class="doc-name">${escapeHtml(file)}</span>
                    </div>`;
                });
                
                Elements.documentsList.innerHTML = html;
            }
        }
    } catch (error) {
        Elements.documentsList.innerHTML = '<div class="no-documents">خطأ في تحميل القائمة</div>';
    }
}

async function uploadDocument(file) {
    Elements.uploadSubmitBtn.classList.add('loading');
    Elements.uploadSubmitBtn.disabled = true;
    Elements.uploadProgress.classList.add('show');
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        Elements.progressFill.style.width = `${progress}%`;
        Elements.progressText.textContent = `جاري الرفع... ${Math.round(progress)}%`;
    }, 200);
    
    try {
        const docName = Elements.docName.value.trim() || null;
        const response = await API.uploadFile('/api/documents/upload', file, 
            docName ? { document_name: docName } : {}
        );
        
        clearInterval(progressInterval);
        Elements.progressFill.style.width = '100%';
        Elements.progressText.textContent = 'اكتمل!';
        
        if (response.ok && response.data.success) {
            showToast(`تم رفع الوثيقة بنجاح! (${response.data.chunks_created} جزء)`, 'success');
            resetUploadForm();
            loadDocuments();
            checkSystemStatus();
        } else {
            showToast(response.data.error_message || 'فشل الرفع', 'error');
        }
    } catch (error) {
        clearInterval(progressInterval);
        showToast('خطأ في رفع الملف', 'error');
    } finally {
        setTimeout(() => {
            Elements.uploadSubmitBtn.classList.remove('loading');
            Elements.uploadProgress.classList.remove('show');
            Elements.progressFill.style.width = '0%';
        }, 1000);
    }
}

function resetUploadForm() {
    Elements.fileInput.value = '';
    Elements.docName.value = '';
    Elements.dropZone.classList.remove('has-file');
    Elements.selectedFileName.textContent = '';
    Elements.uploadSubmitBtn.disabled = true;
}

async function initializeSystem() {
    Elements.initBtn.disabled = true;
    Elements.initBtn.innerHTML = '<span>جاري التهيئة...</span>';
    
    try {
        const response = await API.post('/api/documents/initialize', {});
        
        if (response.ok && response.data.success) {
            showToast('تم تهيئة النظام بنجاح!', 'success');
            loadDocuments();
            checkSystemStatus();
        } else {
            showToast(response.data.error_message || 'فشل التهيئة', 'error');
        }
    } catch (error) {
        showToast('خطأ في تهيئة النظام', 'error');
    } finally {
        Elements.initBtn.disabled = false;
        Elements.initBtn.innerHTML = '<span>تهيئة النظام</span>';
    }
}

// ==================== Settings ====================

function loadSystemInfo() {
    checkSystemStatus();
}

// ==================== Event Listeners ====================

function initEventListeners() {
    // Navigation
    Elements.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchSection(item.dataset.section);
        });
    });
    
    // Mobile menu
    Elements.mobileMenuBtn.addEventListener('click', () => {
        Elements.sidebar.classList.toggle('open');
    });
    
    Elements.sidebarToggle.addEventListener('click', () => {
        Elements.sidebar.classList.toggle('open');
    });
    
    // Theme
    Elements.themeToggle.addEventListener('click', () => {
        const newTheme = AppState.theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    
    Elements.themeButtons.forEach(btn => {
        btn.addEventListener('click', () => setTheme(btn.dataset.theme));
    });
    
    // Chat form
    Elements.chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = Elements.queryInput.value.trim();
        if (query) {
            sendQuery(query);
            Elements.queryInput.value = '';
            autoResizeTextarea(Elements.queryInput);
        }
    });
    
    // Auto-resize textarea
    Elements.queryInput.addEventListener('input', () => {
        autoResizeTextarea(Elements.queryInput);
    });
    
    // Example chips
    Elements.exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.dataset.query;
            Elements.queryInput.value = query;
            Elements.queryInput.focus();
        });
    });
    
    // Upload - Drop zone
    Elements.dropZone.addEventListener('click', () => Elements.fileInput.click());
    
    Elements.dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        Elements.dropZone.classList.add('dragover');
    });
    
    Elements.dropZone.addEventListener('dragleave', () => {
        Elements.dropZone.classList.remove('dragover');
    });
    
    Elements.dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        Elements.dropZone.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files);
    });
    
    Elements.fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });
    
    Elements.removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUploadForm();
    });
    
    Elements.uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const file = Elements.fileInput.files[0];
        if (file) uploadDocument(file);
    });
    
    Elements.initBtn.addEventListener('click', initializeSystem);
    
    // History
    Elements.clearHistoryBtn.addEventListener('click', clearHistory);
    
    // Settings
    Elements.defaultSources.addEventListener('change', (e) => {
        AppState.settings.numSources = parseInt(e.target.value);
        Elements.numSources.value = e.target.value;
    });
    
    Elements.autoShowSources.addEventListener('change', (e) => {
        AppState.settings.showSources = e.target.checked;
        Elements.showSources.checked = e.target.checked;
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to send
        if (e.ctrlKey && e.key === 'Enter' && document.activeElement === Elements.queryInput) {
            e.preventDefault();
            Elements.chatForm.dispatchEvent(new Event('submit'));
        }
        
        // Escape to close sidebar on mobile
        if (e.key === 'Escape') {
            Elements.sidebar.classList.remove('open');
        }
    });
    
    // Click outside sidebar to close (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024) {
            if (!Elements.sidebar.contains(e.target) && 
                !Elements.mobileMenuBtn.contains(e.target)) {
                Elements.sidebar.classList.remove('open');
            }
        }
    });
}

function handleFileSelect(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    
    if (file.type !== 'application/pdf') {
        showToast('يجب أن يكون الملف بصيغة PDF', 'warning');
        return;
    }
    
    Elements.dropZone.classList.add('has-file');
    Elements.selectedFileName.textContent = file.name;
    Elements.uploadSubmitBtn.disabled = false;
    
    // Copy file to input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    Elements.fileInput.files = dataTransfer.files;
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// ==================== Initialize ====================

async function init() {
    // Set theme
    setTheme(AppState.theme);
    
    // Initialize event listeners
    initEventListeners();
    
    // Check system status
    await checkSystemStatus();
    
    // Hide loading overlay
    setTimeout(() => {
        Elements.loadingOverlay.classList.add('hidden');
    }, 500);
    
    // Start periodic status check
    setInterval(checkSystemStatus, 30000);
}

// Start app when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Make toggleSources globally available
window.toggleSources = toggleSources;
