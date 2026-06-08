// ========================================
// MAIN.JS - Home Page (Updated with Settings Menu & Language Selector)
// ========================================

let currentPage = 1;
let currentCategory = 'all';
let totalPages = 1;

// ========================================
// FETCH ARTICLES
// ========================================

async function fetchArticles(page = 1, category = 'all') {
    try {
        let url = `${CONFIG.API_URL}/api/articles?page=${page}&limit=${CONFIG.ARTICLES_PER_PAGE}`;
        if (category !== 'all') {
            url += `&category=${category}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            totalPages = data.pages;
            renderArticles(data.articles);
            renderPagination(data.page, data.pages);

            // Set featured article
            if (page === 1 && data.articles.length > 0) {
                renderFeaturedArticle(data.articles[0]);
            }
        }
    } catch (error) {
        console.error('Error fetching articles:', error);
        showError('Articles load nahi ho sake!');
    }
}


// ========================================
// RENDER FEATURED ARTICLE
// ========================================

function renderFeaturedArticle(article) {
    const container = document.getElementById('featuredArticle');
    if (!container) return;

    const image = article.featured_image || CONFIG.DEFAULT_IMAGE;
    const date = formatDate(article.published_at);

    container.innerHTML = `
        <div class="featured-card" onclick="openArticle('${article.slug}')">
            <img src="${image}" 
                 alt="${article.title}"
                 onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
            <div class="featured-overlay">
                <span class="featured-category">
                    ${getCategoryIcon(article.category_id)} Featured
                </span>
                <h2 class="featured-title">${article.title}</h2>
                <div class="featured-meta">
                    <span>📅 ${date}</span>
                    <span>👁️ ${formatNumber(article.views)} views</span>
                    <span>📖 ${article.word_count} words</span>
                </div>
            </div>
        </div>
    `;
}


// ========================================
// RENDER ARTICLES GRID
// ========================================

function renderArticles(articles) {
    const grid = document.getElementById('articlesGrid');
    if (!grid) return;

    if (articles.length === 0) {
        grid.innerHTML = `
            <div class="no-articles">
                <p>😔 Koi article nahi mila!</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = articles.map(article => {
        const image = article.featured_image || CONFIG.DEFAULT_IMAGE;
        const date = formatDate(article.published_at);
        const summary = truncateText(article.summary, 100);

        return `
            <div class="article-card" onclick="openArticle('${article.slug}')">
                <img class="article-card-image" 
                     src="${image}" 
                     alt="${article.title}"
                     loading="lazy"
                     onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
                <div class="article-card-content">
                    <span class="article-category-tag">
                        📰 News
                    </span>
                    <h3 class="article-card-title">${article.title}</h3>
                    <p class="article-card-summary">${summary}</p>
                    <div class="article-card-meta">
                        <span>📅 ${date}</span>
                        <span class="article-views">
                            👁️ ${formatNumber(article.views)}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}


// ========================================
// RENDER PAGINATION
// ========================================

function renderPagination(current, total) {
    const container = document.getElementById('pagination');
    if (!container || total <= 1) return;

    let buttons = '';

    // Previous button
    if (current > 1) {
        buttons += `
            <button class="page-btn" onclick="goToPage(${current - 1})">
                ← Pehle
            </button>
        `;
    }

    // Page numbers
    for (let i = 1; i <= total; i++) {
        if (
            i === 1 || 
            i === total || 
            (i >= current - 2 && i <= current + 2)
        ) {
            buttons += `
                <button class="page-btn ${i === current ? 'active' : ''}" 
                        onclick="goToPage(${i})">
                    ${i}
                </button>
            `;
        } else if (i === current - 3 || i === current + 3) {
            buttons += `<span class="page-dots">...</span>`;
        }
    }

    // Next button
    if (current < total) {
        buttons += `
            <button class="page-btn" onclick="goToPage(${current + 1})">
                Agle →
            </button>
        `;
    }

    container.innerHTML = buttons;
}


// ========================================
// FETCH TRENDING
// ========================================

async function fetchTrending() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/trending`);
        const data = await response.json();

        if (data.success) {
            renderTrending(data.articles);
        }
    } catch (error) {
        console.error('Trending fetch error:', error);
    }
}

function renderTrending(articles) {
    const container = document.getElementById('trendingPosts');
    if (!container) return;

    container.innerHTML = articles.map((article, index) => `
        <div class="trending-item" onclick="openArticle('${article.slug}')">
            <span class="trending-number">${index + 1}</span>
            <div>
                <div class="trending-title">${article.title}</div>
                <small style="color: var(--text-light)">
                    👁️ ${formatNumber(article.views)} views
                </small>
            </div>
        </div>
    `).join('');
}


// ========================================
// FETCH CATEGORIES
// ========================================

async function fetchCategories() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/categories`);
        const data = await response.json();

        if (data.success) {
            renderCategories(data.categories);
        }
    } catch (error) {
        console.error('Categories fetch error:', error);
    }
}

function renderCategories(categories) {
    const container = document.getElementById('categoriesList');
    if (!container) return;

    container.innerHTML = categories.map(cat => `
        <div class="category-item" 
             onclick="window.location.href='category.html?cat=${cat.slug}'">
            <span>${cat.icon} ${cat.name}</span>
        </div>
    `).join('');
}


// ========================================
// TOP DEALS SIDEBAR
// ========================================

function renderTopDeals() {
    const container = document.getElementById('topDeals');
    if (!container) return;

    const deals = [
        {
            name: "Samsung Galaxy S24",
            price: "₹74,999",
            image: "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=300",
            url: `https://www.amazon.in/s?k=Samsung+Galaxy+S24&tag=${getAmazonTag()}`
        },
        {
            name: "boAt Rockerz Earbuds",
            price: "₹1,999",
            image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
            url: `https://www.amazon.in/s?k=boat+earbuds&tag=${getAmazonTag()}`
        },
        {
            name: "Kindle Paperwhite",
            price: "₹13,999",
            image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300",
            url: `https://www.amazon.in/s?k=kindle+paperwhite&tag=${getAmazonTag()}`
        }
    ];

    container.innerHTML = deals.map(deal => `
        <div class="deal-item">
            <img class="deal-image" 
                 src="${deal.image}" 
                 alt="${deal.name}"
                 onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
            <div class="deal-name">${deal.name}</div>
            <div class="deal-price">${deal.price}</div>
            <a href="${deal.url}" 
               target="_blank" 
               class="deal-btn"
               onclick="trackDealClick('${deal.name}')">
                🛒 Amazon Par Dekho
            </a>
        </div>
    `).join('');
}

function getAmazonTag() {
    return 'sk200709-21';
}

function trackDealClick(productName) {
    console.log('Deal clicked:', productName);
}


// ========================================
// NEWS TICKER
// ========================================

async function loadNewsTicker() {
    try {
        const response = await fetch(
            `${CONFIG.API_URL}/api/articles?page=1&limit=5`
        );
        const data = await response.json();

        if (data.success && data.articles.length > 0) {
            const ticker = document.getElementById('newsTicker');
            if (ticker) {
                ticker.textContent = data.articles
                    .map(a => `• ${a.title}`)
                    .join('   ');
            }
        }
    } catch (error) {
        console.error('Ticker error:', error);
    }
}


// ========================================
// HELPER FUNCTIONS
// ========================================

function getCategoryIcon(categoryId) {
    const icons = {
        1: '💻', 2: '🏏', 3: '💼',
        4: '🎬', 5: '📚', 6: '🌍',
        7: '🇮🇳', 8: '📰'
    };
    return icons[categoryId] || '📰';
}

function openArticle(slug) {
    window.location.href = `article.html?slug=${slug}`;
}

function filterByCategory(category, btn) {
    currentCategory = category;
    currentPage = 1;

    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('active');
    });
    btn.classList.add('active');

    fetchArticles(1, category);
}

function goToPage(page) {
    currentPage = page;
    fetchArticles(page, currentCategory);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    const grid = document.getElementById('articlesGrid');
    if (grid) {
        grid.innerHTML = `
            <div style="text-align:center; padding:40px; color:var(--text-light)">
                <p style="font-size:3rem">😔</p>
                <p>${message}</p>
                <button onclick="initPage()" 
                        style="margin-top:12px; padding:8px 20px; 
                               background:var(--primary); color:white; 
                               border:none; border-radius:8px; cursor:pointer">
                    Dobara Try Karein
                </button>
            </div>
        `;
    }
}


// ========================================
// SETTINGS MENU & LANGUAGE SELECTOR
// ========================================

function initSettingsMenu() {
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsMenu = document.getElementById('settingsMenu');
    if (!settingsBtn || !settingsMenu) return;

    settingsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        settingsMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!settingsBtn.contains(e.target) && !settingsMenu.contains(e.target)) {
            settingsMenu.classList.remove('show');
        }
    });
}

function initSettingsLanguage() {
    const container = document.getElementById('settingsLangDropdown');
    if (!container) return;
    if (typeof createLanguageSelector === 'function') {
        container.innerHTML = createLanguageSelector('site');
    }
}

// ========================================
// INIT
// ========================================

async function initPage() {
    await Promise.all([
        fetchArticles(1, 'all'),
        fetchTrending(),
        fetchCategories(),
        loadNewsTicker()
    ]);
    renderTopDeals();
    
    initSettingsMenu();
    initSettingsLanguage();
}

// Start
document.addEventListener('DOMContentLoaded', initPage);
