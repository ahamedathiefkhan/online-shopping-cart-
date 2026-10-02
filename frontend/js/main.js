/**
 * Main application JS — Layout, Toast notifications, Cart badge, Global auth state
 */
let currentUser = null;
let authPromise = null;

document.addEventListener('DOMContentLoaded', async () => {
  renderNavbar();
  renderFooter();
  await getAuthUser();
  updateCartBadge();
});

// Toast notification helper — Industrial telemetry theme
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="mono-spec" style="font-weight: bold;">${type === 'success' ? '[SYS // OK]' : '[SYS // ERR]'}</span>
    <div>${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3500);
}

// Format Currency in Rupees (INR)
function formatCurrency(amount) {
  const num = typeof amount === 'number' ? amount : parseFloat(amount) || 0;
  return '₹' + num.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}
window.formatCurrency = formatCurrency;

// Get Auth User asynchronously — resolves auth state before proceeding
async function getAuthUser(forceRefresh = false) {
  if (forceRefresh || !authPromise) {
    authPromise = (async () => {
      try {
        const res = await apiRequest('/users/profile', { method: 'GET' });
        if (res.authenticated && res.user) {
          currentUser = res.user;
        } else {
          currentUser = null;
        }
      } catch (err) {
        currentUser = null;
      }
      updateNavbarUserUI();
      return currentUser;
    })();
  }
  return authPromise;
}

// Global Cart Count Update
async function updateCartBadge() {
  const badge = document.getElementById('cart-count-badge');
  if (!badge) return;

  const user = await getAuthUser();
  if (!user) {
    badge.textContent = '0';
    return;
  }

  try {
    const cart = await apiRequest('/cart', { method: 'GET' });
    badge.textContent = cart.total_items || 0;
  } catch (err) {
    badge.textContent = '0';
  }
}

// Render Industrial Header Navigation — Amazon-Style Top Navigation Bar (Sub-Navbar Removed)
function renderNavbar() {
  const header = document.getElementById('site-header');
  if (!header) return;

  const currentPath = window.location.pathname;
  const currentLocation = localStorage.getItem('digicart_location') || 'Coimbatore 641008';

  header.innerHTML = `
    <nav class="navbar">
      <!-- Main Top Navigation Bar -->
      <div class="nav-main-bar">
        <!-- Brand Logo -->
        <a href="/pages/index.html" class="brand-logo" title="digiCart Home">
          <img src="/images/digicart-icon.png" alt="digiCart" class="brand-logo-img" />
          <span class="brand-logo-text">digi<span class="brand-logo-accent">Cart</span></span>
        </a>

        <!-- Location Selector Widget -->
        <div class="nav-location-widget" title="Click to Change Delivery Location" onclick="changeDeliveryLocation()">
          <span class="nav-location-icon">📍</span>
          <div class="nav-location-text">
            <span id="nav-location-sub" class="nav-location-sub">Delivering to ${currentLocation}</span>
            <span class="nav-location-main">Update location</span>
          </div>
        </div>

        <!-- Central Search Bar with Category Select -->
        <form class="nav-search-container" onsubmit="handleNavSearchSubmit(event)">
          <select id="nav-search-category" class="nav-search-category-select">
            <option value="">All Categories</option>
            <option value="1">Electronics</option>
            <option value="2">Fashion & Clothing</option>
            <option value="3">Books & Stationery</option>
            <option value="4">Home & Living</option>
          </select>
          <input 
            type="text" 
            id="nav-search-input" 
            class="nav-search-input" 
            placeholder="Search digiCart inventory..." 
            autocomplete="off" 
          />
          <button type="submit" class="nav-search-btn" title="Search Catalog">
            <span>🔍</span>
          </button>
        </form>

        <!-- Right Side Actions Area -->
        <div class="nav-right-actions">
          <!-- Region / Flag Badge -->
          <div class="nav-lang-badge" title="Region: India (EN)" onclick="showToast('Region set to India (EN)', 'success')">
            <span>🇮🇳</span>
            <span>EN ▾</span>
          </div>

          <!-- User Account Container -->
          <div id="user-nav-container">
            <a href="/pages/login.html" class="nav-action-item">
              <span class="nav-action-sub">Hello, sign in</span>
              <span class="nav-action-main">Mobile & Account ▾</span>
            </a>
          </div>

          <!-- Returns & Orders Link -->
          <a href="/pages/order-history.html" class="nav-action-item ${currentPath.includes('order-history.html') ? 'active' : ''}">
            <span class="nav-action-sub">Returns</span>
            <span class="nav-action-main">& Orders</span>
          </a>

          <!-- Cart Button -->
          <a href="/pages/cart.html" class="cart-btn-link-amazon">
            <span style="font-size: 1.25rem;">🛒</span>
            <span>CART</span>
            <span id="cart-count-badge" class="cart-badge">0</span>
          </a>
        </div>
      </div>
    </nav>
  `;
}

// Location Change Handler
function changeDeliveryLocation() {
  const currentLoc = localStorage.getItem('digicart_location') || 'Coimbatore 641008';
  const newLoc = prompt('Enter your delivery city or pincode:', currentLoc);
  if (newLoc && newLoc.trim()) {
    const trimmed = newLoc.trim();
    localStorage.setItem('digicart_location', trimmed);
    const locText = document.getElementById('nav-location-sub');
    if (locText) locText.textContent = `Delivering to ${trimmed}`;
    showToast(`Delivery location updated to ${trimmed}`, 'success');
  }
}

// Search form handler
function handleNavSearchSubmit(event) {
  event.preventDefault();
  const searchInput = document.getElementById('nav-search-input');
  const catSelect = document.getElementById('nav-search-category');

  const query = searchInput ? searchInput.value.trim() : '';
  const categoryId = catSelect ? catSelect.value : '';

  const currentPath = window.location.pathname;

  // If on index.html and loadProducts function exists, trigger live catalog search
  if ((currentPath.includes('index.html') || currentPath === '/') && typeof loadProducts === 'function') {
    if (typeof selectedCategoryId !== 'undefined') {
      selectedCategoryId = categoryId || null;
    }
    const mainSearchInput = document.getElementById('search-input');
    if (mainSearchInput) mainSearchInput.value = query;

    const mainCategoryPills = document.querySelectorAll('.category-pill');
    if (mainCategoryPills.length > 0) {
      mainCategoryPills.forEach(pill => pill.classList.remove('active'));
    }

    loadProducts();
  } else {
    // Navigate to index.html with query parameters
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (categoryId) params.append('category_id', categoryId);
    window.location.href = `/pages/index.html` + (params.toString() ? `?${params.toString()}` : '');
  }
}

function updateNavbarUserUI() {
  const userContainer = document.getElementById('user-nav-container');

  if (!userContainer) return;

  if (currentUser) {
    const firstName = currentUser.name ? currentUser.name.split(' ')[0] : 'User';
    const subText = currentUser.phone ? `📱 ${currentUser.phone}` : 'Account & Profile';
    const isAdmin = currentUser.role === 'admin';

    userContainer.innerHTML = `
      <div class="user-dropdown-wrapper">
        <div class="nav-action-item">
          <span class="nav-action-sub">Hello, ${firstName}</span>
          <span class="nav-action-main">${subText} ▾</span>
        </div>
        <div class="user-dropdown-menu">
          <a href="/pages/profile.html" class="user-dropdown-item">
            <span>👤</span>
            <span>Your Profile</span>
          </a>
          <a href="/pages/order-history.html" class="user-dropdown-item">
            <span>📦</span>
            <span>Your Orders</span>
          </a>
          ${isAdmin ? `
            <a href="/pages/admin/dashboard.html" class="user-dropdown-item" style="color: var(--lime-accent);">
              <span>⚙</span>
              <span>Telemetry Panel</span>
            </a>
          ` : ''}
          <div style="border-top: 1px solid var(--evergreen-surface); margin: 0.25rem 0;"></div>
          <button onclick="handleLogout()" class="user-dropdown-item" style="width: 100%; border: none; background: none; cursor: pointer; text-align: left; color: var(--status-error);">
            <span>🚪</span>
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    `;
  } else {
    userContainer.innerHTML = `
      <a href="/pages/login.html" class="nav-action-item">
        <span class="nav-action-sub">Hello, sign in</span>
        <span class="nav-action-main">Mobile & Account ▾</span>
      </a>
    `;
  }
}

async function handleLogout() {
  try {
    await apiRequest('/users/logout', { method: 'POST' });
    showToast('Session ended successfully', 'success');
    currentUser = null;
    updateNavbarUserUI();
    setTimeout(() => {
      window.location.href = '/pages/index.html';
    }, 500);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Render Amazon-Style Multi-Section Footer
function renderFooter() {
  const footer = document.getElementById('site-footer');
  if (!footer) return;

  footer.innerHTML = `
    <footer class="footer-container">
      <!-- Back to Top Button Bar -->
      <div class="footer-back-to-top" onclick="window.scrollTo({ top: 0, behavior: 'smooth' })">
        Back to top
      </div>

      <!-- Main 4-Column Footer Sections -->
      <div class="footer-main-section">
        <div>
          <h3 class="footer-col-title">Get to Know Us</h3>
          <ul class="footer-links-list">
            <li class="footer-link-item"><a href="/pages/index.html">About digiCart</a></li>
            <li class="footer-link-item"><a href="#">Careers</a></li>
            <li class="footer-link-item"><a href="#">Press Releases</a></li>
            <li class="footer-link-item"><a href="#">digiCart Science</a></li>
          </ul>
        </div>

        <div>
          <h3 class="footer-col-title">Connect with Us</h3>
          <ul class="footer-links-list">
            <li class="footer-link-item"><a href="https://facebook.com" target="_blank" rel="noopener">Facebook</a></li>
            <li class="footer-link-item"><a href="https://twitter.com" target="_blank" rel="noopener">Twitter</a></li>
            <li class="footer-link-item"><a href="https://instagram.com" target="_blank" rel="noopener">Instagram</a></li>
          </ul>
        </div>

        <div>
          <h3 class="footer-col-title">Make Money with Us</h3>
          <ul class="footer-links-list">
            <li class="footer-link-item"><a href="#">Sell on digiCart</a></li>
            <li class="footer-link-item"><a href="#">Sell under digiCart Accelerator</a></li>
            <li class="footer-link-item"><a href="#">Protect and Build Your Brand</a></li>
            <li class="footer-link-item"><a href="#">digiCart Global Selling</a></li>
            <li class="footer-link-item"><a href="#">Supply to digiCart</a></li>
            <li class="footer-link-item"><a href="#">Become an Affiliate</a></li>
            <li class="footer-link-item"><a href="#">Fulfilment by digiCart</a></li>
            <li class="footer-link-item"><a href="#">Advertise Your Products</a></li>
            <li class="footer-link-item"><a href="#">digiCart Pay on Merchants</a></li>
          </ul>
        </div>

        <div>
          <h3 class="footer-col-title">Let Us Help You</h3>
          <ul class="footer-links-list">
            <li class="footer-link-item"><a href="/pages/profile.html">Your Account</a></li>
            <li class="footer-link-item"><a href="/pages/order-history.html">Returns Centre</a></li>
            <li class="footer-link-item"><a href="#">Recalls and Product Safety Alerts</a></li>
            <li class="footer-link-item"><a href="#">100% Purchase Protection</a></li>
            <li class="footer-link-item"><a href="#">digiCart App Download</a></li>
            <li class="footer-link-item"><a href="#">Help</a></li>
          </ul>
        </div>
      </div>

      <!-- Middle Controls Bar -->
      <div class="footer-controls-section">
        <a href="/pages/index.html" class="brand-logo" title="digiCart Home">
          <img src="/images/digicart-icon.png" alt="digiCart" style="height: 32px; width: auto; object-fit: contain;" />
          <span class="brand-logo-text" style="font-size: 1.2rem;">digi<span class="brand-logo-accent">Cart</span></span>
        </a>
        <div style="display: flex; gap: 1rem;">
          <button class="footer-control-btn" onclick="showToast('Language: English (US)', 'success')">
            <span>🌐 English</span>
            <span>⬍</span>
          </button>
          <button class="footer-control-btn" onclick="showToast('Region: India', 'success')">
            <span>🇮🇳 India</span>
          </button>
        </div>
      </div>

      <!-- Ecosystem Services Grid -->
      <div class="footer-services-section">
        <div class="footer-services-grid">
          <div class="footer-service-card">
            <h4>AbeBooks</h4>
            <p>Books, art & collectibles</p>
          </div>
          <div class="footer-service-card">
            <h4>digiCart Cloud (AWS)</h4>
            <p>Scalable Cloud Computing Services</p>
          </div>
          <div class="footer-service-card">
            <h4>Audible</h4>
            <p>Download Audio Books</p>
          </div>
          <div class="footer-service-card">
            <h4>IMDb</h4>
            <p>Movies, TV & Celebrities</p>
          </div>
          <div class="footer-service-card">
            <h4>Shopbop</h4>
            <p>Designer Fashion Brands</p>
          </div>
          <div class="footer-service-card">
            <h4>digiCart Business</h4>
            <p>Everything For Your Business</p>
          </div>
          <div class="footer-service-card">
            <h4>digiCart Music</h4>
            <p>Stream millions of songs</p>
          </div>
        </div>
      </div>

      <!-- Bottom Legal & Copyright Bar -->
      <div class="footer-bottom-bar">
        <div class="footer-legal-links">
          <a href="#">Conditions of Use & Sale</a>
          <a href="#">Privacy Notice</a>
          <a href="#">Interest-Based Ads</a>
        </div>
        <div>
          © 1996-2026, digiCart.com, Inc. or its affiliates
        </div>
      </div>
    </footer>
  `;
}
