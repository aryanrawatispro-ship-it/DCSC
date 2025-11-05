// Discord Data Scraper - Main JavaScript

let socket;
let currentJobId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    socket = io();

    // Socket event listeners
    socket.on('connect', function() {
        console.log('Connected to server');
    });

    socket.on('log_message', function(data) {
        if (data.job_id === currentJobId) {
            addLogEntry(data.log);
        }
    });

    socket.on('progress_update', function(data) {
        if (data.job_id === currentJobId) {
            updateProgress(data.scraped);
        }
    });

    socket.on('status_update', function(data) {
        if (data.job_id === currentJobId) {
            updateStatus(data.status);
        }
    });

    // Form submission
    document.getElementById('scraperForm').addEventListener('submit', handleFormSubmit);

    // Toggle password visibility
    document.getElementById('toggleToken').addEventListener('click', toggleTokenVisibility);

    // Action change handler
    document.getElementById('action').addEventListener('change', handleActionChange);

    // Load recent jobs
    loadRecentJobs();
});

// Handle form submission
function handleFormSubmit(e) {
    e.preventDefault();

    // Get form values
    const formData = {
        token: document.getElementById('token').value,
        action: document.getElementById('action').value,
        channelUrl: document.getElementById('channelUrl').value,
        limit: document.getElementById('limit').value,
        timeout: document.getElementById('timeout').value,
        minDelay: document.getElementById('minDelay').value,
        maxDelay: document.getElementById('maxDelay').value
    };

    // Add message-specific fields if scraping messages
    if (formData.action === 'scrapeMessages') {
        formData.before = document.getElementById('before').value;
        formData.after = document.getElementById('after').value;
    }

    // Validate
    if (!formData.token) {
        showAlert('Please enter your Discord token', 'danger');
        return;
    }

    if (!formData.channelUrl) {
        showAlert('Please enter a channel URL', 'danger');
        return;
    }

    // Disable submit button
    const submitBtn = document.getElementById('startBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Starting...';

    // Send request
    fetch('/api/start-scraping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Scraping';
        } else {
            currentJobId = data.job_id;
            showProgressSection();
            showAlert(data.message, 'success');
            // Keep button disabled while scraping
        }
    })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Scraping';
    });
}

// Toggle token visibility
function toggleTokenVisibility() {
    const tokenInput = document.getElementById('token');
    const toggleBtn = document.getElementById('toggleToken');

    if (tokenInput.type === 'password') {
        tokenInput.type = 'text';
        toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
        tokenInput.type = 'password';
        toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
    }
}

// Handle action change
function handleActionChange() {
    const action = document.getElementById('action').value;
    const messageOptions = document.getElementById('messageOptions');

    if (action === 'scrapeMessages') {
        messageOptions.style.display = 'block';
    } else {
        messageOptions.style.display = 'none';
    }
}

// Show progress section
function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'block';

    // Clear log output
    document.getElementById('logOutput').innerHTML = '';

    // Reset progress
    document.getElementById('itemCount').textContent = '0';
    document.getElementById('statusText').textContent = 'Starting...';
    document.getElementById('statusText').className = 'badge bg-primary';

    // Hide result actions
    document.getElementById('resultActions').style.display = 'none';

    // Scroll to progress section
    progressSection.scrollIntoView({ behavior: 'smooth' });
}

// Add log entry
function addLogEntry(log) {
    const logOutput = document.getElementById('logOutput');

    const logClass = 'log-' + log.level;
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-timestamp">[${log.timestamp}]</span>
        <span class="${logClass}"> ${log.message}</span>
    `;

    logOutput.appendChild(logEntry);

    // Auto-scroll to bottom
    logOutput.scrollTop = logOutput.scrollHeight;
}

// Update progress
function updateProgress(count) {
    document.getElementById('itemCount').textContent = count;
}

// Update status
function updateStatus(status) {
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');
    const submitBtn = document.getElementById('startBtn');

    if (status === 'completed') {
        statusText.textContent = 'Completed';
        statusText.className = 'badge bg-success';
        progressBar.className = 'progress-bar bg-success';
        progressBar.textContent = 'Completed!';

        // Show result actions
        document.getElementById('resultActions').style.display = 'block';

        // Enable submit button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Scraping';

        // Load recent jobs
        loadRecentJobs();

        // Setup result buttons
        document.getElementById('viewResultsBtn').onclick = function() {
            window.location.href = `/results?job=${currentJobId}`;
        };

        document.getElementById('downloadBtn').onclick = function() {
            window.location.href = `/api/download/${currentJobId}`;
        };

    } else if (status === 'failed') {
        statusText.textContent = 'Failed';
        statusText.className = 'badge bg-danger';
        progressBar.className = 'progress-bar bg-danger';
        progressBar.textContent = 'Failed';

        // Enable submit button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Scraping';

        // Load recent jobs
        loadRecentJobs();

    } else if (status === 'running') {
        statusText.textContent = 'Running';
        statusText.className = 'badge bg-primary';
    }
}

// Show alert
function showAlert(message, type) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        alert.classList.remove('show');
        setTimeout(function() {
            alert.remove();
        }, 150);
    }, 5000);
}

// Load recent jobs
function loadRecentJobs() {
    fetch('/api/jobs')
        .then(response => response.json())
        .then(data => {
            const recentJobsDiv = document.getElementById('recentJobs');

            if (data.jobs.length === 0) {
                recentJobsDiv.innerHTML = '<p class="text-muted small">No jobs yet</p>';
                return;
            }

            // Sort by ID descending (most recent first)
            data.jobs.sort((a, b) => b.id - a.id);

            // Take only last 5 jobs
            const recentJobs = data.jobs.slice(0, 5);

            let html = '';
            recentJobs.forEach(job => {
                const actionText = job.action === 'scrapeMessages' ? 'Messages' : 'Members';
                const statusClass = `status-${job.status}`;

                html += `
                    <div class="job-item" onclick="viewJob(${job.id})">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small><strong>Job #${job.id}</strong></small><br>
                                <small class="text-muted">${actionText}</small>
                            </div>
                            <span class="job-status ${statusClass}">${job.status}</span>
                        </div>
                        <small class="text-muted">${job.total_items} items</small>
                    </div>
                `;
            });

            recentJobsDiv.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading jobs:', error);
        });
}

// View job
function viewJob(jobId) {
    fetch(`/api/job/${jobId}`)
        .then(response => response.json())
        .then(job => {
            if (job.status === 'completed' && job.output_file) {
                window.location.href = `/results?job=${jobId}`;
            } else {
                showAlert(`Job #${jobId} - Status: ${job.status}`, 'info');
            }
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'danger');
        });
}

// Copy token script to clipboard
function copyTokenScript() {
    const script = "(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()";

    navigator.clipboard.writeText(script).then(function() {
        showAlert('Token extraction script copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy:', err);
    });
}

// Refresh jobs every 10 seconds
setInterval(loadRecentJobs, 10000);
