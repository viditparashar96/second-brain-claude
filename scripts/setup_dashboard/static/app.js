/**
 * Second Brain Setup Dashboard — Frontend Logic
 *
 * Handles: status loading, OAuth flows, token modals, setup completion.
 */

// ──────────── State ────────────

let currentStatus = {};
let pollTimer = null;

// ──────────── Init ────────────

document.addEventListener('DOMContentLoaded', () => {
  loadStatus();
  handleAuthRedirect();
});

// ──────────── Status ────────────

async function loadStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    currentStatus = data;
    populateForm(data);
    updateIntegrationBadges(data.integrations);
  } catch (e) {
    console.error('Failed to load status:', e);
  }
}

function populateForm(data) {
  const user = data.user || {};

  if (user.name) {
    document.getElementById('user-name').value = user.name;
  }
  if (user.role) {
    document.getElementById('user-role').value = user.role;
  }
  if (user.timezone) {
    const tz = document.getElementById('user-timezone');
    // Try exact match first, then partial
    for (const opt of tz.options) {
      if (opt.value === user.timezone) {
        tz.value = user.timezone;
        break;
      }
    }
  }
  if (data.proactivity) {
    const radio = document.querySelector(`input[name="proactivity"][value="${data.proactivity}"]`);
    if (radio) radio.checked = true;
  }
  if (data.memory_level) {
    const radio = document.querySelector(`input[name="memory_level"][value="${data.memory_level}"]`);
    if (radio) radio.checked = true;
  }
}

function updateIntegrationBadges(integrations) {
  if (!integrations) return;

  const services = ['gmail', 'gcal', 'github', 'asana', 'slack'];

  for (const svc of services) {
    const info = integrations[svc];
    if (!info) continue;

    const badge = document.getElementById(`${svc}-badge`);
    const detail = document.getElementById(`${svc}-detail`);
    if (!badge) continue;

    if (info.coming_soon) {
      // Already styled in HTML
      continue;
    }

    if (info.connected) {
      badge.className = 'badge badge-connected';
      badge.innerHTML = '<span class="badge-dot"></span> Connected';
      badge.onclick = null;
      badge.style.cursor = 'default';

      // Update detail text with account info
      if (detail) {
        if (svc === 'gmail' && info.email) {
          detail.textContent = info.email;
        } else if (svc === 'github' && info.username) {
          detail.textContent = '@' + info.username;
        } else if (svc === 'asana' && info.name) {
          detail.textContent = info.name;
        } else if (svc === 'gcal' && info.calendars) {
          detail.textContent = info.calendars + ' calendar(s) found';
        }
      }
    } else if (info.error && !info.error.includes('Not authenticated') && !info.error.includes('not set')) {
      badge.className = 'badge badge-error';
      badge.innerHTML = '<span class="badge-dot"></span> Error';
    }
    // else: stays as "Connect" (default from HTML)
  }
}

// ──────────── Auth Redirect Handling ────────────

function handleAuthRedirect() {
  const params = new URLSearchParams(window.location.search);

  if (params.get('auth_success') === 'google') {
    const services = (params.get('services') || '').split(',');
    const names = services.map(s => s === 'gmail' ? 'Gmail' : s === 'gcal' ? 'Calendar' : s).join(' + ');
    showToast(`${names} connected!`, 'success');
    // Clean URL
    window.history.replaceState({}, '', '/');
    // Refresh status
    loadStatus();
  }

  if (params.get('auth_error')) {
    showToast('Connection failed: ' + params.get('auth_error'), 'error');
    window.history.replaceState({}, '', '/');
  }

  if (params.get('google_setup') === 'needed') {
    window.history.replaceState({}, '', '/');
    openModal('google');
  }
}

// ──────────── Google OAuth (Gmail + Calendar) ────────────

function connectGoogle() {
  // Redirect to Google OAuth with combined scopes
  window.location.href = '/api/auth/google?scopes=all';
}

// ──────────── Token Modals (GitHub, Asana) ────────────

function openModal(service) {
  const modal = document.getElementById(`modal-${service}`);
  if (modal) {
    modal.classList.add('active');
    // Focus input
    const input = document.getElementById(`${service}-token`);
    if (input) {
      input.value = '';
      setTimeout(() => input.focus(), 100);
    }
    // Clear errors
    const error = document.getElementById(`${service}-error`);
    if (error) {
      error.textContent = '';
      error.classList.remove('visible');
    }
  }
}

function closeModal(service) {
  const modal = document.getElementById(`modal-${service}`);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
  }
});

async function submitToken(service) {
  const input = document.getElementById(`${service}-token`);
  const error = document.getElementById(`${service}-error`);
  const confirm = document.getElementById(`${service}-confirm`);
  const token = input ? input.value.trim() : '';

  if (!token) {
    error.textContent = 'Please paste your token';
    error.classList.add('visible');
    return;
  }

  // Show loading
  confirm.disabled = true;
  confirm.textContent = 'Verifying...';
  error.classList.remove('visible');

  try {
    const res = await fetch(`/api/auth/${service}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });

    const data = await res.json();

    if (data.connected) {
      closeModal(service);
      showToast(`${capitalize(service)} connected!`, 'success');
      loadStatus();
    } else {
      error.textContent = data.error || 'Verification failed. Check your token.';
      error.classList.add('visible');
    }
  } catch (e) {
    error.textContent = 'Connection error. Is the server running?';
    error.classList.add('visible');
  } finally {
    confirm.disabled = false;
    confirm.textContent = 'Connect';
  }
}

// ──────────── Complete Setup ────────────

async function completeSetup() {
  const btn = document.getElementById('btn-complete');
  const name = document.getElementById('user-name').value.trim();
  const role = document.getElementById('user-role').value;
  const timezone = document.getElementById('user-timezone').value;
  const proactivity = document.querySelector('input[name="proactivity"]:checked')?.value || 'assistant';
  const memory_level = document.querySelector('input[name="memory_level"]:checked')?.value || 'full';

  // Validation
  if (!name) {
    showToast('Please enter your name', 'error');
    document.getElementById('user-name').focus();
    return;
  }

  // Show loading
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Setting up...';

  try {
    // Save profile first
    await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, role, timezone, proactivity, memory_level }),
    });

    // Complete setup
    const res = await fetch('/api/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user: { name, role, timezone },
        proactivity,
        services: {
          heartbeat: document.getElementById('svc-heartbeat').checked,
          indexer: document.getElementById('svc-indexer').checked,
          reflection: document.getElementById('svc-reflection').checked,
        },
        shutdown: true,
      }),
    });

    const data = await res.json();

    if (data.status === 'complete') {
      // Show success screen
      document.getElementById('setup-form').style.display = 'none';
      const successScreen = document.getElementById('success-screen');
      successScreen.classList.add('active');

      if (data.vault_path) {
        document.getElementById('success-vault').textContent = data.vault_path;
      }
      if (data.config_path) {
        document.getElementById('success-config').textContent = data.config_path;
      }

      // Show connected integrations
      const intDiv = document.getElementById('success-integrations');
      if (data.integrations) {
        const connected = Object.entries(data.integrations)
          .filter(([_, v]) => v.enabled)
          .map(([k, _]) => capitalize(k));
        if (connected.length > 0) {
          intDiv.textContent = 'Connected: ' + connected.join(', ');
        } else {
          intDiv.textContent = 'No integrations connected (you can add them later)';
        }
      }
    }
  } catch (e) {
    showToast('Setup failed: ' + e.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Complete Setup';
  }
}

// ──────────── Toast ────────────

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.classList.add('visible');

  setTimeout(() => {
    toast.classList.remove('visible');
  }, 4000);
}

// ──────────── Utils ────────────

function capitalize(str) {
  if (str === 'gcal') return 'Google Calendar';
  return str.charAt(0).toUpperCase() + str.slice(1);
}
