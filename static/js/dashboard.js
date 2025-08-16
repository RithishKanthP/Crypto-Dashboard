// Dashboard JavaScript functionality

// Global variables
let refreshInProgress = false;
let autoRefreshInterval = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set up auto-refresh (optional)
    // setupAutoRefresh();
    
    // Add event listeners
    setupEventListeners();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Set up event listeners for interactive elements
 */
function setupEventListeners() {
    // Add click handlers for refresh buttons
    const refreshButtons = document.querySelectorAll('[onclick*="refreshData"]');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            refreshData(event);
        });
    });
    
    // Add click handlers for chart buttons
    const chartButtons = document.querySelectorAll('[onclick*="showChart"]');
    chartButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const cryptoId = this.getAttribute('data-crypto-id');
            const cryptoName = this.getAttribute('data-crypto-name');
            if (cryptoId && cryptoName) {
                showChart(cryptoId, cryptoName);
            }
        });
    });
}

/**
 * Refresh cryptocurrency data
 * @param {Event} event - Click event
 */
async function refreshData(event) {
    if (event) {
        event.preventDefault();
    }
    
    if (refreshInProgress) {
        console.log('Refresh already in progress');
        return;
    }
    
    refreshInProgress = true;
    
    // Find refresh button and show loading state
    const refreshButton = event ? event.target.closest('button, a') : document.querySelector('[onclick*="refreshData"]');
    const originalText = refreshButton ? refreshButton.innerHTML : '';
    
    if (refreshButton) {
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<span class="loading"></span> Refreshing...';
    }
    
    try {
        console.log('Fetching latest cryptocurrency data...');
        
        const response = await fetch('/api/refresh', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            console.log('Data refreshed successfully');
            showAlert('success', 'Data refreshed successfully!');
            
            // Reload the page to show new data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            console.error('Failed to refresh data:', data.message);
            showAlert('danger', `Failed to refresh data: ${data.message}`);
        }
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        showAlert('danger', 'Network error while refreshing data. Please try again.');
    } finally {
        refreshInProgress = false;
        
        if (refreshButton) {
            refreshButton.disabled = false;
            refreshButton.innerHTML = originalText;
        }
    }
}

/**
 * Show alert message to user
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} message - Alert message
 */
function showAlert(type, message) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert.auto-dismiss');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show auto-dismiss`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of main content
    const mainContainer = document.querySelector('main .container, main .container-fluid');
    if (mainContainer) {
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Format number with appropriate suffixes
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    if (num >= 1e12) {
        return (num / 1e12).toFixed(1) + 'T';
    }
    if (num >= 1e9) {
        return (num / 1e9).toFixed(1) + 'B';
    }
    if (num >= 1e6) {
        return (num / 1e6).toFixed(1) + 'M';
    }
    if (num >= 1e3) {
        return (num / 1e3).toFixed(1) + 'K';
    }
    return num.toFixed(2);
}

/**
 * Format currency with proper decimals
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency
 */
function formatCurrency(amount) {
    if (amount >= 1) {
        return '$' + amount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    } else {
        return '$' + amount.toFixed(6);
    }
}

/**
 * Format percentage with color coding
 * @param {number} percentage - Percentage value
 * @returns {string} HTML string with formatted percentage
 */
function formatPercentage(percentage) {
    const isPositive = percentage >= 0;
    const className = isPositive ? 'text-success' : 'text-danger';
    const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
    const sign = isPositive ? '+' : '';
    
    return `
        <span class="${className}">
            <i class="fas ${icon} me-1"></i>
            ${sign}${percentage.toFixed(2)}%
        </span>
    `;
}

/**
 * Set up auto-refresh functionality (optional)
 */
function setupAutoRefresh() {
    // Auto-refresh every 5 minutes (300000 ms)
    const refreshInterval = 300000;
    
    autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing data...');
        refreshData();
    }, refreshInterval);
    
    console.log(`Auto-refresh set up to run every ${refreshInterval / 1000} seconds`);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped');
    }
}

/**
 * Show detailed chart for a specific cryptocurrency
 * @param {string} cryptoId - Cryptocurrency ID
 * @param {string} cryptoName - Cryptocurrency name
 */
function showChart(cryptoId, cryptoName) {
    console.log(`Showing chart for ${cryptoName} (${cryptoId})`);
    
    // Update modal title
    const modalTitle = document.getElementById('cryptoModalLabel');
    if (modalTitle) {
        modalTitle.textContent = `${cryptoName} Price Chart`;
    }
    
    // Show modal
    const modal = document.getElementById('cryptoModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Create placeholder chart
        // In a real implementation, you would fetch historical data here
        createCryptoChart(cryptoId, cryptoName);
    }
}

/**
 * Create a cryptocurrency chart
 * @param {string} cryptoId - Cryptocurrency ID
 * @param {string} cryptoName - Cryptocurrency name
 */
function createCryptoChart(cryptoId, cryptoName) {
    const canvas = document.getElementById('cryptoChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.cryptoChartInstance) {
        window.cryptoChartInstance.destroy();
    }
    
    // Generate sample data (in real implementation, fetch from API)
    const sampleData = generateSampleData();
    
    window.cryptoChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sampleData.labels,
            datasets: [{
                label: `${cryptoName} Price (USD)`,
                data: sampleData.prices,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price (USD)'
                    },
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Generate sample data for chart demonstration
 * @returns {Object} Sample data object
 */
function generateSampleData() {
    const labels = [];
    const prices = [];
    const now = new Date();
    
    // Generate 7 days of sample data
    for (let i = 6; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString());
        
        // Generate random price movement
        const basePrice = 50000;
        const variation = (Math.random() - 0.5) * 0.1;
        prices.push(basePrice * (1 + variation));
    }
    
    return { labels, prices };
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + R for refresh
    if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        refreshData();
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

/**
 * Handle page visibility changes
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, stop auto-refresh to save resources
        stopAutoRefresh();
    } else {
        // Page is visible again, restart auto-refresh
        // setupAutoRefresh();
    }
});

/**
 * Check if the page needs to be refreshed
 */
function checkForUpdates() {
    fetch('/api/crypto-data')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Data check completed');
                // Could implement logic to check if data is newer and prompt user to refresh
            }
        })
        .catch(error => {
            console.error('Error checking for updates:', error);
        });
}

// Export functions for global access
window.refreshData = refreshData;
window.showChart = showChart;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatPercentage = formatPercentage;
