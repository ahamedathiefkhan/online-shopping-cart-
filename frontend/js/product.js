/**
 * Product Catalog Module — Data-Led Product Grid, Filtering, and Cart Operations
 */

let allProducts = [];
let selectedCategoryId = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('product-grid-container')) {
    initProductCatalog();
  }
});

async function initProductCatalog() {
  // Check for search query or category in URL
  const urlParams = new URLSearchParams(window.location.search);
  const qParam = urlParams.get('q');
  const catParam = urlParams.get('category_id');

  if (catParam) {
    selectedCategoryId = parseInt(catParam, 10);
  }

  const navSearchInput = document.getElementById('nav-search-input');
  if (navSearchInput && qParam) {
    navSearchInput.value = qParam;
  }

  const navCatSelect = document.getElementById('nav-search-category');
  if (navCatSelect && catParam) {
    navCatSelect.value = catParam;
  }

  await loadCategories();
  await loadProducts();
  setupSearchAndFilters();
}

// Load Categories into Industrial Category Pills
async function loadCategories() {
  const container = document.getElementById('category-pills-container');
  if (!container) return;

  try {
    const categories = await apiRequest('/products/categories', { method: 'GET' });
    
    let html = `
      <button class="category-pill ${!selectedCategoryId ? 'active' : ''}" onclick="filterByCategory(null, this)">ALL PRODUCTS</button>
    `;
    categories.forEach(cat => {
      const isActive = selectedCategoryId === cat.id;
      html += `
        <button class="category-pill ${isActive ? 'active' : ''}" onclick="filterByCategory(${cat.id}, this)">${cat.name.toUpperCase()}</button>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    console.error('Failed to load categories', err);
  }
}

// Load Products from API
async function loadProducts() {
  const container = document.getElementById('product-grid-container');
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted); font-family: var(--font-mono);">
      <div style="font-size: 1.2rem; margin-bottom: 0.5rem; color: var(--evergreen-dark);">[SYS // INITIALIZING CATALOG TELEMETRY...]</div>
      <div style="font-size: 0.85rem;">Fetching real-time inventory levels</div>
    </div>
  `;

  try {
    let url = '/products';
    const params = new URLSearchParams();

    // Check navbar category or selected pill
    const navCatSelect = document.getElementById('nav-search-category');
    const activeCategory = selectedCategoryId || (navCatSelect && navCatSelect.value ? parseInt(navCatSelect.value, 10) : null);

    if (activeCategory) params.append('category_id', activeCategory);

    // Check search query from top navbar or URL
    const navSearchInput = document.getElementById('nav-search-input');
    const urlParams = new URLSearchParams(window.location.search);
    const query = (navSearchInput && navSearchInput.value.trim()) || urlParams.get('q') || '';
    if (query) {
      params.append('q', query);
    }

    const sortSelect = document.getElementById('sort-select');
    if (sortSelect && sortSelect.value) {
      params.append('sort', sortSelect.value);
    }

    const minPriceInput = document.getElementById('min-price-input');
    if (minPriceInput && minPriceInput.value) {
      params.append('min_price', minPriceInput.value);
    }

    const maxPriceInput = document.getElementById('max-price-input');
    if (maxPriceInput && maxPriceInput.value) {
      params.append('max_price', maxPriceInput.value);
    }

    if (params.toString()) {
      url += '?' + params.toString();
    }

    allProducts = await apiRequest(url, { method: 'GET' });
    renderProductCards(allProducts);
  } catch (err) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--status-error); font-family: var(--font-mono);">
        <p>[ERR // TELEMETRY FETCH FAILED: ${err.message}]</p>
      </div>
    `;
  }
}

// Render Data-Led Product Cards
function renderProductCards(products) {
  const container = document.getElementById('product-grid-container');
  if (!container) return;

  if (!products || products.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem; background: var(--bg-paper-light); border-radius: var(--radius-sm); border: 1px solid var(--border-paper-strong);">
        <div style="font-family: var(--font-mono); font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--text-subtle);">[NO INVENTORY FOUND]</div>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Adjust search filters or price threshold parameters.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = products.map(product => {
    const skuCode = `SKU #${String(product.id).padStart(4, '0')}`;
    const inStock = product.stock_quantity > 0;

    return `
      <div class="product-card">
        <div class="product-image-wrap">
          <img src="${product.image_url}" alt="${product.name}" class="product-image" loading="lazy" />
          <span class="product-badge">${product.category_name}</span>
          <span class="product-sku-tag">${skuCode}</span>
        </div>
        <div class="product-info">
          <div class="product-category-name">${product.category_name}</div>
          <h3 class="product-title" title="${product.name}">${product.name}</h3>
          <p class="product-desc">${product.description || 'Precision item specification pending update.'}</p>
          
          <div class="product-telemetry-row">
            <div class="stock-indicator ${inStock ? 'in-stock' : 'out-stock'}">
              <span>${inStock ? '●' : '○'}</span>
              <span>${inStock ? `STOCK: ${product.stock_quantity} UNITS` : 'OUT OF STOCK'}</span>
            </div>
            <div style="color: var(--text-subtle);">DISPATCH: 24H</div>
          </div>

          <div class="product-footer">
            <div class="product-price">${formatCurrency(product.price)}</div>
            <button 
              onclick="addToCart(${product.id})" 
              class="btn-add-cart"
              ${!inStock ? 'disabled' : ''}
            >
              <span>+ ADD TO CART</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Filter by category
function filterByCategory(catId, btnElement) {
  selectedCategoryId = catId;
  const pills = document.querySelectorAll('.category-pill');
  pills.forEach(p => p.classList.remove('active'));
  if (btnElement) btnElement.classList.add('active');

  loadProducts();
}

// Setup live search & filter listeners
function setupSearchAndFilters() {
  const navSearchInput = document.getElementById('nav-search-input');
  if (navSearchInput) {
    let debounceTimer;
    navSearchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => loadProducts(), 250);
    });
  }

  const navCatSelect = document.getElementById('nav-search-category');
  if (navCatSelect) {
    navCatSelect.addEventListener('change', () => {
      selectedCategoryId = navCatSelect.value ? parseInt(navCatSelect.value, 10) : null;
      const pills = document.querySelectorAll('.category-pill');
      pills.forEach(p => p.classList.remove('active'));
      loadProducts();
    });
  }

  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => loadProducts());
  }

  const applyPriceBtn = document.getElementById('apply-price-btn');
  if (applyPriceBtn) {
    applyPriceBtn.addEventListener('click', () => loadProducts());
  }
}

// Add item to cart action
async function addToCart(productId) {
  const user = await getAuthUser();
  if (!user) {
    showToast('Please sign in with your mobile number to add items to cart', 'error');
    setTimeout(() => {
      window.location.href = '/pages/login.html';
    }, 1200);
    return;
  }

  try {
    await apiRequest('/cart', {
      method: 'POST',
      body: { product_id: productId, quantity: 1 }
    });

    showToast('Inventory unit registered to cart', 'success');
    updateCartBadge();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
