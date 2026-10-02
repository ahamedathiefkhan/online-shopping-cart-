/**
 * Admin Module — Dashboard analytics, product CRUD, order status management
 */

let currentAdminTab = 'products';
let editingProductId = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('admin-dashboard-root')) {
    initAdminDashboard();
  }
});

async function initAdminDashboard() {
  const user = await getAuthUser();
  if (!user || user.role !== 'admin') {
    showToast('Admin access required', 'error');
    setTimeout(() => {
      window.location.href = '/pages/login.html';
    }, 1000);
    return;
  }

  await loadDashboardMetrics();
  await loadAdminProducts();
  await loadAdminCategoriesSelect();
}

// Load Dashboard Metrics
async function loadDashboardMetrics() {
  try {
    const stats = await apiRequest('/admin/dashboard', { method: 'GET' });

    const revEl = document.getElementById('kpi-revenue');
    const ordersEl = document.getElementById('kpi-orders');
    const productsEl = document.getElementById('kpi-products');
    const usersEl = document.getElementById('kpi-users');

    if (revEl) revEl.textContent = formatCurrency(stats.total_revenue);
    if (ordersEl) ordersEl.textContent = stats.total_orders;
    if (productsEl) productsEl.textContent = stats.total_products;
    if (usersEl) usersEl.textContent = stats.total_users;
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Switch Tabs
function switchAdminTab(tabName, element) {
  currentAdminTab = tabName;
  document.querySelectorAll('.admin-tab').forEach(tab => tab.classList.remove('active'));
  if (element) element.classList.add('active');

  const productsView = document.getElementById('admin-products-view');
  const ordersView = document.getElementById('admin-orders-view');

  if (tabName === 'products') {
    if (productsView) productsView.style.display = 'block';
    if (ordersView) ordersView.style.display = 'none';
    loadAdminProducts();
  } else if (tabName === 'orders') {
    if (productsView) productsView.style.display = 'none';
    if (ordersView) ordersView.style.display = 'block';
    loadAdminOrders();
  }
}

// Load Product Table
async function loadAdminProducts() {
  const tableBody = document.getElementById('admin-products-table-body');
  if (!tableBody) return;

  try {
    const products = await apiRequest('/products', { method: 'GET' });

    if (!products || products.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No products in catalog.</td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = products.map(p => `
      <tr>
        <td>
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <img src="${p.image_url}" alt="" style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px;" />
            <div style="font-weight: 600;">${p.name}</div>
          </div>
        </td>
        <td>${p.category_name}</td>
        <td style="font-weight: 700;">${formatCurrency(p.price)}</td>
        <td>
          <span style="font-weight: 600; color: ${p.stock_quantity > 5 ? '#10b981' : '#f59e0b'};">
            ${p.stock_quantity}
          </span>
        </td>
        <td>
          <button onclick="openEditProductModal(${p.id})" class="btn-outline" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin-right: 0.4rem;">✏️ Edit</button>
          <button onclick="deleteProduct(${p.id})" class="btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">🗑️ Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Load Categories into Select Dropdown in Modal
async function loadAdminCategoriesSelect() {
  const select = document.getElementById('modal-product-category');
  if (!select) return;

  try {
    const categories = await apiRequest('/products/categories', { method: 'GET' });
    select.innerHTML = categories.map(c => `
      <option value="${c.id}">${c.name}</option>
    `).join('');
  } catch (err) {
    console.error('Failed to load categories for modal', err);
  }
}

// Open Modal for New Product
function openCreateProductModal() {
  editingProductId = null;
  const title = document.getElementById('modal-title');
  if (title) title.textContent = 'Add New Product';

  const form = document.getElementById('product-form');
  if (form) form.reset();

  const modal = document.getElementById('product-modal-overlay');
  if (modal) modal.classList.add('active');
}

// Open Modal for Edit Product
async function openEditProductModal(productId) {
  editingProductId = productId;
  const title = document.getElementById('modal-title');
  if (title) title.textContent = 'Edit Product';

  try {
    const product = await apiRequest(`/products/${productId}`, { method: 'GET' });
    
    const form = document.getElementById('product-form');
    if (form) {
      form.name.value = product.name;
      form.description.value = product.description || '';
      form.price.value = product.price;
      form.stock_quantity.value = product.stock_quantity;
      if (form.category_id && product.category_id) {
        form.category_id.value = product.category_id;
      }
      form.image_url.value = product.image_url || '';
    }

    const modal = document.getElementById('product-modal-overlay');
    if (modal) modal.classList.add('active');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function closeProductModal() {
  const modal = document.getElementById('product-modal-overlay');
  if (modal) modal.classList.remove('active');
}

// Submit Product Modal Form
async function handleProductFormSubmit(event) {
  event.preventDefault();
  const form = event.target;

  const payload = {
    name: form.name.value.trim(),
    description: form.description.value.trim(),
    price: parseFloat(form.price.value),
    stock_quantity: parseInt(form.stock_quantity.value, 10),
    category_id: form.category_id ? parseInt(form.category_id.value, 10) : null,
    image_url: form.image_url.value.trim()
  };

  try {
    if (editingProductId) {
      await apiRequest(`/admin/products/${editingProductId}`, {
        method: 'PUT',
        body: payload
      });
      showToast('Product updated successfully!', 'success');
    } else {
      await apiRequest('/admin/products', {
        method: 'POST',
        body: payload
      });
      showToast('New product created!', 'success');
    }

    closeProductModal();
    await loadAdminProducts();
    await loadDashboardMetrics();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Delete Product
async function deleteProduct(productId) {
  if (!confirm('Are you sure you want to delete this product?')) return;

  try {
    await apiRequest(`/admin/products/${productId}`, { method: 'DELETE' });
    showToast('Product deleted', 'success');
    await loadAdminProducts();
    await loadDashboardMetrics();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Load Orders Table for Admin
async function loadAdminOrders() {
  const tableBody = document.getElementById('admin-orders-table-body');
  if (!tableBody) return;

  try {
    const orders = await apiRequest('/admin/orders', { method: 'GET' });

    if (!orders || orders.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No orders placed yet.</td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = orders.map(o => `
      <tr>
        <td style="font-weight: 700;">#${o.id}</td>
        <td>
          <div>${o.user_name}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono);">📱 ${o.user_phone || o.user_email || 'N/A'}</div>
        </td>
        <td style="font-weight: 700;">${formatCurrency(o.total_amount)}</td>
        <td style="font-size: 0.85rem; max-width: 200px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;" title="${o.shipping_address}">
          ${o.shipping_address}
        </td>
        <td>
          <select onchange="updateOrderStatus(${o.id}, this.value)" class="select-control" style="padding: 0.35rem 0.65rem; font-size: 0.85rem;">
            <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
            <option value="processing" ${o.status === 'processing' ? 'selected' : ''}>Processing</option>
            <option value="shipped" ${o.status === 'shipped' ? 'selected' : ''}>Shipped</option>
            <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
            <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </td>
        <td style="font-size: 0.8rem; color: var(--text-muted);">
          ${new Date(o.created_at).toLocaleDateString()}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Update Order Status
async function updateOrderStatus(orderId, newStatus) {
  try {
    await apiRequest(`/admin/orders/${orderId}/status`, {
      method: 'PUT',
      body: { status: newStatus }
    });

    showToast(`Order #${orderId} status updated to ${newStatus}`, 'success');
    await loadDashboardMetrics();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
