// A5000mine Dashboard JavaScript

const REFRESH_INTERVAL = 5000; // 5 seconds
let startTime = Date.now();

// Update all dashboard data
async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update mining status
        updateMiningStatus(data.mining);

        // Update performance metrics
        updatePerformance(data.performance);

        // Update GPU stats
        updateGPUStats(data.gpu);

        // Update logs
        updateLogs(data.logs);

    } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setOfflineStatus();
    }
}

function updateMiningStatus(mining) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('mining-status');
    const workerName = document.getElementById('worker-name');
    const poolUrl = document.getElementById('pool-url');
    const uptime = document.getElementById('uptime');

    if (mining && mining.active) {
        statusIndicator.className = 'status-indicator status-online';
        statusText.textContent = 'Mining';
        workerName.textContent = mining.worker || '-';
        poolUrl.textContent = formatPoolUrl(mining.pool || '-');
        uptime.textContent = formatUptime(mining.uptime || 0);
    } else {
        statusIndicator.className = 'status-indicator status-offline';
        statusText.textContent = 'Offline';
        workerName.textContent = '-';
        poolUrl.textContent = '-';
        uptime.textContent = '-';
    }
}

function updatePerformance(performance) {
    const hashrate = document.getElementById('hashrate');
    const sharesAccepted = document.getElementById('shares-accepted');
    const sharesRejected = document.getElementById('shares-rejected');
    const efficiency = document.getElementById('efficiency');

    if (performance) {
        hashrate.textContent = `${(performance.hashrate || 0).toFixed(2)} G/s`;
        sharesAccepted.textContent = performance.shares_accepted || 0;
        sharesRejected.textContent = performance.shares_rejected || 0;

        const total = (performance.shares_accepted || 0) + (performance.shares_rejected || 0);
        const eff = total > 0 ? ((performance.shares_accepted / total) * 100).toFixed(1) : 0;
        efficiency.textContent = `${eff}%`;
    } else {
        hashrate.textContent = '- G/s';
        sharesAccepted.textContent = '0';
        sharesRejected.textContent = '0';
        efficiency.textContent = '-';
    }
}

function updateGPUStats(gpu) {
    const gpuName = document.getElementById('gpu-name');
    const gpuTemp = document.getElementById('gpu-temp');
    const gpuPower = document.getElementById('gpu-power');
    const gpuUtil = document.getElementById('gpu-util');

    if (gpu) {
        gpuName.textContent = gpu.name || '-';
        gpuTemp.textContent = gpu.temperature ? `${gpu.temperature} °C` : '- °C';
        gpuPower.textContent = gpu.power_draw ? `${gpu.power_draw} W` : '- W';
        gpuUtil.textContent = gpu.utilization ? `${gpu.utilization}%` : '- %';
    } else {
        gpuName.textContent = '-';
        gpuTemp.textContent = '- °C';
        gpuPower.textContent = '- W';
        gpuUtil.textContent = '- %';
    }
}

function updateLogs(logs) {
    const logContainer = document.getElementById('log-container');

    if (logs && logs.length > 0) {
        logContainer.innerHTML = logs
            .slice(-15) // Show last 15 entries
            .map(entry => `<div class="log-entry">${escapeHtml(entry)}</div>`)
            .join('');
        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

function setOfflineStatus() {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('mining-status');

    statusIndicator.className = 'status-indicator status-offline';
    statusText.textContent = 'Connection Lost';
}

function formatPoolUrl(url) {
    // Shorten pool URL for display
    return url.replace('stratum+tcp://', '').replace(':4040', '');
}

function formatUptime(seconds) {
    if (!seconds || seconds === 0) return '-';

    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('A5000mine Dashboard initialized');

    // Initial update
    updateDashboard();

    // Set up auto-refresh
    setInterval(updateDashboard, REFRESH_INTERVAL);
});
