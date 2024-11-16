document.addEventListener('DOMContentLoaded', function() {
    loadTransactions();
    setupDateFilters();
});

function loadTransactions(offset = 0) {
    const limit = 8;
    fetch(`/recent_transactions?limit=${limit}&offset=${offset}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('transactions-container');
            const table = container.querySelector('table') || createTransactionTable();
            const tbody = table.querySelector('tbody');
            
            data.transactions.forEach(transaction => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${transaction.date}</td>
                    <td>${transaction.name}</td>
                    <td>${transaction.amount}</td>
                    <td>${transaction.category || ''}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading transactions:', error));
}

function createTransactionTable() {
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Category</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    document.getElementById('transactions-container').appendChild(table);
    return table;
}

function setupDateFilters() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    // Set default date range (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    startDate.value = thirtyDaysAgo.toISOString().split('T')[0];
    endDate.value = today.toISOString().split('T')[0];
}