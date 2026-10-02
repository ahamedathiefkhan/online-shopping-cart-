/**
 * Cart Module — Cart page rendering, item quantity updates, item removal, and order summary calculation
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('cart-items-container')) {
    initCartPage();
  }
});

async function initCartPage() {
  await renderCartView();
}

async function renderCartView() {
  const container = document.getElementById('cart-items-container');
  const summaryContainer = document.getElementById('cart-summary-box');

  if (!container) return;

  const user = await getAuthUser();
  if (!user) {
    container.innerHTML = `
      <div style="text-align: center; padding: 4rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
        <h3>Please Sign In with Mobile OTP</h3>
        <p style="color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">You need to be signed in to view your shopping cart.</p>
        <a href="/pages/login.html" class="btn-primary">Sign In Now</a>
      </div>
    `;
    if (summaryContainer) summaryContainer.style.display = 'none';
    return;
  }

  try {
    const data = await apiRequest('/cart', { method: 'GET' });
    const items = data.items || [];

    if (items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 4rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
          <div style="font-size: 3.5rem; margin-bottom: 1rem;">🛍️</div>
          <h3>Your cart is empty</h3>
          <p style="color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">Explore our catalog and find something you love!</p>
          <a href="/pages/index.html" class="btn-primary">Browse Products</a>
        </div>
      `;
      if (summaryContainer) summaryContainer.style.display = 'none';
      return;
    }

    if (summaryContainer) summaryContainer.style.display = 'block';

    container.innerHTML = items.map(item => `
      <div class="cart-item-row">
        <img src="${item.product ? item.product.image_url : ''}" alt="${item.product ? item.product.name : ''}" class="cart-item-img" />
        <div class="cart-item-info">
          <div class="cart-item-title">${item.product ? item.product.name : 'Unknown Product'}</div>
          <div class="cart-item-price">${formatCurrency(item.product ? item.product.price : 0)} each</div>
        </div>
        <div class="qty-control">
          <button class="qty-btn" onclick="updateItemQuantity(${item.id}, ${item.quantity - 1})">-</button>
          <span class="qty-val">${item.quantity}</span>
          <button class="qty-btn" onclick="updateItemQuantity(${item.id}, ${item.quantity + 1})">+</button>
        </div>
        <div style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; min-width: 90px; text-align: right;">
          ${formatCurrency(item.total_price)}
        </div>
        <button onclick="removeCartItem(${item.id})" class="btn-danger" style="padding: 0.4rem 0.6rem;" title="Remove Item">
          🗑️
        </button>
      </div>
    `).join('');

    renderOrderSummary(data);
  } catch (err) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: #ef4444;">
        <p>Error loading cart: ${err.message}</p>
      </div>
    `;
  }
}

function renderOrderSummary(cartData) {
  const subtotal = cartData.total_amount || 0;
  const tax = subtotal * 0.18; // 18% GST
  const shipping = subtotal > 499 ? 0 : 49; // Free shipping over ₹499
  const grandTotal = subtotal > 0 ? (subtotal + tax + shipping) : 0;

  const subtotalEl = document.getElementById('summary-subtotal');
  const taxEl = document.getElementById('summary-tax');
  const shippingEl = document.getElementById('summary-shipping');
  const totalEl = document.getElementById('summary-grand-total');

  if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
  if (taxEl) taxEl.textContent = formatCurrency(tax);
  if (shippingEl) shippingEl.textContent = (subtotal > 0 && shipping === 0) ? 'FREE' : (subtotal > 0 ? formatCurrency(shipping) : '₹0.00');
  if (totalEl) totalEl.textContent = formatCurrency(grandTotal);
}

async function updateItemQuantity(itemId, newQuantity) {
  try {
    await apiRequest(`/cart/${itemId}`, {
      method: 'PUT',
      body: { quantity: newQuantity }
    });

    updateCartBadge();
    await renderCartView();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function removeCartItem(itemId) {
  try {
    await apiRequest(`/cart/${itemId}`, { method: 'DELETE' });
    showToast('Item removed', 'success');
    updateCartBadge();
    await renderCartView();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleClearCart() {
  if (!confirm('Are you sure you want to clear your entire cart?')) return;

  try {
    await apiRequest('/cart/clear', { method: 'DELETE' });
    showToast('Cart cleared', 'success');
    updateCartBadge();
    await renderCartView();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
