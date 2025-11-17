// Configuration
const API_URL = 'http://127.0.0.1:8000';
let selectedFile = null;
let chatHistory = [];

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const messagesArea = document.getElementById('messagesArea');
const loadingSpinner = document.getElementById('loadingSpinner');
const chatHistoryContainer = document.getElementById('chatHistory');

// Upload Box Event Listeners
uploadBox.addEventListener('click', () => fileInput.click());

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#0d6efd';
    uploadBox.style.backgroundColor = 'rgba(13, 110, 253, 0.15)';
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#0d6efd';
    uploadBox.style.backgroundColor = 'rgba(13, 110, 253, 0.05)';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle File Selection
function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        showStatus('خطأ: يرجى اختيار ملف PDF', 'error');
        return;
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB limit
        showStatus('خطأ: حجم الملف كبير جداً (حد أقصى 50MB)', 'error');
        return;
    }

    selectedFile = file;
    uploadBox.innerHTML = `
        <i class="bi bi-check-circle" style="color: #28a745; font-size: 2rem;"></i>
        <p><strong>${file.name}</strong></p>
        <p class="text-muted small">جاهز للرفع</p>
    `;
    uploadBtn.disabled = false;
}

// Upload File
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>جاري الرفع...';
    showStatus('جاري رفع الملف...', 'info');

    try {
        const response = await fetch(`${API_URL}/upload_pdf/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            showStatus(`✓ تم تحضير الملف بنجاح!`, 'success');
            enableChat();
            clearMessages();
            addMessageToUI('مساعد', 'تم تحميل الدستور بنجاح! الآن يمكنك طرح أسئلتك.', 'assistant');
        } else {
            const error = await response.json();
            showStatus(`خطأ: ${error.detail || 'فشل الرفع'}`, 'error');
        }
    } catch (error) {
        showStatus(`خطأ: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="bi bi-upload"></i> رفع وتحضير';
    }
});

// Enable Chat
function enableChat() {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    questionInput.focus();
}

// Send Message
async function sendMessage() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message to UI
    addMessageToUI('أنت', question, 'user');
    addToHistory(question);

    questionInput.value = '';
    showLoading(true);
    
    // Force scroll to bottom
    scrollToBottom();

    try {
        const response = await fetch(`${API_URL}/chat?query_request=${encodeURIComponent(question)}`);

        if (response.ok) {
            const data = await response.json();
            const answer = data.response || 'لم أستطع الحصول على إجابة';
            addMessageToUI('مساعد', answer, 'assistant');
        } else {
            const error = await response.json();
            addMessageToUI('مساعد', `خطأ: ${error.detail || 'حدث خطأ في المعالجة'}`, 'assistant');
        }
    } catch (error) {
        addMessageToUI('مساعد', `خطأ في الاتصال: ${error.message}`, 'assistant');
    } finally {
        showLoading(false);
        scrollToBottom();
    }
}

// Scroll to bottom
function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Send Button Click
sendBtn.addEventListener('click', sendMessage);

// Enter Key
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Add Message to UI
function addMessageToUI(sender, text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const time = new Date().toLocaleTimeString('ar-EG', {
        hour: '2-digit',
        minute: '2-digit'
    });

    // Format text with enhanced parsing for lists and formatting
    let formattedText = formatMessageText(text);

    messageDiv.innerHTML = `
        <div>
            <div class="message-content">
                <strong>${sender}:</strong><br>
                <div class="message-text">${formattedText}</div>
                <span class="message-time">${time}</span>
            </div>
        </div>
    `;

    messagesArea.appendChild(messageDiv);
    
    // Scroll to bottom - use requestAnimationFrame for smooth rendering
    requestAnimationFrame(() => {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    });
}

// Format message text with lists and bold text
function formatMessageText(text) {
    let formatted = escapeHtml(text);
    
    // Convert numbered lists (1. 2. 3. etc)
    formatted = formatted.replace(/(\d+)\.\s+/g, '<li>');
    
    // Wrap consecutive list items in <ol>
    formatted = formatted.replace(/(<li>.*?)<\/div>/s, (match) => {
        if (match.includes('<li>')) {
            const items = match.match(/<li>[^<]*<br>/g) || [];
            if (items.length > 1) {
                return '<ol>' + match.replace(/<li>/g, '<li>').replace(/<\/div>/, '</ol></div>');
            }
        }
        return match;
    });
    
    return formatted;
}

// Add to Chat History
function addToHistory(question) {
    chatHistory.unshift(question);
    if (chatHistory.length > 10) chatHistory.pop();
    updateHistoryUI();
}

// Update History UI
function updateHistoryUI() {
    if (chatHistory.length === 0) {
        chatHistoryContainer.innerHTML = '<p class="text-muted text-center small">لم تبدأ أي محادثة بعد</p>';
        return;
    }

    chatHistoryContainer.innerHTML = chatHistory.map((item, index) => `
        <div class="history-item" title="${item}" onclick="restoreQuestion('${escapeHtml(item)}')">
            <i class="bi bi-chat-left-text"></i>
            ${item.substring(0, 30)}${item.length > 30 ? '...' : ''}
        </div>
    `).join('');
}

// Restore Question from History
function restoreQuestion(question) {
    questionInput.value = question;
    questionInput.focus();
}

// Show Status Message
function showStatus(message, type) {
    uploadStatus.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'error' : type === 'success' ? 'success' : 'info'}">
            ${message}
        </div>
    `;

    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            uploadStatus.innerHTML = '';
        }, 5000);
    }
}

// Clear Messages
function clearMessages() {
    messagesArea.innerHTML = `
        <div class="empty-state">
            <i class="bi bi-chat-dots"></i>
            <p class="mt-3">ابدأ بطرح سؤالك عن الدستور المصري</p>
            <small class="d-block mt-2">تأكد من رفع ملف الدستور أولاً</small>
        </div>
    `;
}

// Show/Hide Loading Spinner
function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('d-none');
    } else {
        loadingSpinner.classList.add('d-none');
    }
}

// Escape HTML and parse markdown-like formatting
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    let escaped = div.innerHTML;
    
    // Preserve line breaks
    escaped = escaped.replace(/\n/g, '<br>');
    
    // Convert **text** to <strong>text</strong>
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return escaped;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('تطبيق دستور مصر الذكي جاهز');
    showStatus('اختر ملف الدستور PDF وارفعه لبدء الاستخدام', 'info');
});
