document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const currentPriceElement = document.getElementById('current-price');
    const lastUpdatedElement = document.getElementById('last-updated');
    const pricesTableBody = document.getElementById('prices-table-body');
    const alertsTableBody = document.getElementById('alerts-table-body');
    const noPricesMessage = document.getElementById('no-prices-message');
    const noAlertsMessage = document.getElementById('no-alerts-message');
    const refreshButton = document.getElementById('refresh-btn');
    
    // Format price with 2 decimal places and $ symbol
    function formatPrice(price) {
        return '$' + parseFloat(price).toFixed(2);
    }
    
    // Format timestamp
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
    
    // Calculate price change and add appropriate class
    function calculatePriceChange(currentPrice, previousPrice) {
        if (!previousPrice) return '-';
        
        const change = ((currentPrice - previousPrice) / previousPrice) * 100;
        const changeText = change.toFixed(2) + '%';
        
        if (change > 0) {
            return `<span class="price-up">+${changeText}</span>`;
        } else if (change < 0) {
            return `<span class="price-down">${changeText}</span>`;
        } else {
            return `<span>${changeText}</span>`;
        }
    }
    
    // Update prices table
    function updatePricesTable(prices) {
        if (prices.length === 0) {
            pricesTableBody.innerHTML = '';
            noPricesMessage.classList.remove('d-none');
            return;
        }
        
        noPricesMessage.classList.add('d-none');
        pricesTableBody.innerHTML = '';
        
        // Sort prices by timestamp (newest first)
        prices.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Update the current price display
        if (prices.length > 0) {
            currentPriceElement.textContent = formatPrice(prices[0].price_usd);
            lastUpdatedElement.textContent = formatTimestamp(prices[0].timestamp);
        }
        
        // Add rows to the table
        prices.forEach((price, index) => {
            const row = document.createElement('tr');
            
            // Calculate change from previous price (if available)
            const previousPrice = prices[index + 1] ? prices[index + 1].price_usd : null;
            const changeHtml = calculatePriceChange(price.price_usd, previousPrice);
            
            row.innerHTML = `
                <td>${formatTimestamp(price.timestamp)}</td>
                <td>${formatPrice(price.price_usd)}</td>
                <td>${changeHtml}</td>
            `;
            
            pricesTableBody.appendChild(row);
        });
    }
    
    // Update alerts table
    function updateAlertsTable(alerts) {
        if (alerts.length === 0) {
            alertsTableBody.innerHTML = '';
            noAlertsMessage.classList.remove('d-none');
            return;
        }
        
        noAlertsMessage.classList.add('d-none');
        alertsTableBody.innerHTML = '';
        
        // Sort alerts by timestamp (newest first)
        alerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Add rows to the table
        alerts.forEach(alert => {
            const row = document.createElement('tr');
            const changeClass = alert.percent_change > 0 ? 'price-up' : 'price-down';
            const badgeClass = alert.direction === 'increase' ? 'bg-success' : 'bg-danger';
            const directionText = alert.direction === 'increase' ? 'Increase' : 'Decrease';
            
            row.innerHTML = `
                <td>${formatTimestamp(alert.timestamp)}</td>
                <td>${formatPrice(alert.current_price)}</td>
                <td>${formatPrice(alert.previous_price)}</td>
                <td class="${changeClass}">${alert.percent_change.toFixed(2)}%</td>
                <td><span class="badge ${badgeClass}">${directionText}</span></td>
            `;
            
            alertsTableBody.appendChild(row);
        });
    }
    
    // Fetch data from API
    function fetchData() {
        // Fetch prices
        fetch('/api/prices')
            .then(response => response.json())
            .then(data => {
                updatePricesTable(data.prices);
            })
            .catch(error => console.error('Error fetching prices:', error));
        
        // Fetch alerts
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                updateAlertsTable(data.alerts);
            })
            .catch(error => console.error('Error fetching alerts:', error));
    }
    
    // Set up EventSource for real-time updates
    function setupEventSource() {
        const eventSource = new EventSource('/api/stream');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'price_update') {
                fetchData();
            }
        };
        
        eventSource.onerror = function() {
            console.error('EventSource failed. Reconnecting in 5 seconds...');
            eventSource.close();
            setTimeout(setupEventSource, 5000);
        };
    }
    
    // Initial fetch
    fetchData();
    
    // Set up event source for real-time updates
    setupEventSource();
    
    // Manual refresh button
    refreshButton.addEventListener('click', fetchData);
    
    // Refresh data every 60 seconds as a fallback
    setInterval(fetchData, 60000);
});