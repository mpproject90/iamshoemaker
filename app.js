/* ======================================================================
   iamshoemaker.com — Application JavaScript
   Misaki Zuno 造 | Where Craftsmanship Meets Intelligence
====================================================================== */

// ─── CONSTANTS ──────────────────────────────────────────────────────────
const FEED_URL     = './feed.json';
const BULLETIN_URL = './bulletin.json';
const REFRESH_INTERVAL    = 30 * 60 * 1000;
const ARTICLES_PER_PAGE   = 20;
const HOMEPAGE_ARTICLE_COUNT = 6;

// ─── STATE ──────────────────────────────────────────────────────────────
let feedData           = null;
let currentCategory    = 'All';
let currentPage        = 1;
let searchQuery        = '';
let searchDebounceTimer = null;
let currentSort        = 'newest';

// ─── UTILITY ────────────────────────────────────────────────────────────

function truncate(str, maxLen) {
  if (!str) return '';
  return str.length <= maxLen ? str : str.slice(0, maxLen) + '...';
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

function timeAgo(isoString) {
  const now  = new Date();
  const then = new Date(isoString);
  const diffMins = Math.floor((now - then) / 60000);

  if (diffMins < 1)    return 'Just now';
  if (diffMins < 60)   return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
  if (diffMins < 120)  return '1 hour ago';
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
  if (diffMins < 2880) return 'Yesterday';
  return `${Math.floor(diffMins / 1440)} days ago`;
}

function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// ─── DATA LOADING ───────────────────────────────────────────────────────

async function loadFeed() {
  try {
    const isNewsPage = !!document.getElementById('news-feed-grid');
    const isHomePage = !!document.getElementById('home-feed-grid');

    const container = isNewsPage
      ? document.getElementById('news-feed-grid')
      : document.getElementById('home-feed-grid');

    if (container) showSkeleton(container, isHomePage ? HOMEPAGE_ARTICLE_COUNT : 9);

    const response = await fetch(FEED_URL + '?t=' + Date.now());
    if (!response.ok) throw new Error('Feed unavailable');
    feedData = await response.json();

    const lastUpdatedEl = document.getElementById('last-updated-text');
    if (lastUpdatedEl && feedData.last_updated) {
      lastUpdatedEl.textContent = 'Last updated: ' + timeAgo(feedData.last_updated);
    }

    if (isNewsPage)      renderNewsFeed();
    else if (isHomePage) renderHomeFeed();

  } catch (err) {
    console.error('Feed load error:', err);
    ['home-feed-grid', 'news-feed-grid'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:60px 20px;">
          <p style="color:var(--color-text-muted);font-size:14px;">Unable to load feed. Please try again shortly.</p>
        </div>`;
    });
  }
}

// ─── RENDER HOME FEED ───────────────────────────────────────────────────

function renderHomeFeed() {
  const container = document.getElementById('home-feed-grid');
  if (!container || !feedData) return;

  let articles = feedData.articles.slice();
  if (currentCategory !== 'All') articles = articles.filter(a => a.category === currentCategory);
  articles.sort((a, b) => new Date(b.original_publish_time) - new Date(a.original_publish_time));
  articles = articles.slice(0, HOMEPAGE_ARTICLE_COUNT);

  if (articles.length === 0) { showEmptyState(container); return; }
  container.innerHTML = articles.map(a => buildCard(a)).join('');
}

// ─── RENDER NEWS FEED ───────────────────────────────────────────────────

function renderNewsFeed() {
  const container = document.getElementById('news-feed-grid');
  if (!container || !feedData) return;

  let articles = feedData.articles.slice();

  if (currentCategory !== 'All') articles = articles.filter(a => a.category === currentCategory);

  if (searchQuery) {
    articles = articles.filter(a =>
      a.title.toLowerCase().includes(searchQuery) ||
      (a.summary && a.summary.toLowerCase().includes(searchQuery)) ||
      (a.brands_mentioned && a.brands_mentioned.some(b => b.toLowerCase().includes(searchQuery))) ||
      a.source_name.toLowerCase().includes(searchQuery)
    );
  }

  if (currentSort === 'newest')    articles.sort((a, b) => new Date(b.original_publish_time) - new Date(a.original_publish_time));
  else if (currentSort === 'oldest') articles.sort((a, b) => new Date(a.original_publish_time) - new Date(b.original_publish_time));
  else if (currentSort === 'relevance') articles.sort((a, b) => b.relevance_score - a.relevance_score);

  const countEl = document.getElementById('results-count');
  if (countEl) {
    const total       = articles.length;
    const label       = currentCategory !== 'All' ? ` in ${currentCategory}` : '';
    const searchLabel = searchQuery ? ` matching "${searchQuery}"` : '';
    countEl.textContent = `${total} article${total === 1 ? '' : 's'}${label}${searchLabel}`;
  }

  const paginated = paginate(articles, currentPage, ARTICLES_PER_PAGE);

  if (articles.length === 0) {
    showEmptyState(container);
    document.getElementById('pagination').innerHTML = '';
    return;
  }

  container.innerHTML = paginated.map(a => buildCard(a)).join('');
  renderPagination(articles.length, ARTICLES_PER_PAGE);
}

// ─── BUILD ARTICLE CARD ─────────────────────────────────────────────────

function buildCard(article) {
  const categorySlug = slugify(article.category);
  const brandTagsHtml = article.brands_mentioned && article.brands_mentioned.length > 0
    ? article.brands_mentioned.map(b => `<span class="brand-tag">${b}</span>`).join('')
    : '';

  return `<article class="article-card" onclick="openArticle('${article.id}')" style="cursor:pointer;">
    <div class="card-header">
      <span class="badge badge-${categorySlug}">${article.category}</span>
      <span class="source-name">${article.source_name}</span>
    </div>
    <h3 class="card-title">${article.title}</h3>
    <p class="card-summary">${truncate(article.summary, 120)}</p>
    <div class="card-footer">
      <div class="brand-tags">${brandTagsHtml}</div>
      <span class="timestamp">${timeAgo(article.original_publish_time)}</span>
    </div>
  </article>`;
}

// ─── CATEGORY FILTERING ─────────────────────────────────────────────────

function filterByCategory(category) {
  currentCategory = category;
  currentPage     = 1;

  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === category);
  });

  if (document.getElementById('news-feed-grid'))      renderNewsFeed();
  else if (document.getElementById('home-feed-grid')) renderHomeFeed();
}

// ─── SEARCH ─────────────────────────────────────────────────────────────

function searchArticles(query) {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    searchQuery = query.toLowerCase().trim();
    currentPage = 1;
    renderNewsFeed();
  }, 300);
}

// ─── PAGINATION ─────────────────────────────────────────────────────────

function paginate(articles, page, perPage) {
  const start = (page - 1) * perPage;
  return articles.slice(start, start + perPage);
}

function renderPagination(total, perPage) {
  const container = document.getElementById('pagination');
  if (!container) return;

  const totalPages = Math.ceil(total / perPage);
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  let html = `<button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>&#8592;</button>`;

  let startPage = Math.max(1, currentPage - 2);
  let endPage   = Math.min(totalPages, startPage + 4);
  if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

  if (startPage > 1) {
    html += `<button class="page-btn" onclick="goToPage(1)">1</button>`;
    if (startPage > 2) html += `<span class="page-ellipsis">…</span>`;
  }

  for (let i = startPage; i <= endPage; i++) {
    html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) html += `<span class="page-ellipsis">…</span>`;
    html += `<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
  }

  html += `<button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>&#8594;</button>`;
  container.innerHTML = html;
}

function goToPage(page) {
  const totalPages = feedData ? Math.ceil(getFilteredArticles().length / ARTICLES_PER_PAGE) : 1;
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  renderNewsFeed();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function getFilteredArticles() {
  if (!feedData) return [];
  let articles = feedData.articles.slice();
  if (currentCategory !== 'All') articles = articles.filter(a => a.category === currentCategory);
  if (searchQuery) {
    articles = articles.filter(a =>
      a.title.toLowerCase().includes(searchQuery) ||
      (a.summary && a.summary.toLowerCase().includes(searchQuery)) ||
      (a.brands_mentioned && a.brands_mentioned.some(b => b.toLowerCase().includes(searchQuery))) ||
      a.source_name.toLowerCase().includes(searchQuery)
    );
  }
  return articles;
}

// ─── SKELETON & EMPTY STATE ─────────────────────────────────────────────

function showSkeleton(container, count) {
  let html = '';
  for (let i = 0; i < count; i++) {
    html += `
      <div class="skeleton-card">
        <div class="skeleton-badge skeleton"></div>
        <div class="skeleton-title skeleton" style="margin-top:8px;"></div>
        <div class="skeleton-title-short skeleton" style="margin-top:6px;"></div>
        <div class="skeleton-text skeleton" style="margin-top:10px;"></div>
        <div class="skeleton-text skeleton"></div>
        <div class="skeleton-text-short skeleton"></div>
      </div>`;
  }
  container.innerHTML = html;
}

function showEmptyState(container) {
  container.innerHTML = `
    <div style="grid-column:1/-1;text-align:center;padding:60px 20px;">
      <div style="font-size:32px;margin-bottom:16px;opacity:0.25;font-family:serif;">造</div>
      <p style="color:var(--color-text-muted);font-size:14px;">No articles found for this selection.</p>
    </div>`;
}

// ─── TOAST ──────────────────────────────────────────────────────────────

function showToast(message) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ─── AUTO REFRESH ───────────────────────────────────────────────────────

function startAutoRefresh() {
  setInterval(() => {
    loadFeed();
    showToast('Feed refreshed');
  }, REFRESH_INTERVAL);
}

// ─── MOBILE NAV ─────────────────────────────────────────────────────────

function initMobileNav() {
  const hamburger  = document.getElementById('nav-hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = mobileMenu.classList.contains('open');
    mobileMenu.classList.toggle('open', !isOpen);
    hamburger.classList.toggle('open', !isOpen);
  });

  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
      hamburger.classList.remove('open');
    }
  });

  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      hamburger.classList.remove('open');
    });
  });
}

// ─── INIT HELPERS ───────────────────────────────────────────────────────

function initCategoryFilters() {
  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', () => filterByCategory(btn.dataset.category));
  });
}

function initSearch() {
  const searchInput = document.getElementById('news-search');
  if (!searchInput) return;
  searchInput.addEventListener('input', (e) => searchArticles(e.target.value));
}

function initSort() {
  const sortSelect = document.getElementById('sort-select');
  if (!sortSelect) return;
  sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    currentPage = 1;
    renderNewsFeed();
  });
}

function setActiveNavLink() {
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

function openArticle(id) {
  window.location.href = 'article.html?id=' + id;
}

// ─── ARTICLE DETAIL PAGE ────────────────────────────────────────────────

async function initArticlePage() {
  const params    = new URLSearchParams(window.location.search);
  const articleId = params.get('id');
  if (!articleId) { window.location.href = 'news.html'; return; }

  try {
    const response = await fetch(FEED_URL + '?t=' + Date.now());
    if (!response.ok) throw new Error('Feed unavailable');
    const data    = await response.json();
    const article = data.articles.find(a => a.id === articleId);
    if (!article) { window.location.href = 'news.html'; return; }
    renderArticlePage(article);
  } catch (err) {
    console.error('Article load error:', err);
    document.getElementById('article-body').innerHTML = `
      <p style="color:var(--color-text-muted);text-align:center;padding:60px 0;">
        Unable to load article. <a href="news.html" style="color:var(--color-gold-dim);">Back to feed →</a>
      </p>`;
  }
}

function renderArticlePage(article) {
  const categorySlug = slugify(article.category);
  document.title = article.title + ' — Misaki Zuno 造';

  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) metaDesc.setAttribute('content', article.summary);

  const brandTagsHtml = article.brands_mentioned && article.brands_mentioned.length > 0
    ? article.brands_mentioned.map(b => `<span class="brand-tag">${b}</span>`).join('')
    : '';

  const keywordsHtml = article.keywords_matched && article.keywords_matched.length > 0
    ? `<div class="article-keywords">
         ${article.keywords_matched.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
       </div>`
    : '';

  document.getElementById('article-body').innerHTML = `
    <div class="article-meta-top">
      <span class="badge badge-${categorySlug}">${article.category}</span>
      <span class="article-source-label">${article.source_name}</span>
      <span class="article-timestamp">${timeAgo(article.original_publish_time)}</span>
    </div>

    <h1 class="article-title">${article.title}</h1>
    <div class="article-divider"></div>
    <p class="article-summary">${article.summary}</p>

    ${brandTagsHtml ? `<div class="article-brands-row">${brandTagsHtml}</div>` : ''}
    ${keywordsHtml}

    <div class="article-source-block">
      <div class="source-block-inner">
        <div class="source-block-left">
          <span class="source-block-label">Original source</span>
          <span class="source-block-domain">${article.source_domain || article.source_name}</span>
        </div>
        <a href="${article.source_url}" target="_blank" rel="noopener" class="btn-primary source-block-btn">
          Read Full Article →
        </a>
      </div>
    </div>

    <div class="article-back-row">
      <a href="news.html" class="article-back-link">← Back to Feed</a>
    </div>
  `;
}

// ─── BLOG FUNCTIONS ─────────────────────────────────────────────────────

const POSTS_URL = './posts.json';

async function loadBlog() {
  const grid = document.getElementById('blog-grid');
  if (!grid) return;

  try {
    const response = await fetch(POSTS_URL + '?t=' + Date.now());
    if (!response.ok) throw new Error('Posts unavailable');
    const data  = await response.json();
    const posts = data.posts.slice().sort((a, b) => new Date(b.date) - new Date(a.date));

    if (posts.length === 0) {
      grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 20px;">
        <p style="color:var(--color-text-muted);">No posts yet. Check back soon.</p>
      </div>`;
      return;
    }

    grid.innerHTML = posts.map(post => buildBlogCard(post)).join('');
  } catch (err) {
    console.error('Blog load error:', err);
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 20px;">
      <p style="color:var(--color-text-muted);">Unable to load posts. Please try again shortly.</p>
    </div>`;
  }
}

function buildBlogCard(post) {
  const imageHtml = post.image
    ? `<div class="blog-card-image"><img src="${post.image}" alt="${post.title}" loading="lazy"></div>`
    : `<div class="blog-card-image blog-card-image-placeholder"><span class="blog-placeholder-kanji">造</span></div>`;

  const dateFormatted = new Date(post.date).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

  return `
    <article class="blog-card" onclick="window.location.href='blog-post.html?id=${post.id}'" style="cursor:pointer;">
      ${imageHtml}
      <div class="blog-card-body">
        <div class="blog-card-meta">
          <span class="badge badge-${slugify(post.category)}">${post.category}</span>
          <span class="blog-card-date">${dateFormatted}</span>
        </div>
        <h2 class="blog-card-title">${post.title}</h2>
        <p class="blog-card-summary">${post.summary}</p>
        <span class="blog-card-link">Read more →</span>
      </div>
    </article>`;
}

async function initBlogPostPage() {
  const params = new URLSearchParams(window.location.search);
  const postId = params.get('id');
  if (!postId) { window.location.href = 'blog.html'; return; }

  try {
    const response = await fetch(POSTS_URL + '?t=' + Date.now());
    if (!response.ok) throw new Error('Posts unavailable');
    const data = await response.json();
    const post = data.posts.find(p => p.id === postId);
    if (!post) { window.location.href = 'blog.html'; return; }
    renderBlogPost(post);
  } catch (err) {
    console.error('Blog post load error:', err);
    document.getElementById('blog-post-body').innerHTML = `
      <div class="container" style="text-align:center;padding:80px 24px;">
        <p style="color:var(--color-text-muted);">Unable to load post.
          <a href="blog.html" style="color:var(--color-gold-dim);">Back to Blog →</a>
        </p>
      </div>`;
  }
}

function renderBlogPost(post) {
  document.title = post.title + ' — Misaki Zuno 造';

  const dateFormatted = new Date(post.date).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

  const imageHtml = post.image
    ? `<div class="blog-post-image"><img src="${post.image}" alt="${post.title}"></div>`
    : '';

  const paragraphs = Array.isArray(post.content)
    ? post.content
    : post.content.trim().split(/\n\n+/).filter(p => p.trim());
  const paragraphsHtml = paragraphs.map(p => `<p>${p.trim()}</p>`).join('');

  document.getElementById('blog-post-body').innerHTML = `
    <div class="container">
      <div class="article-page">
        <div class="article-container">
          <a href="blog.html" class="article-back-link" style="display:inline-block;margin-bottom:32px;">← Back to Blog</a>
          <div class="article-meta-top">
            <span class="badge badge-${slugify(post.category)}">${post.category}</span>
            <span class="article-timestamp">${dateFormatted}</span>
          </div>
          <h1 class="article-title">${post.title}</h1>
          <div class="article-divider"></div>
          ${imageHtml}
          <div class="blog-post-body">${paragraphsHtml}</div>
          <div class="article-back-row">
            <a href="blog.html" class="article-back-link">← Back to Blog</a>
          </div>
        </div>
      </div>
    </div>`;
}

// ─── SUNDAY INTELLIGENCE REPORT (BULLETIN) ──────────────────────────────

async function loadBulletin() {
  const container = document.getElementById('bulletin-container');
  if (!container) return;

  try {
    const response = await fetch(BULLETIN_URL + '?t=' + Date.now());
    if (!response.ok) throw new Error('Bulletin unavailable');
    const data = await response.json();

    if (!data.bulletins || data.bulletins.length === 0) {
      container.innerHTML = `<div class="bulletin-empty">The first Sunday Intelligence Report publishes this Sunday.</div>`;
      return;
    }

    const latest = data.bulletins[0];
    renderBulletin(latest, container);

  } catch (err) {
    console.error('Bulletin load error:', err);
    container.innerHTML = `<div class="bulletin-empty">Sunday Intelligence Report coming soon.</div>`;
  }
}

function renderBulletin(bulletin, container) {
  const dateFrom = new Date(bulletin.date_from).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  const dateTo   = new Date(bulletin.date_to).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

  const itemsHtml = bulletin.articles.map((item, i) => {
    const categorySlug = slugify(item.category || 'retail');
    return `
      <div class="bulletin-item" onclick="window.open('${item.source_url}','_blank')" title="Read full article">
        <div class="bulletin-rank">${String(i + 1).padStart(2, '0')}</div>
        <div class="bulletin-item-content">
          <div class="bulletin-item-meta">
            <span class="badge badge-${categorySlug}">${item.category}</span>
            <span class="source-name">${item.source_name}</span>
          </div>
          <div class="bulletin-item-title">${item.title}</div>
          ${item.misaki_take ? `<div class="bulletin-item-take">"${item.misaki_take}"</div>` : ''}
        </div>
      </div>`;
  }).join('');

  container.innerHTML = `
    <div class="bulletin-card">
      <div class="bulletin-masthead">
        <div class="bulletin-masthead-left">
          <div class="bulletin-title">Sunday Intelligence Report</div>
          <div class="bulletin-date-range">${dateFrom} — ${dateTo}</div>
        </div>
        <div class="bulletin-week-badge">Wk ${bulletin.week_number} · ${bulletin.year}</div>
      </div>
      ${bulletin.intro ? `<div class="bulletin-intro">${bulletin.intro}</div>` : ''}
      <div class="bulletin-items">${itemsHtml}</div>
      <div class="bulletin-footer">
        <span class="bulletin-footer-sig">— Misaki Zuno 造</span>
        <span class="bulletin-footer-meta">Top ${bulletin.articles.length} signals this week</span>
      </div>
    </div>`;
}

// ─── PAGE INIT ──────────────────────────────────────────────────────────

function initPage() {
  setActiveNavLink();

  const isNewsPage     = !!document.getElementById('news-feed-grid');
  const isHomePage     = !!document.getElementById('home-feed-grid');
  const isArticlePage  = document.body.dataset.page === 'article';
  const isBlogPage     = document.body.dataset.page === 'blog';
  const isBlogPostPage = document.body.dataset.page === 'blog-post';

  if (isHomePage) {
    initMobileNav();
    initCategoryFilters();
    loadFeed();
    loadBulletin();
    startAutoRefresh();
  }

  if (isNewsPage) {
    initMobileNav();
    initCategoryFilters();
    initSearch();
    initSort();
    loadFeed();
    startAutoRefresh();
  }

  if (isArticlePage)  { initMobileNav(); initArticlePage(); }
  if (isBlogPage)     { initMobileNav(); loadBlog(); }
  if (isBlogPostPage) { initMobileNav(); initBlogPostPage(); }

  if (!isHomePage && !isNewsPage && !isArticlePage && !isBlogPage && !isBlogPostPage) {
    initMobileNav();
  }
}

document.addEventListener('DOMContentLoaded', initPage);
