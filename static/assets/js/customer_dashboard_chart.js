document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('monthlyTransactionChart').getContext('2d');

    const monthlyTransactionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Amount (' + window.currency + ')',
                data: window.monthlyData || [0, 0, 0, 0],
                backgroundColor: '#28a745'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
