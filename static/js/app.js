// Auth State
let authToken = localStorage.getItem('auth_token');
let userId = null;

document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        showDashboard();
    } else {
        showLogin();
    }

    // Auth Event Listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignup);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('show-signup').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form').parentElement.parentElement.style.display = 'none';
        document.getElementById('signup-card').style.display = 'block';
    });
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('signup-card').style.display = 'none';
        document.getElementById('login-form').parentElement.parentElement.style.display = 'block';
    });

    // Dashboard Event Listeners
    document.getElementById('settings-form').addEventListener('submit', updateSettings);
    document.getElementById('connect-whatsapp-btn').addEventListener('click', linkWhatsApp);

    // Initial Load if logged in
    if (authToken) {
        loadDashboardData();
        connectWebSocket();
    }
});

function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
}

function showLogin() {
    document.getElementById('auth-container').style.display = 'block';
    document.getElementById('dashboard-container').style.display = 'none';
    document.getElementById('login-form').parentElement.parentElement.style.display = 'block';
    document.getElementById('signup-card').style.display = 'none';
}

function showDashboard() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';

    const payload = parseJwt(authToken);
    if (payload) {
        userId = payload.sub;
        // Update Webhook URL display
        const webhookUrl = `${window.location.origin}/api/v1/webhooks/${userId}/orders/create`;
        document.getElementById('webhook-url').textContent = webhookUrl;
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            localStorage.setItem('auth_token', authToken);
            showDashboard();
            loadDashboardData();
            connectWebSocket();
        } else {
            alert('Login failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Login error');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    try {
        const res = await fetch('/api/v1/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            localStorage.setItem('auth_token', authToken);
            showDashboard();
            loadDashboardData();
            connectWebSocket();
        } else {
            const err = await res.json();
            alert('Signup failed: ' + err.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Signup error');
    }
}

function handleLogout() {
    localStorage.removeItem('auth_token');
    authToken = null;
    userId = null;
    showLogin();
}

async function authFetch(url, options = {}) {
    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = `Bearer ${authToken}`;

    const res = await fetch(url, options);
    if (res.status === 401) {
        handleLogout();
        throw new Error('Unauthorized');
    }
    return res;
}

async function loadDashboardData() {
    fetchOrders();
    fetchConfigs();
    fetchAnalytics();
}

async function fetchOrders() {
    try {
        const res = await authFetch('/api/v1/admin/orders');
        const orders = await res.json();
        const tbody = document.getElementById('orders-table-body');
        tbody.innerHTML = '';

        if (orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No orders found</td></tr>';
            return;
        }

        orders.forEach(order => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${order.order_number}</td>
                <td>${order.customer_name}</td>
                <td>${order.total_price}</td>
                <td><span class="badge ${getStatusBadge(order.status)}">${order.status}</span></td>
                <td>${order.delivery_slot || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching orders:', error);
    }
}

function getStatusBadge(status) {
    switch (status) {
        case 'confirmed': return 'bg-success';
        case 'pending': return 'bg-warning text-dark';
        case 'cancelled': return 'bg-danger';
        case 'delivered': return 'bg-info text-dark';
        default: return 'bg-secondary';
    }
}

async function fetchConfigs() {
    try {
        const res = await authFetch('/api/v1/admin/configs');
        const configs = await res.json();
        const delayConfig = configs.find(c => c.key === 'confirmation_delay_minutes');
        if (delayConfig) {
            document.getElementById('delay-input').value = delayConfig.value;
        }
    } catch (error) {
        console.error('Error fetching configs:', error);
    }
}

async function updateSettings(e) {
    e.preventDefault();
    const delay = document.getElementById('delay-input').value;
    try {
        await authFetch('/api/v1/admin/configs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                key: 'confirmation_delay_minutes',
                value: delay,
                description: 'Delay before sending confirmation (minutes)'
            })
        });
        alert('Settings saved!');
    } catch (error) {
        console.error('Error updating settings:', error);
        alert('Failed to save settings');
    }
}

async function fetchAnalytics() {
    try {
        const res = await authFetch('/api/v1/admin/analytics');
        const data = await res.json();

        document.getElementById('total-orders').textContent = data.total_orders;
        document.getElementById('conf-rate').textContent = data.confirmed_rate.toFixed(1) + '%';
        document.getElementById('cancel-rate').textContent = data.cancellation_rate.toFixed(1) + '%';
        document.getElementById('success-rate').textContent = data.delivery_success_rate.toFixed(1) + '%';
    } catch (error) {
        console.error('Error fetching analytics:', error);
    }
}

async function linkWhatsApp() {
    try {
        const res = await authFetch('/api/v1/admin/whatsapp/link', {
            method: 'POST'
        });
        const data = await res.json();
        alert(data.message);
    } catch (error) {
        console.error('Error linking WhatsApp:', error);
        alert('Failed to initiate linking');
    }
}

// WebSocket for Real-time Updates
let ws;
function connectWebSocket() {
    if (ws) return; // Already connected

    // Use secure WebSocket if on https
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/orders`);

    ws.onopen = () => {
        console.log("Connected to WebSocket");
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'new_order') {
            prependOrder(message.data);
        } else if (message.type === 'status_update') {
            updateOrderStatus(message.order_number, message.status);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 5s...");
        ws = null;
        setTimeout(connectWebSocket, 5000);
    };
}

function prependOrder(order) {
    const tbody = document.getElementById('orders-table-body');

    // Remove "No orders found" row if it exists
    if (tbody.children.length === 1 && tbody.children[0].textContent.includes("No orders found")) {
        tbody.innerHTML = '';
    }

    const tr = document.createElement('tr');
    tr.className = "table-active"; // Highlight new row
    tr.innerHTML = `
        <td>${order.order_number}</td>
        <td>${order.customer_name}</td>
        <td>${order.total_price}</td>
        <td><span class="badge ${getStatusBadge(order.status)}">${order.status}</span></td>
        <td>${order.delivery_slot || '-'}</td>
    `;

    // Add to top of list
    tbody.insertBefore(tr, tbody.firstChild);

    // Remove highlight after 2 seconds
    setTimeout(() => {
        tr.classList.remove("table-active");
    }, 2000);
}

function updateOrderStatus(orderNumber, newStatus) {
    const tbody = document.getElementById('orders-table-body');
    const rows = tbody.getElementsByTagName('tr');

    for (let row of rows) {
        const orderNumCell = row.cells[0];
        if (orderNumCell && orderNumCell.textContent === orderNumber) {
            const statusCell = row.cells[3];
            const statusBadge = statusCell.querySelector('span');

            // Update status text and badge class
            statusBadge.textContent = newStatus;
            statusBadge.className = `badge ${getStatusBadge(newStatus)}`;

            // Highlight the row briefly
            row.classList.add('table-success');
            setTimeout(() => {
                row.classList.remove('table-success');
            }, 2000);

            break;
        }
    }
}
