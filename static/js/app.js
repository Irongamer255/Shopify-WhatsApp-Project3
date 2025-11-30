document.addEventListener('DOMContentLoaded', () => {
    fetchOrders();
    fetchConfigs();
    fetchAnalytics();
    connectWebSocket();

    document.getElementById('settings-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const delay = document.getElementById('delay-input').value;
        try {
            await fetch('/api/v1/admin/configs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    key: 'confirmation_delay_minutes',
                    value: delay,
                    description: 'Delay in minutes before sending confirmation'
                })
            });
            alert('Settings saved!');
        } catch (e) {
            console.error("Error saving settings:", e);
            alert('Failed to save settings');
        }
    });

    document.getElementById('connect-whatsapp-btn').addEventListener('click', async () => {
        if (!confirm("This will open a Chrome window on the server to scan the QR code. Continue?")) return;

        try {
            const btn = document.getElementById('connect-whatsapp-btn');
            btn.disabled = true;
            btn.textContent = "Opening Browser...";

            const res = await fetch('/api/v1/admin/whatsapp/link', { method: 'POST' });
            const data = await res.json();

            alert(data.message);
            btn.textContent = "Browser Opened";

            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-qr-code-scan"></i> Connect WhatsApp';
            }, 5000);

        } catch (e) {
            console.error("Error linking WhatsApp:", e);
            alert("Failed to initiate linking.");
            document.getElementById('connect-whatsapp-btn').disabled = false;
        }
    });
});

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/orders`;
    const ws = new WebSocket(wsUrl);

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

async function fetchOrders() {
    try {
        const res = await fetch('/api/v1/admin/orders');
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
    } catch (e) {
        console.error("Error fetching orders:", e);
    }
}

async function fetchConfigs() {
    try {
        const res = await fetch('/api/v1/admin/configs');
        const data = await res.json();
        const delayConfig = data.find(c => c.key === 'confirmation_delay_minutes');
        if (delayConfig) {
            document.getElementById('delay-input').value = delayConfig.value;
        }
    } catch (e) {
        console.error("Error fetching configs:", e);
    }
}

async function fetchAnalytics() {
    try {
        const res = await fetch('/api/v1/admin/analytics');
        const data = await res.json();

        document.getElementById('total-orders').textContent = data.total_orders;
        document.getElementById('conf-rate').textContent = data.confirmed_rate.toFixed(1) + '%';
        document.getElementById('cancel-rate').textContent = data.cancellation_rate.toFixed(1) + '%';
        document.getElementById('success-rate').textContent = data.delivery_success_rate.toFixed(1) + '%';
    } catch (e) {
        console.error("Error fetching analytics:", e);
    }
}

function getStatusBadge(status) {
    switch (status) {
        case 'confirmed': return 'text-bg-success';
        case 'cancelled': return 'text-bg-danger';
        case 'pending': return 'text-bg-warning';
        case 'shipped': return 'text-bg-info';
        case 'delivered': return 'text-bg-primary';
        default: return 'text-bg-secondary';
    }
}
