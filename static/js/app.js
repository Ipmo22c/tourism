// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const quickActionButtons = document.querySelectorAll('.quick-action-btn');
const themeToggle = document.getElementById('themeToggle');
const helpButton = document.getElementById('helpButton');
const helpModal = document.getElementById('helpModal');
const helpModalClose = document.getElementById('helpModalClose');

// API endpoint
const API_URL = '/api/query';

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    themeToggle.innerHTML = theme === 'dark' ? '<span class="theme-icon">☀️</span>' : '<span class="theme-icon">🌙</span>';
}

// Help Modal
helpButton.addEventListener('click', () => {
    helpModal.classList.add('active');
});

helpModalClose.addEventListener('click', () => {
    helpModal.classList.remove('active');
});

helpModal.addEventListener('click', (e) => {
    if (e.target === helpModal) {
        helpModal.classList.remove('active');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    userInput.focus();
    
    // Event listeners
    sendButton.addEventListener('click', handleSend);
    themeToggle.addEventListener('click', toggleTheme);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Quick action buttons
    quickActionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            userInput.value = query;
            handleSend();
        });
    });
});

// Handle send message
async function handleSend() {
    const query = userInput.value.trim();
    
    if (!query) {
        return;
    }
    
    // Add user message to chat
    addMessage(query, 'user');
    
    // Clear input
    userInput.value = '';
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        removeLoadingMessage(loadingId);
        
        if (data.success) {
            addMessage(data.response, 'bot');
        } else {
            addMessage(`Error: ${data.response}`, 'bot', true);
        }
        
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessage('Sorry, there was an error processing your request. Please try again.', 'bot', true);
        console.error('Error:', error);
    } finally {
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessage(text, type, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const lowerText = text.toLowerCase();
    if (isError || lowerText.includes("don't know") || lowerText.includes("unable") || lowerText.includes("error") || lowerText.includes("unfortunately") || lowerText.includes("sorry")) {
        contentDiv.classList.add('error');
    } else if (lowerText.includes("success") || lowerText.includes("found")) {
        contentDiv.classList.add('success');
    }
    
    const formattedText = formatMessage(text);
    contentDiv.innerHTML = formattedText;
    
    // Make place cards clickable (but not in greeting messages)
    // Check if this is the initial greeting by looking for specific text
    const isGreeting = lowerText.includes("hey there") || 
                       lowerText.includes("ready to explore") || 
                       lowerText.includes("where would you like to explore") ||
                       lowerText.includes("i can help you with");
    
    if (!isGreeting) {
        makePlaceCardsClickable(contentDiv);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Format message text
function formatMessage(text) {
    let formatted = text.split('\n').map(line => {
        line = line.trim();
        if (!line) return '';
        
        // Check if line is a list item (place name)
        if (line.startsWith('- ')) {
            const placeName = line.substring(2);
            return `<div class="place-card"><span class="place-name">${escapeHtml(placeName)}</span><div class="place-card-details"></div></div>`;
        }
        
        // Numbered list
        const numberedMatch = line.match(/^(\d+)\.\s+(.+)$/);
        if (numberedMatch) {
            return `<li>${escapeHtml(numberedMatch[2])}</li>`;
        }
        
        return `<p>${escapeHtml(line)}</p>`;
    }).join('');
    
    // Wrap consecutive list items in <ul>
    formatted = formatted.replace(/(<li>.*?<\/li>)+/g, (match) => {
        return `<ul>${match}</ul>`;
    });
    
    return formatted;
}

// Make place cards clickable
function makePlaceCardsClickable(container) {
    const placeCards = container.querySelectorAll('.place-card');
    placeCards.forEach(card => {
        card.addEventListener('click', async () => {
            const placeName = card.querySelector('.place-name').textContent;
            const detailsDiv = card.querySelector('.place-card-details');
            
            if (card.classList.contains('expanded')) {
                card.classList.remove('expanded');
                detailsDiv.innerHTML = '';
            } else {
                card.classList.add('expanded');
                detailsDiv.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.85rem;">Loading details...</p>';
                
                try {
                    const response = await fetch(API_URL, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: `tell me about ${placeName}` })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        detailsDiv.innerHTML = formatMessage(data.response);
                    } else {
                        detailsDiv.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.85rem;">Details not available</p>';
                    }
                } catch (error) {
                    detailsDiv.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.85rem;">Error loading details</p>';
                }
            }
        });
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add loading message
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'loading-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="loading"></div>';
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return 'loading-message';
}

// Remove loading message
function removeLoadingMessage(id) {
    const loadingMessage = document.getElementById(id);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}
