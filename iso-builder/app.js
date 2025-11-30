// A5000mine ISO Builder Frontend

// Form handling
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('iso-form');
    const buildButton = document.getElementById('build-button');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const statusMessage = document.getElementById('status-message');
    const downloadSection = document.getElementById('download-section');
    const downloadButton = document.getElementById('download-button');
    const logContainer = document.getElementById('log-container');

    // Pool selection handling
    const poolRadios = document.querySelectorAll('input[name="pool"]');
    const customPoolGroup = document.getElementById('custom-pool-group');

    poolRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            // Update visual selection
            document.querySelectorAll('.radio-option').forEach(option => {
                option.classList.remove('selected');
            });
            e.target.closest('.radio-option').classList.add('selected');

            // Show/hide custom pool input
            if (e.target.value === 'custom') {
                customPoolGroup.style.display = 'block';
                document.getElementById('custom-pool').required = true;
            } else {
                customPoolGroup.style.display = 'none';
                document.getElementById('custom-pool').required = false;
            }
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate form
        if (!validateForm()) {
            return;
        }

        // Start build process
        await startBuild();
    });

    function validateForm() {
        const wallet = document.getElementById('wallet').value.trim();
        const worker = document.getElementById('worker').value.trim();
        const poolType = document.querySelector('input[name="pool"]:checked').value;
        const customPool = document.getElementById('custom-pool').value.trim();

        // Validate wallet address
        if (!wallet.startsWith('ak_')) {
            showStatus('Invalid wallet address. Must start with "ak_"', 'error');
            return false;
        }

        // Validate worker name
        if (!worker) {
            showStatus('Worker name is required', 'error');
            return false;
        }

        // Validate custom pool URL if selected
        if (poolType === 'custom' && !customPool) {
            showStatus('Custom pool URL is required', 'error');
            return false;
        }

        if (poolType === 'custom' && !customPool.startsWith('stratum+tcp://')) {
            showStatus('Pool URL must start with "stratum+tcp://"', 'error');
            return false;
        }

        return true;
    }

    async function startBuild() {
        // Collect form data
        const formData = new FormData(form);
        const config = {
            wallet: formData.get('wallet').trim(),
            worker_name: formData.get('worker').trim(),
            pool_url: getSelectedPoolUrl(),
            power_limit: parseInt(formData.get('power-limit')),
            core_offset: parseInt(formData.get('core-offset')),
            mem_offset: parseInt(formData.get('mem-offset'))
        };

        // Disable form and show progress
        setFormEnabled(false);
        showProgress(true);
        showLogs(true);
        showStatus('', '');

        try {
            // Start the build
            const response = await fetch('/api/build-iso', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                // Poll for progress
                await pollBuildProgress(result.build_id);
            } else {
                throw new Error(result.error || 'Build failed');
            }

        } catch (error) {
            console.error('Build error:', error);
            showStatus(`Build failed: ${error.message}`, 'error');
            resetForm();
        }
    }

    function getSelectedPoolUrl() {
        const selectedPool = document.querySelector('input[name="pool"]:checked').value;
        if (selectedPool === 'custom') {
            return document.getElementById('custom-pool').value.trim();
        }
        return selectedPool;
    }

    async function pollBuildProgress(buildId) {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/build-status/${buildId}`);
                const status = await response.json();

                updateProgress(status);

                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    handleBuildComplete(status);
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    showStatus(`Build failed: ${status.error}`, 'error');
                    resetForm();
                }

            } catch (error) {
                console.error('Progress poll error:', error);
            }
        }, 2000); // Poll every 2 seconds

        // Stop polling after 30 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
            showStatus('Build timed out. Please try again.', 'error');
            resetForm();
        }, 30 * 60 * 1000);
    }

    function updateProgress(status) {
        const progress = status.progress || 0;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = status.message || 'Building...';

        // Update logs
        if (status.logs && status.logs.length > 0) {
            updateLogs(status.logs);
        }
    }

    function updateLogs(logs) {
        logContainer.innerHTML = logs
            .slice(-20) // Show last 20 entries
            .map(entry => `<div class="log-entry">${escapeHtml(entry)}</div>`)
            .join('');
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    function handleBuildComplete(status) {
        showStatus('ISO build completed successfully!', 'success');
        downloadButton.href = `/api/download/${status.filename}`;
        downloadSection.style.display = 'block';
        progressContainer.style.display = 'none';
    }

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type ? `status-${type}` : ''}`;
        statusMessage.style.display = message ? 'block' : 'none';
    }

    function showProgress(show) {
        progressContainer.style.display = show ? 'block' : 'none';
        if (show) {
            progressFill.style.width = '0%';
            progressText.textContent = 'Initializing...';
        }
    }

    function showLogs(show) {
        logContainer.style.display = show ? 'block' : 'none';
        if (show) {
            logContainer.innerHTML = '<div class="log-entry">Build process starting...</div>';
        }
    }

    function setFormEnabled(enabled) {
        const inputs = form.querySelectorAll('input, select, button');
        inputs.forEach(input => {
            input.disabled = !enabled;
        });

        buildButton.textContent = enabled ? '🚀 Build Custom ISO' : '🔄 Building ISO...';
    }

    function resetForm() {
        setFormEnabled(true);
        showProgress(false);
        showLogs(false);
        downloadSection.style.display = 'none';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
