const API_URL = 'http://localhost:8000/api/v1/subscriptions';

async function fetchSubscriptions() {
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        
        updateMetrics(data.metrics);
        renderTable(data.subscriptions);
    } catch (err) {
        console.error("Error fetching subscriptions:", err);
    }
}

function updateMetrics(metrics) {
    document.getElementById('burnRate').textContent = metrics.total_monthly_burn_rate.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    
    const rc = document.getElementById('renewalsCount');
    const rcContainer = document.getElementById('renewalsCountContainer');
    rc.textContent = metrics.upcoming_renewals_count;
    
    if (metrics.upcoming_renewals_count > 0) {
        rcContainer.classList.add('value-amber');
    } else {
        rcContainer.classList.remove('value-amber');
    }
}

function renderTable(subscriptions) {
    const tbody = document.getElementById('subTableBody');
    tbody.innerHTML = '';
    
    subscriptions.forEach(sub => {
        const tr = document.createElement('tr');
        tr.id = `row-${sub.id}`;
        if (sub.status === 'PAUSED') tr.classList.add('row-paused');

        // Determine badge
        let badgeHTML = '';
        if (sub.is_overdue) {
            badgeHTML = `<span class="badge-overdue">Overdue</span>`;
        } else if (sub.is_renewing_soon) {
            badgeHTML = `<span class="badge-renewing-soon">Renewing Soon</span>`;
        }

        tr.innerHTML = `
            <td><strong>${sub.service_name}</strong></td>
            <td class="service-cost">$${sub.cost.toFixed(2)}</td>
            <td>${sub.billing_cycle === 'MONTHLY' ? 'Mo' : 'Yr'}</td>
            <td>$${sub.normalized_monthly_cost.toFixed(2)}</td>
            <td>
                <div>${sub.next_renewal_date}</div>
                <div style="margin-top: 4px;">${badgeHTML}</div>
            </td>
            <td>${sub.status}</td>
            <td>
                <label class="toggle-switch">
                    <input type="checkbox" ${sub.status === 'ACTIVE' ? 'checked' : ''} onchange="toggleSubscription('${sub.id}', this)">
                    <span class="slider"></span>
                </label>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function toggleSubscription(id, checkbox) {
    const row = document.getElementById(`row-${id}`);
    
    // Optimistic update
    if (checkbox.checked) {
        row.classList.remove('row-paused');
    } else {
        row.classList.add('row-paused');
    }

    try {
        const res = await fetch(`${API_URL}/${id}/toggle`, {
            method: 'PATCH'
        });
        
        if (res.ok) {
            const data = await res.json();
            updateMetrics(data.metrics);
            // Optionally refetch to ensure source of truth
            fetchSubscriptions();
        } else {
            // Revert on failure
            checkbox.checked = !checkbox.checked;
            if (checkbox.checked) row.classList.remove('row-paused');
            else row.classList.add('row-paused');
            alert("Failed to toggle subscription.");
        }
    } catch (err) {
        console.error(err);
        // Revert on failure
        checkbox.checked = !checkbox.checked;
        if (checkbox.checked) row.classList.remove('row-paused');
        else row.classList.add('row-paused');
    }
}

document.getElementById('subForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        service_name: document.getElementById('serviceName').value,
        cost: parseFloat(document.getElementById('cost').value),
        billing_cycle: document.getElementById('billingCycle').value,
        next_renewal_date: document.getElementById('renewalDate').value
    };

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            document.getElementById('subForm').reset();
            fetchSubscriptions();
        } else {
            const error = await res.json();
            alert("Error: " + JSON.stringify(error));
        }
    } catch (err) {
        console.error(err);
        alert("Error creating subscription.");
    }
});

fetchSubscriptions();
