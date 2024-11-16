document.addEventListener('DOMContentLoaded', function() {
    loadInitialTransactions();
    setupDateFilters();
});

function loadInitialTransactions() {
    fetch('/recent_transactions?limit=8&offset=0')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('transactionTableBody');
            tableBody.innerHTML = ''; // Clear existing rows
            
            if (data.transactions && data.transactions.length > 0) {
                data.transactions.forEach(transaction => {
                    const row = document.createElement('tr');
                    const amountClass = transaction.amount >= 0 ? 'amount-positive' : 'amount-negative';
                    row.innerHTML = `
                        <td>${transaction.date}</td>
                        <td>${transaction.name}</td>
                        <td class="${amountClass}">$${Math.abs(transaction.amount).toFixed(2)}</td>
                        <td>${transaction.category}</td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="4">No transactions found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('transactionTableBody').innerHTML = 
                '<tr><td colspan="4">Error loading transactions</td></tr>';
        });
}