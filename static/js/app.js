/**
 * Fridge Observer — App Entry Point
 * app.js: Navigation, WebSocket wiring, global utilities
 */

// ── Global Utilities ─────────────────────────────────────────

/** Escape HTML to prevent XSS */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/** Show a toast notification */
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'polite');

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  toast.innerHTML = `<span aria-hidden="true">${icons[type] || 'ℹ'}</span> ${escapeHtml(message)}`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-out');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, duration);
}

// Make utilities global
window.escapeHtml = escapeHtml;
window.showToast = showToast;

// ── Navigation ───────────────────────────────────────────────

const SECTIONS = ['inventory', 'settings', 'sustainability'];
let _activeSection = 'inventory';
let _sectionInitialized = {};

function navigateTo(section) {
  if (!SECTIONS.includes(section)) return;

  // Update active section
  _activeSection = section;

  // Show/hide content sections
  SECTIONS.forEach(s => {
    const el = document.getElementById(`section-${s}`);
    if (el) el.classList.toggle('active', s === section);
  });

  // Update topbar nav items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.section === section);
    item.setAttribute('aria-current', item.dataset.section === section ? 'page' : 'false');
  });

  // Update notification button active state
  const notifBtn = document.getElementById('btn-notifications');
  if (notifBtn) {
    notifBtn.classList.toggle('active', section === 'notifications');
  }

  // Initialize section on first visit
  if (!_sectionInitialized[section]) {
    _sectionInitialized[section] = true;
    initSection(section);
  }

  // Close notification panel and account dropdown
  closeNotificationPanel();
  closeAccountDropdown();

  // Update URL hash
  history.replaceState(null, '', `#${section}`);
}

function initSection(section) {
  switch (section) {
    case 'inventory':
      if (window.inventoryModule) window.inventoryModule.refreshInventory();
      if (window.recipesModule) window.recipesModule.refreshRecipes();
      break;
    case 'notifications':
      if (window.notificationsModule) window.notificationsModule.initNotifications();
      break;
    case 'settings':
      if (window.settingsModule) window.settingsModule.initSettings();
      break;
    case 'sustainability':
      if (window.sustainabilityModule) window.sustainabilityModule.initSustainability();
      break;
  }
}

// ── Account Dropdown ─────────────────────────────────────────

function toggleAccountDropdown() {
  const dropdown = document.getElementById('account-dropdown');
  if (dropdown) {
    dropdown.classList.toggle('show');
  }
}

function closeAccountDropdown() {
  const dropdown = document.getElementById('account-dropdown');
  if (dropdown) {
    dropdown.classList.remove('show');
  }
}

function initAccountDropdown() {
  const accountBtn = document.getElementById('btn-account');
  if (accountBtn) {
    accountBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAccountDropdown();
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    const container = document.querySelector('.account-menu-container');
    if (container && !container.contains(e.target)) {
      closeAccountDropdown();
    }
  });

  // Settings button inside dropdown
  const settingsBtn = document.getElementById('btn-settings');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', () => {
      navigateTo('settings');
    });
  }
}

// ── Notification Panel ───────────────────────────────────────

let _notificationsLoaded = false;

function toggleNotificationPanel() {
  const panel = document.getElementById('notification-panel');
  if (panel) {
    const isShowing = panel.classList.toggle('show');
    // Load notifications on first open
    if (isShowing && !_notificationsLoaded) {
      _notificationsLoaded = true;
      if (window.notificationsModule) {
        window.notificationsModule.initNotifications();
      }
    }
    // Close account dropdown if open
    closeAccountDropdown();
  }
}

function closeNotificationPanel() {
  const panel = document.getElementById('notification-panel');
  if (panel) {
    panel.classList.remove('show');
  }
}

function initNotificationButton() {
  const btn = document.getElementById('btn-notifications');
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleNotificationPanel();
    });
  }

  // Close panel when clicking outside
  document.addEventListener('click', (e) => {
    const container = document.querySelector('.notif-menu-container');
    if (container && !container.contains(e.target)) {
      closeNotificationPanel();
    }
  });
}

// ── WebSocket Wiring ─────────────────────────────────────────

function initWebSocket() {
  const ws = window.fridgeWS;
  if (!ws) return;

  // Inventory updates
  ws.on('inventory_update', (payload) => {
    if (window.inventoryModule && _activeSection === 'inventory') {
      window.inventoryModule.renderInventoryGrid(payload);
    }
    // Also refresh EcoScan item list when inventory changes
    if (window.sustainabilityModule && _activeSection === 'sustainability') {
      window.sustainabilityModule.refreshItems();
    }
  });

  // Notifications
  ws.on('notification', (payload) => {
    const level = payload.level === 'warning' ? 'warning' : 'info';
    showToast(payload.message, level);
  });

  // Temperature updates
  ws.on('temperature_update', (payload) => {
    if (window.settingsModule) {
      window.settingsModule.updateTemperatureDisplay(payload);
    }
  });

  // Connect
  ws.connect();
}

// ── Connection Banner ────────────────────────────────────────

function initConnectionBanner() {
  const closeBtn = document.querySelector('.connection-banner-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      document.querySelector('.connection-banner')?.classList.remove('visible');
    });
  }
}

// ── App Initialization ───────────────────────────────────────

async function initAuth() {
  try {
    const res = await fetch('/auth/me', { credentials: 'include' });
    if (!res.ok) {
      window.location.href = '/login';
      return false;
    }
    const user = await res.json();
    // Show user name in account dropdown
    const dropdownName = document.getElementById('dropdown-user-name');
    if (dropdownName) {
      dropdownName.textContent = user.display_name || user.email;
    }
    return true;
  } catch {
    window.location.href = '/login';
    return false;
  }
}

function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
    window.location.href = '/login';
  });
}

function initApp() {
  // Set up topbar nav items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const section = item.dataset.section;
      if (section) navigateTo(section);
    });

    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const section = item.dataset.section;
        if (section) navigateTo(section);
      }
    });
  });

  // Initialize account dropdown
  initAccountDropdown();

  // Initialize notification button
  initNotificationButton();

  // Initialize connection banner
  initConnectionBanner();

  // Initialize WebSocket
  initWebSocket();

  // Navigate to initial section (from hash or default)
  const hash = location.hash.replace('#', '');
  const initialSection = SECTIONS.includes(hash) ? hash : 'inventory';
  navigateTo(initialSection);

  // Initialize inventory immediately (it's the default section)
  if (window.inventoryModule) {
    initInventory();
  }
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', async () => {
    const authed = await initAuth();
    if (authed) { initLogout(); initApp(); }
  });
} else {
  initAuth().then(authed => { if (authed) { initLogout(); initApp(); } });
}
