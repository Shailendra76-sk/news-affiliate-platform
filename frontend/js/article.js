// ========================================
// ARTICLE.JS - Article Detail Page
// ========================================

let currentArticle = null;

// ========================================
// FETCH ARTICLE
// ========================================

async function fetchArticle() {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');

    if (!slug) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch(
            `${CONFIG.API_URL}/api/articles/${slug}`
        );
        const data = await response.json();

        if (data.success) {
            currentArticle = data.article;
            renderArticle(data.article);
            updateMetaTags(data.article);
            updateBreadcrumb(data.article);
        } else {
            showArticleError();
        }
    } catch (error) {
        console.error('Error fetching article:', error);
        showArticleError();
    }
}


// ========================================
// RENDER ARTICLE
// ========================================

function renderArticle(article) {
    const container = document.getElementById('articleContent');
    if (!container) return;

    const image = article.featured_image || CONFIG.DEFAULT_IMAGE;
    const date = formatDate(article.published_at);
    const category = article.category || { name: 'General', slug: 'general' };

    // Format content
    const formattedContent = formatArticleContent(article.content);

    // Affiliate products HTML
    const affiliateHTML = renderAffiliateProducts(
        article.affiliate_products || []
    );

    // FAQ HTML
    const faqHTML = renderFAQ(article.faq || []);

    // Hashtags HTML
    const hashtagsHTML = renderHashtags(article.hashtags || '');

    // Related articles HTML
    const relatedHTML = renderRelatedArticles(
        article.related_articles || []
    );

    container.innerHTML = `
        <!-- Article Header -->
        <div class="article-header">
            <span class="article-category-badge">
                ${category.icon || '📰'} ${category.name}
            </span>
            <h1 class="article-title">${article.title}</h1>
            <div class="article-meta">
                <span>📅 ${date}</span>
                <span>👁️ ${formatNumber(article.views)} views</span>
                <span>📖 ${article.word_count} words</span>
                <span>🤖 ${article.ai_provider || 'AI'}</span>
            </div>
        </div>

        <!-- Featured Image -->
        <img class="article-featured-image"
             src="${image}"
             alt="${article.title}"
             onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">

        <!-- Summary -->
        ${article.summary ? `
        <div class="article-summary">
            📌 ${article.summary}
        </div>
        ` : ''}

        <!-- Article Body -->
        <div class="article-body">
            ${formattedContent}
        </div>

        <!-- Affiliate Products -->
        ${affiliateHTML}

        <!-- Conclusion -->
        ${article.conclusion ? `
        <div class="article-conclusion">
            <h3>🎯 Conclusion</h3>
            <p>${article.conclusion}</p>
        </div>
        ` : ''}

        <!-- FAQ -->
        ${faqHTML}

        <!-- Hashtags -->
        ${hashtagsHTML}

        <!-- Related Articles -->
        ${relatedHTML}
    `;

    // Init FAQ accordion
    initFAQAccordion();
}


// ========================================
// FORMAT ARTICLE CONTENT
// ========================================

function formatArticleContent(content) {
    if (!content) return '';

    // Convert ## headings
    content = content.replace(
        /^## (.+)$/gm,
        '<h2>$1</h2>'
    );

    // Convert ### headings
    content = content.replace(
        /^### (.+)$/gm,
        '<h3>$1</h3>'
    );

    // Convert **bold**
    content = content.replace(
        /\*\*(.+?)\*\*/g,
        '<strong>$1</strong>'
    );

    // Convert *italic*
    content = content.replace(
        /\*(.+?)\*/g,
        '<em>$1</em>'
    );

    // Convert line breaks to paragraphs
    const paragraphs = content.split('\n\n');
    content = paragraphs
        .filter(p => p.trim())
        .map(p => {
            if (p.startsWith('<h2>') || p.startsWith('<h3>')) {
                return p;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        })
        .join('');

    return content;
}


// ========================================
// RENDER AFFILIATE PRODUCTS
// ========================================

function renderAffiliateProducts(products) {
    if (!products || products.length === 0) return '';

    return `
        <div class="affiliate-section">
            <h3 class="affiliate-section-title">
                🛒 Isse Bhi Dekho - Top Products
            </h3>
            <div class="affiliate-products-grid">
                ${products.slice(0, 6).map(product => `
                    <div class="affiliate-product-card">
                        <img class="affiliate-product-image"
                             src="${product.image || CONFIG.DEFAULT_IMAGE}"
                             alt="${product.name}"
                             onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
                        <div class="affiliate-product-name">
                            ${product.name}
                        </div>
                        <div class="affiliate-product-price">
                            ${product.price || 'Price Check Karein'}
                        </div>
                        <a href="${product.url}"
                           target="_blank"
                           class="affiliate-buy-btn"
                           onclick="trackProductClick(${product.id})">
                            🛒 Amazon Par Dekho
                        </a>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}


// ========================================
// RENDER FAQ
// ========================================

function renderFAQ(faqs) {
    if (!faqs || faqs.length === 0) return '';

    return `
        <div class="faq-section">
            <h2 class="faq-title">❓ Aksar Pooche Jaane Wale Sawaal</h2>
            ${faqs.map((faq, index) => `
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(${index})">
                        <span>${faq.question}</span>
                        <span class="faq-icon" id="faqIcon${index}">+</span>
                    </div>
                    <div class="faq-answer" id="faqAnswer${index}">
                        ${faq.answer}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function toggleFAQ(index) {
    const answer = document.getElementById(`faqAnswer${index}`);
    const icon = document.getElementById(`faqIcon${index}`);
    const question = answer?.previousElementSibling;

    if (answer) {
        answer.classList.toggle('open');
        if (icon) {
            icon.textContent = answer.classList.contains('open') ? '−' : '+';
        }
        if (question) {
            question.classList.toggle('active');
        }
    }
}

function initFAQAccordion() {
    // Open first FAQ by default
    const firstAnswer = document.getElementById('faqAnswer0');
    const firstIcon = document.getElementById('faqIcon0');
    if (firstAnswer) {
        firstAnswer.classList.add('open');
        if (firstIcon) firstIcon.textContent = '−';
    }
}


// ========================================
// RENDER HASHTAGS
// ========================================

function renderHashtags(hashtags) {
    if (!hashtags) return '';

    const tags = hashtags.split(' ').filter(t => t.startsWith('#'));

    return `
        <div class="article-hashtags">
            ${tags.map(tag => `
                <span class="hashtag"
                      onclick="searchByTag('${tag}')">
                    ${tag}
                </span>
            `).join('')}
        </div>
    `;
}

function searchByTag(tag) {
    const query = tag.replace('#', '');
    window.location.href = `search.html?q=${encodeURIComponent(query)}`;
}


// ========================================
// RENDER RELATED ARTICLES
// ========================================

function renderRelatedArticles(articles) {
    if (!articles || articles.length === 0) return '';

    return `
        <div class="related-section">
            <h2 class="related-title">📰 Related Articles</h2>
            <div class="related-grid">
                ${articles.map(article => `
                    <div class="related-card"
                         onclick="openArticle('${article.slug}')">
                        <img src="${article.featured_image || CONFIG.DEFAULT_IMAGE}"
                             alt="${article.title}"
                             onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
                        <div class="related-card-content">
                            <div class="related-card-title">
                                ${article.title}
                            </div>
                            <small style="color:var(--text-light)">
                                📅 ${formatDate(article.published_at)}
                            </small>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}


// ========================================
// UPDATE META TAGS
// ========================================

function updateMetaTags(article) {
    const image = article.featured_image || CONFIG.DEFAULT_IMAGE;

    // Title
    document.title = `${article.title} - LootBazaar News`;
    setMeta('pageTitle', article.title);

    // Meta
    setMeta('metaDescription', article.meta_description || article.summary);
    setMeta('metaKeywords', article.meta_keywords);

    // OG Tags
    setMeta('ogTitle', article.title);
    setMeta('ogDescription', article.meta_description || article.summary);
    setMeta('ogImage', image);

    // Twitter
    setMeta('twitterTitle', article.title);
    setMeta('twitterDesc', article.meta_description || article.summary);
    setMeta('twitterImage', image);
}

function setMeta(id, content) {
    const el = document.getElementById(id);
    if (el && content) {
        if (el.tagName === 'META') {
            el.setAttribute('content', content);
        } else {
            el.textContent = content;
        }
    }
}


// ========================================
// UPDATE BREADCRUMB
// ========================================

function updateBreadcrumb(article) {
    const catEl = document.getElementById('breadcrumbCategory');
    const titleEl = document.getElementById('breadcrumbTitle');

    if (catEl && article.category) {
        catEl.textContent = article.category.name;
        catEl.style.cursor = 'pointer';
        catEl.onclick = () => {
            window.location.href = 
                `category.html?cat=${article.category.slug}`;
        };
    }

    if (titleEl) {
        titleEl.textContent = truncateText(article.title, 40);
    }
}


// ========================================
// SHARE FUNCTIONS
// ========================================

function shareWhatsApp() {
    if (!currentArticle) return;
    const url = window.location.href;
    const text = `${currentArticle.title}\n\n${url}`;
    window.open(
        `https://wa.me/?text=${encodeURIComponent(text)}`,
        '_blank'
    );
}

function shareFacebook() {
    const url = window.location.href;
    window.open(
        `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        '_blank'
    );
}

function shareTwitter() {
    if (!currentArticle) return;
    const url = window.location.href;
    const text = currentArticle.title;
    window.open(
        `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
        '_blank'
    );
}

function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        showToast('Link copy ho gaya!', 'success');
    });
}


// ========================================
// TRENDING SIDEBAR
// ========================================

async function fetchTrending() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/trending`);
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('trendingPosts');
            if (container) {
                container.innerHTML = data.articles.map((a, i) => `
                    <div class="trending-item"
                         onclick="openArticle('${a.slug}')">
                        <span class="trending-number">${i + 1}</span>
                        <div>
                            <div class="trending-title">${a.title}</div>
                            <small style="color:var(--text-light)">
                                👁️ ${formatNumber(a.views)}
                            </small>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Trending error:', error);
    }
}


// ========================================
// SIDEBAR DEALS
// ========================================

function renderSidebarDeals() {
    const container = document.getElementById('sidebarDeals');
    if (!container) return;

    const deals = [
        {
            name: "Samsung Galaxy S24",
            price: "₹74,999",
            image: "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=300",
            url: `https://www.amazon.in/s?k=Samsung+Galaxy+S24&tag=sk200709-21`
        },
        {
            name: "boAt Rockerz Earbuds",
            price: "₹1,999",
            image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
            url: `https://www.amazon.in/s?k=boat+earbuds&tag=sk200709-21`
        },
        {
            name: "Kindle Paperwhite",
            price: "₹13,999",
            image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300",
            url: `https://www.amazon.in/s?k=kindle&tag=sk200709-21`
        }
    ];

    container.innerHTML = deals.map(deal => `
        <div class="sidebar-deal-item">
            <img class="sidebar-deal-img"
                 src="${deal.image}"
                 alt="${deal.name}"
                 onerror="this.src='${CONFIG.DEFAULT_IMAGE}'">
            <div class="deal-name">${deal.name}</div>
            <div class="deal-price">${deal.price}</div>
            <a href="${deal.url}"
               target="_blank"
               class="deal-btn">
                🛒 Amazon Par Dekho
            </a>
        </div>
    `).join('');
}


// ========================================
// TRACK CLICK
// ========================================

async function trackProductClick(productId) {
    try {
        await fetch(
            `${CONFIG.API_URL}/api/affiliate/click/${productId}`
        );
    } catch (error) {
        console.error('Track error:', error);
    }
}

function openArticle(slug) {
    window.location.href = `article.html?slug=${slug}`;
}

function showArticleError() {
    const container = document.getElementById('articleContent');
    if (container) {
        container.innerHTML = `
            <div style="text-align:center; padding:60px 20px">
                <p style="font-size:4rem">😔</p>
                <h2>Article nahi mila!</h2>
                <p style="color:var(--text-light); margin:12px 0">
                    Yeh article delete ho gaya ya URL galat hai
                </p>
                <a href="index.html"
                   style="display:inline-block; margin-top:16px;
                          background:var(--primary); color:white;
                          padding:10px 24px; border-radius:8px">
                    🏠 Home Par Jayen
                </a>
            </div>
        `;
    }
}


// ========================================
// INIT
// ========================================

document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([
        fetchArticle(),
        fetchTrending()
    ]);
    renderSidebarDeals();
});
