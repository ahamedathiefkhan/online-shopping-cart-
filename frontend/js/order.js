/**
 * Order Module — Checkout form, Place order, Order history, and tracking
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('checkout-items-list')) {
    initCheckoutPage();
  }

  if (document.getElementById('order-history-container')) {
    initOrderHistoryPage();
  }
});

// Checkout Page Initialization
async function initCheckoutPage() {
  const container = document.getElementById('checkout-items-list');
  const totalAmountEl = document.getElementById('checkout-total-amount');

  const user = await getAuthUser();
  if (!user) {
    window.location.href = '/pages/login.html';
    return;
  }

  try {
    const data = await apiRequest('/cart', { method: 'GET' });
    const items = data.items || [];

    if (items.length === 0) {
      showToast('Your cart is empty', 'error');
      setTimeout(() => {
        window.location.href = '/pages/cart.html';
      }, 1000);
      return;
    }

    container.innerHTML = items.map(item => `
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; color: var(--text-muted);">
        <div>${item.product ? item.product.name : ''} x ${item.quantity}</div>
        <div style="font-weight: 600; color: #ffffff;">${formatCurrency(item.total_price)}</div>
      </div>
    `).join('');

    const subtotal = data.total_amount || 0;
    const tax = subtotal * 0.18; // 18% GST
    const shipping = subtotal > 499 ? 0 : 49; // Free shipping over ₹499
    const total = subtotal > 0 ? (subtotal + tax + shipping) : 0;

    if (totalAmountEl) totalAmountEl.textContent = formatCurrency(total);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Checkout Form Submission
async function handleCheckoutFormSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const address = form.address.value.trim();
  const city = form.city.value.trim();
  const state = form.state.value.trim();
  const zip = form.zip.value.trim();

  const fullAddress = `${address}, ${city}, ${state} ${zip}`;

  const submitBtn = document.getElementById('place-order-btn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing Order...';
  }

  try {
    const res = await apiRequest('/orders', {
      method: 'POST',
      body: { shipping_address: fullAddress }
    });

    showToast('🎉 Order placed successfully!', 'success');
    updateCartBadge();

    setTimeout(() => {
      window.location.href = '/pages/order-history.html';
    }, 1200);
  } catch (err) {
    showToast(err.message, 'error');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Place Order';
    }
  }
}

// Order History Initialization
async function initOrderHistoryPage() {
  const container = document.getElementById('order-history-container');
  if (!container) return;

  const user = await getAuthUser();
  if (!user) {
    container.innerHTML = `
      <div style="text-align: center; padding: 4rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
        <h3>Please Sign In with Mobile OTP</h3>
        <p style="color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">Log in to view your past orders and track order status.</p>
        <a href="/pages/login.html" class="btn-primary">Sign In</a>
      </div>
    `;
    return;
  }

  try {
    const orders = await apiRequest('/orders', { method: 'GET' });

    if (!orders || orders.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 4rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
          <div style="font-size: 3.5rem; margin-bottom: 1rem;">📦</div>
          <h3>No Orders Yet</h3>
          <p style="color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">You haven't placed any orders yet.</p>
          <a href="/pages/index.html" class="btn-primary">Start Shopping</a>
        </div>
      `;
      return;
    }

    container.innerHTML = orders.map(order => `
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 1.5rem;">
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem; margin-bottom: 1rem;">
          <div>
            <div style="font-weight: 700; font-size: 1.1rem;">Order #${order.id}</div>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
              Placed on ${new Date(order.created_at).toLocaleDateString()} at ${new Date(order.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 1.5rem;">
            <span class="badge-status status-${order.status}">${order.status}</span>
            <div style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 800; color: #ffffff;">
              ${formatCurrency(order.total_amount)}
            </div>
          </div>
        </div>

        <div style="margin-bottom: 1rem;">
          <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;">Shipping Address:</div>
          <div style="font-size: 0.95rem; font-weight: 500;">📍 ${order.shipping_address}</div>
        </div>

        <div style="background: rgba(15, 23, 42, 0.6); border-radius: var(--radius-md); padding: 1rem;">
          <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.75rem; text-transform: uppercase;">
            Order Items (${order.items.length})
          </div>
          ${order.items.map(item => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed rgba(255,255,255,0.08);">
              <div style="display: flex; align-items: center; gap: 0.75rem;">
                <img src="${item.product_image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'}" alt="" style="width: 42px; height: 42px; object-fit: cover; border-radius: 6px;" />
                <div>
                  <div style="font-weight: 600; font-size: 0.95rem;">${item.product_name}</div>
                  <div style="font-size: 0.8rem; color: var(--text-muted);">${formatCurrency(item.price_at_purchase)} x ${item.quantity}</div>
                </div>
              </div>
              <div style="font-weight: 700;">${formatCurrency(item.subtotal)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: #ef4444;">
        <p>Error loading orders: ${err.message}</p>
      </div>
    `;
  }
}
