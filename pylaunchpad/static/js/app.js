/**
 * PyLaunchpad Client Controller: Auth, Dashboard, and Polar Checkout.
 */

const PyLaunchpad = {
  getToken() {
    return localStorage.getItem("pylp_token");
  },

  setToken(token) {
    localStorage.setItem("pylp_token", token);
  },

  clearToken() {
    localStorage.removeItem("pylp_token");
  },

  async apiRequest(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    headers["Content-Type"] = "application/json";

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    if (response.status === 401 && !options.skipAuthRedirect) {
      this.clearToken();
      if (window.location.pathname.startsWith("/dashboard")) {
        window.location.href = "/login";
      }
    }

    return response;
  },

  async handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    const password = form.password.value;
    const errorEl = document.getElementById("login-error");

    if (errorEl) errorEl.style.display = "none";

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await res.json();
      this.setToken(data.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    }
  },

  async handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    const password = form.password.value;
    const fullName = form.full_name.value;
    const errorEl = document.getElementById("register-error");

    if (errorEl) errorEl.style.display = "none";

    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }

      // Auto login after registration
      const loginRes = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (loginRes.ok) {
        const loginData = await loginRes.json();
        this.setToken(loginData.access_token);
        window.location.href = "/dashboard";
      } else {
        window.location.href = "/login";
      }
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    }
  },

  async loadDashboard() {
    const token = this.getToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      // 1. Fetch user profile
      const userRes = await this.apiRequest("/api/v1/auth/me");
      if (!userRes.ok) return;
      const user = await userRes.json();
      const userEl = document.getElementById("user-name");
      if (userEl) userEl.textContent = user.full_name || user.email;

      // 2. Fetch API keys
      this.loadApiKeys();

      // 3. Fetch Orders
      this.loadOrders();
    } catch (err) {
      console.error("Failed to load dashboard:", err);
    }
  },

  async loadApiKeys() {
    const res = await this.apiRequest("/api/v1/apikeys");
    if (!res.ok) return;
    const keys = await res.json();
    const container = document.getElementById("api-keys-list");
    if (!container) return;

    if (keys.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No API keys generated yet.</p>`;
      return;
    }

    container.innerHTML = keys
      .map(
        (k) => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
        <div>
          <strong>${k.name}</strong>
          <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary);">${k.key_prefix}...</div>
        </div>
        <button class="btn btn-secondary btn-sm" onclick="PyLaunchpad.revokeApiKey(${k.id})">Revoke</button>
      </div>
    `
      )
      .join("");
  },

  async createApiKey(event) {
    event.preventDefault();
    const name = document.getElementById("key-name").value;
    if (!name) return;

    const res = await this.apiRequest("/api/v1/apikeys", {
      method: "POST",
      body: JSON.stringify({ name }),
    });

    if (res.ok) {
      const data = await res.json();
      document.getElementById("key-name").value = "";
      alert(`API Key Created: ${data.api_key}\n\nCopy and store it now. You will not be able to view it again.`);
      this.loadApiKeys();
    }
  },

  async revokeApiKey(id) {
    if (!confirm("Are you sure you want to revoke this API key?")) return;
    const res = await this.apiRequest(`/api/v1/apikeys/${id}`, { method: "DELETE" });
    if (res.ok) {
      this.loadApiKeys();
    }
  },

  async loadOrders() {
    const res = await this.apiRequest("/api/v1/billing/orders");
    if (!res.ok) return;
    const orders = await res.json();
    const container = document.getElementById("orders-list");
    if (!container) return;

    if (orders.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No purchases found.</p>`;
      return;
    }

    container.innerHTML = orders
      .map(
        (o) => `
      <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
        <div>
          <strong>${o.product_name}</strong>
          <div style="font-size: 0.8rem; color: var(--text-muted);">${new Date(o.created_at).toLocaleDateString()}</div>
        </div>
        <div style="font-weight: 700; color: var(--accent-emerald);">$${(o.amount / 100).toFixed(2)} ${o.currency.toUpperCase()}</div>
      </div>
    `
      )
      .join("");
  },

  logout() {
    this.clearToken();
    window.location.href = "/login";
  },
};
