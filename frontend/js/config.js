// ========================================
// CONFIGURATION
// ========================================

const CONFIG = {
    // Backend API URL - Render deploy hone ke baad update karna
    API_URL: "https://your-backend.onrender.com",
    
    // Site Info
    SITE_NAME: "LootBazaar News",
    SITE_TAGLINE: "Latest Hindi News",
    
    // Pagination
    ARTICLES_PER_PAGE: 10,
    
    // Categories
    CATEGORIES: {
        "technology": { name: "Technology", icon: "💻" },
        "sports": { name: "Sports", icon: "🏏" },
        "business": { name: "Business", icon: "💼" },
        "entertainment": { name: "Entertainment", icon: "🎬" },
        "education": { name: "Education", icon: "📚" },
        "india": { name: "India", icon: "🇮🇳" },
        "world": { name: "World", icon: "🌍" },
        "general": { name: "General", icon: "📰" }
    },

    // Default Image
    DEFAULT_IMAGE: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
};

// Format date to Hindi
function formatDate(dateStr) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return date.toLocaleDateString('hi-IN', options);
}

// Format number
function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num;
}

// Get category info
function getCategoryInfo(slug) {
    return CONFIG.CATEGORIES[slug] || { name: slug, icon: "📰" };
}

// Show toast notification
function showToast(message, type = "info") {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'error' ? '#e53e3e' : '#48bb78'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 9999;
        font-size: 0.9rem;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Truncate text
function truncateText(text, maxLength) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
}

// Theme toggle
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.innerHTML = theme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

// Menu toggle
function initMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navbar = document.getElementById('navbar');
    if (menuToggle && navbar) {
        menuToggle.addEventListener('click', () => {
            navbar.classList.toggle('open');
        });
    }
}

// Search function
function searchNews() {
    const query = document.getElementById('searchInput')?.value?.trim();
    if (query && query.length >= 2) {
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    } else {
        showToast("Kam se kam 2 characters likhein", "error");
    }
}

// Enter key search
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMenu();
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchNews();
        });
    }

    // Theme toggle button
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
});
