const CONFIG = {
    API_URL: "https://news-affiliate-platform.onrender.com",
    
    SITE_NAME: "IndiaXpress",
    SITE_TAGLINE: "India's Premier News Platform",
    WHATSAPP_CHANNEL: "https://www.whatsapp.com/channel/0029VbCy92nBadmau8nw0v3j",
    
    ARTICLES_PER_PAGE: 10,
    
    // 6 Languages
    LANGUAGES: {
        "en": { name: "English", native: "English", flag: "🇬🇧" },
        "hi": { name: "Hindi", native: "हिंदी", flag: "🇮🇳" },
        "te": { name: "Telugu", native: "తెలుగు", flag: "🇮🇳" },
        "ta": { name: "Tamil", native: "தமிழ்", flag: "🇮🇳" },
        "bn": { name: "Bengali", native: "বাংলা", flag: "🇮🇳" },
        "mr": { name: "Marathi", native: "मराठी", flag: "🇮🇳" }
    },

    DEFAULT_LANGUAGE: "en",

    // UI Translations
    UI_TEXT: {
        "en": {
            search_placeholder: "Search news...",
            breaking: "Breaking",
            trending: "Trending Posts",
            categories: "Categories",
            top_deals: "Top Deals",
            buy_now: "Buy on Amazon",
            read_more: "Read More",
            home: "Home",
            about: "About",
            contact: "Contact",
            privacy: "Privacy Policy",
            disclaimer: "Disclaimer",
            latest_news: "Latest News",
            featured: "Featured",
            views: "views",
            words: "words",
            related: "Related Articles",
            share: "Share",
            faq: "Frequently Asked Questions",
            conclusion: "Conclusion",
            change_language: "Change Language",
            article_language: "Article Language"
        },
        "hi": {
            search_placeholder: "समाचार खोजें...",
            breaking: "ब्रेकिंग",
            trending: "ट्रेंडिंग",
            categories: "श्रेणियाँ",
            top_deals: "टॉप डील्स",
            buy_now: "Amazon पर खरीदें",
            read_more: "और पढ़ें",
            home: "होम",
            about: "हमारे बारे में",
            contact: "संपर्क",
            privacy: "गोपनीयता नीति",
            disclaimer: "अस्वीकरण",
            latest_news: "ताज़ा खबर",
            featured: "फीचर्ड",
            views: "व्यूज़",
            words: "शब्द",
            related: "संबंधित लेख",
            share: "शेयर करें",
            faq: "अक्सर पूछे जाने वाले प्रश्न",
            conclusion: "निष्कर्ष",
            change_language: "भाषा बदलें",
            article_language: "लेख की भाषा"
        },
        "te": {
            search_placeholder: "వార్తలు వెతకండి...",
            breaking: "బ్రేకింగ్",
            trending: "ట్రెండింగ్",
            categories: "వర్గాలు",
            top_deals: "టాప్ డీల్స్",
            buy_now: "Amazon లో కొనండి",
            read_more: "మరింత చదవండి",
            home: "హోమ్",
            about: "మా గురించి",
            contact: "సంప్రదించండి",
            privacy: "గోప్యతా విధానం",
            disclaimer: "నిరాకరణ",
            latest_news: "తాజా వార్తలు",
            featured: "ఫీచర్డ్",
            views: "వ్యూస్",
            words: "పదాలు",
            related: "సంబంధిత వ్యాసాలు",
            share: "షేర్ చేయండి",
            faq: "తరచుగా అడిగే ప్రశ్నలు",
            conclusion: "ముగింపు",
            change_language: "భాష మార్చండి",
            article_language: "వ్యాస భాష"
        },
        "ta": {
            search_placeholder: "செய்திகளை தேடுங்கள்...",
            breaking: "முக்கிய செய்தி",
            trending: "டிரெண்டிங்",
            categories: "வகைகள்",
            top_deals: "சிறந்த டீல்கள்",
            buy_now: "Amazon இல் வாங்கவும்",
            read_more: "மேலும் படிக்கவும்",
            home: "முகப்பு",
            about: "எங்களைப் பற்றி",
            contact: "தொடர்பு",
            privacy: "தனியுரிமை கொள்கை",
            disclaimer: "மறுப்பு",
            latest_news: "சமீபத்திய செய்திகள்",
            featured: "சிறப்பு",
            views: "பார்வைகள்",
            words: "வார்த்தைகள்",
            related: "தொடர்புடைய கட்டுரைகள்",
            share: "பகிரவும்",
            faq: "அடிக்கடி கேட்கப்படும் கேள்விகள்",
            conclusion: "முடிவு",
            change_language: "மொழியை மாற்றவும்",
            article_language: "கட்டுரை மொழி"
        },
        "bn": {
            search_placeholder: "খবর খুঁজুন...",
            breaking: "ব্রেকিং",
            trending: "ট্রেন্ডিং",
            categories: "বিভাগ",
            top_deals: "টপ ডিলস",
            buy_now: "Amazon এ কিনুন",
            read_more: "আরও পড়ুন",
            home: "হোম",
            about: "আমাদের সম্পর্কে",
            contact: "যোগাযোগ",
            privacy: "গোপনীয়তা নীতি",
            disclaimer: "দাবিত্যাগ",
            latest_news: "সর্বশেষ সংবাদ",
            featured: "বৈশিষ্ট্য",
            views: "ভিউ",
            words: "শব্দ",
            related: "সম্পর্কিত নিবন্ধ",
            share: "শেয়ার করুন",
            faq: "সচরাচর জিজ্ঞাসিত প্রশ্ন",
            conclusion: "উপসংহার",
            change_language: "ভাষা পরিবর্তন করুন",
            article_language: "নিবন্ধের ভাষা"
        },
        "mr": {
            search_placeholder: "बातम्या शोधा...",
            breaking: "ब्रेकिंग",
            trending: "ट्रेंडिंग",
            categories: "श्रेणी",
            top_deals: "टॉप डील्स",
            buy_now: "Amazon वर खरेदी करा",
            read_more: "अधिक वाचा",
            home: "मुख्यपृष्ठ",
            about: "आमच्याबद्दल",
            contact: "संपर्क",
            privacy: "गोपनीयता धोरण",
            disclaimer: "अस्वीकरण",
            latest_news: "ताज्या बातम्या",
            featured: "वैशिष्ट्यीकृत",
            views: "व्ह्यूज",
            words: "शब्द",
            related: "संबंधित लेख",
            share: "शेअर करा",
            faq: "वारंवार विचारले जाणारे प्रश्न",
            conclusion: "निष्कर्ष",
            change_language: "भाषा बदला",
            article_language: "लेखाची भाषा"
        }
    },

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

    DEFAULT_IMAGE: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
    AMAZON_TAG: "sk200709-21"
};

// Current language
let currentLang = localStorage.getItem('site_language') || CONFIG.DEFAULT_LANGUAGE;
let currentArticleLang = localStorage.getItem('article_language') || CONFIG.DEFAULT_LANGUAGE;

// Get UI text
function t(key) {
    const lang = CONFIG.UI_TEXT[currentLang] || CONFIG.UI_TEXT['en'];
    return lang[key] || CONFIG.UI_TEXT['en'][key] || key;
}

// Set site language
function setSiteLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('site_language', lang);
    updateUILanguage();
}

// Set article language only
function setArticleLanguage(lang) {
    currentArticleLang = lang;
    localStorage.setItem('article_language', lang);
}

// Update UI text
function updateUILanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = t(key);
    });
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.placeholder = t('search_placeholder');
    }
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    const locales = {
        'en': 'en-IN', 'hi': 'hi-IN', 'te': 'te-IN',
        'ta': 'ta-IN', 'bn': 'bn-IN', 'mr': 'mr-IN'
    };
    return date.toLocaleDateString(locales[currentLang] || 'en-IN', {
        year: 'numeric', month: 'long', day: 'numeric'
    });
}

function formatNumber(num) {
    if (!num) return 0;
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num;
}

function getCategoryInfo(slug) {
    return CONFIG.CATEGORIES[slug] || { name: slug, icon: "📰" };
}

function showToast(message, type = "info") {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        background: ${type === 'error' ? '#e53e3e' : '#48bb78'};
        color: white; padding: 12px 20px; border-radius: 8px;
        z-index: 9999; font-size: 0.9rem;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function truncateText(text, maxLength) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
}

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

function initMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navbar = document.getElementById('navbar');
    if (menuToggle && navbar) {
        menuToggle.addEventListener('click', () => {
            navbar.classList.toggle('open');
        });
    }
}

function searchNews() {
    const query = document.getElementById('searchInput')?.value?.trim();
    if (query && query.length >= 2) {
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    } else {
        showToast('Please enter at least 2 characters', 'error');
    }
}

// Language Selector HTML
function createLanguageSelector(type = 'site') {
    const langs = CONFIG.LANGUAGES;
    const current = type === 'site' ? currentLang : currentArticleLang;

    return `
        <div class="lang-selector">
            <button class="lang-btn" onclick="toggleLangDropdown('${type}')">
                ${langs[current].flag} ${langs[current].native}
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="lang-dropdown" id="langDropdown_${type}">
                ${Object.entries(langs).map(([code, lang]) => `
                    <div class="lang-option ${code === current ? 'active' : ''}"
                         onclick="${type === 'site' ? `setSiteLanguage('${code}')` : `setArticleLanguage('${code}')`};
                                  toggleLangDropdown('${type}')">
                        ${lang.flag} ${lang.native}
                        <small>${lang.name}</small>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function toggleLangDropdown(type) {
    const dropdown = document.getElementById(`langDropdown_${type}`);
    if (dropdown) dropdown.classList.toggle('show');
}

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('.lang-selector')) {
        document.querySelectorAll('.lang-dropdown').forEach(d => {
            d.classList.remove('show');
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMenu();
    updateUILanguage();

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchNews();
        });
    }

    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
});
