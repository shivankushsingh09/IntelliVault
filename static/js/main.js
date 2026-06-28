/**
 * IntelliVault Main JavaScript
 * Client-side functionality and utilities
 */

// API Base Configuration
const API = {
    BASE_URL: '/api',
    
    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    /**
     * GET request
     */
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    /**
     * POST request
     */
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * PUT request
     */
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * DELETE request
     */
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
};

// Utility Functions
const Utils = {
    /**
     * Format date to readable format
     */
    formatDate(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        };
        
        return date.toLocaleDateString('en-US', options);
    },
    
    /**
     * Show notification
     */
    notify(message, type = 'info', duration = 3000) {
        const alertClass = `alert-${type}`;
        const alertHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertContainer = document.createElement('div');
        alertContainer.innerHTML = alertHTML;
        
        const mainContent = document.querySelector('main');
        mainContent.insertBefore(alertContainer.firstChild, mainContent.firstChild);
        
        if (duration > 0) {
            setTimeout(() => {
                const alert = mainContent.querySelector('.alert');
                if (alert) alert.remove();
            }, duration);
        }
    },
    
    /**
     * Show loading spinner
     */
    showLoader(element) {
        element.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner"></div>
                <p class="mt-3 text-muted">Loading...</p>
            </div>
        `;
    },
    
    /**
     * Truncate text
     */
    truncate(text, length = 100) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    },
    
    /**
     * Copy to clipboard
     */
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.notify('Copied to clipboard!', 'success', 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    },
    
    /**
     * Confirm action
     */
    confirm(message) {
        return window.confirm(message);
    },
    
    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
};

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    // Setup Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Setup Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Setup theme toggle
    setupThemeToggle();

    // Setup search form
    setupSearch();
    
    // Setup auto-save
    setupAutoSave();
    
    // Setup settings page
    setupSettingsPage();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
}

/**
 * Setup settings page functionality
 */
function setupSettingsPage() {
    const settingsForm = document.getElementById('settingsForm');
    if (!settingsForm) return;

    const themeSelect = document.getElementById('themeSelect');
    const notificationsToggle = document.getElementById('notificationsToggle');
    const resetPreferencesBtn = document.getElementById('resetPreferencesBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');

    const updateThemeView = (theme) => {
        const effectiveTheme = theme === 'system'
            ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : theme;

        document.documentElement.setAttribute('data-theme', effectiveTheme);
        document.documentElement.setAttribute('data-bs-theme', effectiveTheme);
        localStorage.setItem('theme', theme);
    };

    themeSelect?.addEventListener('change', (event) => {
        updateThemeView(event.target.value);
    });

    settingsForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(settingsForm);
        const payload = {
            full_name: formData.get('full_name') || null,
            bio: formData.get('bio') || null,
            theme: formData.get('theme') || 'light',
            notifications_enabled: formData.get('notifications_enabled') === 'on',
        };

        const currentPassword = formData.get('current_password');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');

        try {
            await API.put('/profile', payload);

            if (currentPassword || newPassword || confirmPassword) {
                if (!currentPassword || !newPassword || !confirmPassword) {
                    throw new Error('Please fill in all password fields to change your password.');
                }
                if (newPassword.length < 8) {
                    throw new Error('New password must be at least 8 characters.');
                }
                if (newPassword !== confirmPassword) {
                    throw new Error('New password and confirmation do not match.');
                }

                await API.post('/profile/password', {
                    old_password: currentPassword,
                    new_password: newPassword,
                });
            }

            updateThemeView(payload.theme);
            Utils.notify('Settings saved successfully.', 'success');
        } catch (error) {
            Utils.notify(error.message || 'Failed to save settings.', 'danger');
        }
    });

    resetPreferencesBtn?.addEventListener('click', async () => {
        if (!Utils.confirm('Reset theme and notification preferences to defaults?')) return;

        try {
            const response = await API.post('/profile/reset', {});
            themeSelect.value = response.theme || 'light';
            notificationsToggle.checked = response.notifications_enabled;
            updateThemeView(response.theme || 'light');
            Utils.notify('Preferences reset to defaults.', 'success');
        } catch (error) {
            Utils.notify('Failed to reset preferences.', 'danger');
        }
    });

    deleteAccountBtn?.addEventListener('click', async () => {
        if (!Utils.confirm('This will permanently delete your account. Continue?')) return;

        try {
            await API.delete('/profile/delete');
            window.location.href = '/auth/login';
        } catch (error) {
            Utils.notify('Failed to delete account.', 'danger');
        }
    });
}

/**
 * Setup theme toggle functionality
 */
function setupThemeToggle() {
    const toggleBtn = document.getElementById('themeToggle');
    if (!toggleBtn) return;
    
    const updateIcon = (theme) => {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
            } else {
                icon.className = 'fas fa-moon';
            }
        }
    };

    // Set initial icon based on current theme
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    updateIcon(currentTheme);

    toggleBtn.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = theme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', nextTheme);
        document.documentElement.setAttribute('data-bs-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
        updateIcon(nextTheme);
    });
}

/**
 * Setup search functionality
 */
function setupSearch() {
    const searchForm = document.querySelector('form[action*="search"]');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('input[name="q"]');
    if (!searchInput) return;
    
    // Add search suggestions (optional)
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) return;
        
        // You can add autocomplete here
    });
}

/**
 * Setup auto-save for forms
 */
function setupAutoSave() {
    const forms = document.querySelectorAll('[data-autosave]');
    forms.forEach(form => {
        let timeout;
        form.addEventListener('change', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-save logic here
            }, 2000);
        });
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            // Save logic here
        }
        
        // Ctrl/Cmd + / to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) searchInput.focus();
        }
    });
}

/**
 * Delete item with confirmation
 */
async function deleteItem(url, itemName = 'item') {
    if (!Utils.confirm(`Are you sure you want to delete this ${itemName}?`)) {
        return;
    }
    
    try {
        await API.delete(url);
        Utils.notify('Item deleted successfully', 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        Utils.notify(`Error deleting ${itemName}: ${error.message}`, 'danger');
    }
}

/**
 * Pin/Unpin item
 */
async function togglePin(url, element) {
    try {
        const data = await API.put(url, { is_pinned: !element.classList.contains('pinned') });
        element.classList.toggle('pinned');
        Utils.notify('Updated successfully', 'success', 2000);
    } catch (error) {
        Utils.notify(`Error: ${error.message}`, 'danger');
    }
}

/**
 * Archive item
 */
async function archiveItem(url, itemName = 'item') {
    try {
        await API.put(url, { is_archived: true });
        Utils.notify(`${itemName} archived successfully`, 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        Utils.notify(`Error archiving ${itemName}: ${error.message}`, 'danger');
    }
}

/**
 * Export data to JSON
 */
function exportToJSON(data, filename = 'export.json') {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Load dashboard stats
 */
async function loadDashboardStats() {
    try {
        const stats = await API.get('/dashboard/stats');
        updateStatsUI(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Update stats UI
 */
function updateStatsUI(stats) {
    // Update statistics cards
    const statsElements = {
        'stat-documents': stats.documents,
        'stat-notes': stats.notes,
        'stat-quizzes': stats.quizzes,
        'stat-chats': stats.chat_sessions,
    };
    
    Object.entries(statsElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

/**
 * Render notes list
 */
function renderNotesList(notes, container) {
    if (!notes || notes.length === 0) {
        container.innerHTML = '<p class="text-muted">No notes found.</p>';
        return;
    }
    
    const html = notes.map(note => `
        <tr>
            <td>${Utils.escapeHtml(note.title)}</td>
            <td><span class="badge bg-info">${note.note_type}</span></td>
            <td>${Utils.formatDate(note.created_at)}</td>
            <td>
                <a href="/notes/${note.id}" class="btn btn-sm btn-outline-primary">
                    View
                </a>
            </td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${html}
            </tbody>
        </table>
    `;
}

// Export for use in other modules
window.API = API;
window.Utils = Utils;
