/**
 * Fridge Observer — Notifications & History
 * notifications.js
 */

const ACTION_ICONS = {
  added: '➕',
  removed: '➖',
  updated: '✏️',
  expired: '⚠️',
};

/** Fetch activity log */
async function fetchActivityLog() {
  const res = await fetch('/api/notifications/activity-log?limit=50');
  if (!res.ok) throw new Error('Failed to fetch activity log');
  return res.json();
}

/** Fetch weekly report */
async function fetchWeeklyReport() {
  const res = await fetch('/api/notifications/weekly-report');
  if (!res.ok) throw new Error('Failed to fetch weekly report');
  return res.json();
}

/** Fetch streak */
async function fetchStreak() {
  const res = await fetch('/api/notifications/streak');
  if (!res.ok) throw new Error('Failed to fetch streak');
  return res.json();
}

/** Format a datetime string */
function formatDateTime(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

/** Render the activity log */
function renderActivityLog(entries) {
  const container = document.getElementById('activity-log');
  if (!container) return;

  if (!entries || entries.length === 0) {
    container.innerHTML = `
      <div class="empty-state-mini">
        <div class="empty-state-text">No activity discovered</div>
      </div>
    `;
    return;
  }

  container.innerHTML = entries.slice(0, 15).map(entry => `
    <div class="log-item-compact">
      <div class="log-indicator ${entry.action}"></div>
      <div class="log-info">
        <div class="log-main">
          <span class="log-subject">${escapeHtml(entry.item_name)}</span>
          <span class="log-verb">${entry.action}</span>
        </div>
        <div class="log-aside">${formatDateTime(entry.occurred_at)}</div>
      </div>
    </div>
  `).join('');
}

/** Render the waste report */
function renderWasteReport(report) {
  const container = document.getElementById('waste-report');
  if (!container) return;

  const thisWeek = report.this_week || {};
  const prevWeek = report.prev_week || {};

  const expired = thisWeek.expired || 0;
  const consumed = thisWeek.consumed || 0;
  const prevExpired = prevWeek.expired || 0;
  const prevConsumed = prevWeek.consumed || 0;

  const expiredDelta = expired - prevExpired;
  const consumedDelta = consumed - prevConsumed;

  const getDeltaClass = (val, inverted = false) => {
    if (val === 0) return 'delta-neutral';
    const isGood = inverted ? val <= 0 : val >= 0;
    return isGood ? 'delta-positive' : 'delta-negative';
  };

  const formatDelta = (val) => (val > 0 ? `+${val}` : `${val}`);

  container.innerHTML = `
    <div class="report-summary">
      <div class="report-item">
        <div class="report-meta">
          <span class="report-tag tag-ok">Consumed</span>
          <span class="report-trend ${getDeltaClass(consumedDelta)}">${formatDelta(consumedDelta)} vs last week</span>
        </div>
        <div class="report-count">${consumed} <small>items</small></div>
      </div>
      <div class="report-item">
        <div class="report-meta">
          <span class="report-tag tag-expired">⚠️ Expired</span>
          <span class="report-trend ${getDeltaClass(expiredDelta, true)}">${formatDelta(expiredDelta)} vs last week</span>
        </div>
        <div class="report-count">${expired} <small>items</small></div>
      </div>
    </div>
  `;
}

/** Render the streak */
function renderStreak(data) {
  const container = document.getElementById('streak-display');
  if (!container) return;

  if (!data.gamification_enabled) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-title">Gamification disabled</div>
        <div class="empty-state-text">Enable gamification in Settings to track your zero-waste streak.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="streak-card">
      <span class="streak-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 22 12 12"/></svg>
      </span>
      <div class="streak-number">${data.streak}</div>
      <div class="streak-label">Week${data.streak !== 1 ? 's' : ''} Zero-Waste Streak</div>
      <div class="streak-message">${data.message || ''}</div>
    </div>
  `;
}

/** Initialize the notifications section */
async function initNotifications() {
  // Load all data
  try {
    const [log, report, streak] = await Promise.all([
      fetchActivityLog(),
      fetchWeeklyReport(),
      fetchStreak(),
    ]);
    renderActivityLog(log);
    renderWasteReport(report);
    renderStreak(streak);
  } catch (err) {
    console.error('Failed to load notifications:', err);
  }
}

window.notificationsModule = { initNotifications, renderActivityLog };
