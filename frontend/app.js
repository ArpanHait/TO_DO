let API_BASE = 'http://127.0.0.1:8000'; // Default local fallback

// Load config dynamically
async function loadConfig() {
  try {
    const res = await fetch('/config.json');
    if (res.ok) {
      const data = await res.json();
      if (data.API_BASE) {
        API_BASE = data.API_BASE.replace(/\/$/, ''); // strip trailing slash
      }
    }
  } catch (e) {
    console.warn('Failed to load config.json, using fallback API_BASE:', API_BASE);
  }
}

function getToken() {
  return localStorage.getItem('token') || '';
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user')) || null;
  } catch (e) {
    return null;
  }
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function logoutLocal() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = 'index.html';
}

async function logout() {
  const token = getToken();
  if (token) {
    try {
      await fetch(`${API_BASE}/api/auth/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`
        }
      });
    } catch (e) {
      console.error('Logout error:', e);
    }
  }
  logoutLocal();
}

function getAvatarUrl(url) {
  if (!url) return '';
  if (url.startsWith('http') || url.startsWith('data:')) return url;
  return `${API_BASE}${url}`;
}

// Global initialization promise
const configPromise = loadConfig();
