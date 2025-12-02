// API Base URL - Use current domain for production, localhost for development
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1'
    : `${window.location.protocol}//${window.location.host}/api/v1`;

// State
let currentTaskId = null;

// Helper: Format markdown-like text for better display
function formatMarkdown(text) {
    if (!text) return '';
    
    return text
        // Preserve line breaks
        .split('\n')
        .map(line => {
            // Headers
            if (line.startsWith('### ')) {
                return `<h5 style="color: var(--primary); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.15rem;">${line.substring(4)}</h5>`;
            }
            if (line.startsWith('## ')) {
                return `<h4 style="color: var(--primary); margin-top: 1.75rem; margin-bottom: 0.85rem; font-size: 1.25rem;">${line.substring(3)}</h4>`;
            }
            if (line.startsWith('# ')) {
                return `<h3 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.4rem;">${line.substring(2)}</h3>`;
            }
            
            // Bold text
            line = line.replace(/\*\*(.*?)\*\*/g, '<strong style="color: rgba(255, 255, 255, 0.95);">$1</strong>');
            
            // Bullet points
            if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                return `<div style="margin-left: 1.5rem; margin-bottom: 0.5rem;">• ${line.substring(line.indexOf(' ') + 1)}</div>`;
            }
            
            // Numbered lists
            if (/^\d+\.\s/.test(line.trim())) {
                return `<div style="margin-left: 1.5rem; margin-bottom: 0.5rem;">${line}</div>`;
            }
            
            // Empty lines
            if (!line.trim()) {
                return '<div style="height: 0.75rem;"></div>';
            }
            
            // Regular paragraphs
            return `<p style="margin-bottom: 0.75rem;">${line}</p>`;
        })
        .join('');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadHistory();
    initParticles();
});

// Particle Animation
function initParticles() {
    const canvas = document.getElementById('particles');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 80;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        
        draw() {
            ctx.fillStyle = `rgba(16, 185, 129, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // Connect particles
        particles.forEach((a, i) => {
            particles.slice(i + 1).forEach(b => {
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 120) {
                    ctx.strokeStyle = `rgba(255, 201, 168, ${0.2 * (1 - distance / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Event Listeners
function initializeEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.getAttribute('data-tab')) {
                e.preventDefault();
                switchTab(link.getAttribute('data-tab'));
            }
        });
    });

    // Task card clicks
    document.querySelectorAll('.task-card').forEach(card => {
        card.querySelector('.btn').addEventListener('click', () => {
            const taskType = card.getAttribute('data-task');
            showTaskForm(taskType);
        });
    });

    // File input change handlers
    document.getElementById('docFile')?.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || '';
        const fileInfo = document.getElementById('docFileInfo');
        if (fileName && fileInfo) {
            fileInfo.textContent = `Selected: ${fileName}`;
        }
    });
    
    document.getElementById('dataFile')?.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || '';
        const fileInfo = document.getElementById('dataFileInfo');
        if (fileName && fileInfo) {
            fileInfo.textContent = `Selected: ${fileName}`;
        }
    });

    // Form submissions
    document.getElementById('analyzeTextForm')?.addEventListener('submit', handleTextAnalysis);
    document.getElementById('analyzeDocForm')?.addEventListener('submit', handleDocumentAnalysis);
    document.getElementById('analyzeDataForm')?.addEventListener('submit', handleDataAnalysis);
}

// Tab Switching
function switchTab(tabName) {
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-tab') === tabName) {
            link.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    // Load history if switching to history tab
    if (tabName === 'history') {
        loadHistory();
    }
}

// Show Task Form
function showTaskForm(taskType) {
    hideTaskForms();
    document.getElementById('taskForms').style.display = 'block';
    
    const formMap = {
        'text': 'textForm',
        'document': 'documentForm',
        'data': 'dataForm'
    };
    
    const formId = formMap[taskType];
    if (formId) {
        document.getElementById(formId).classList.add('active');
        document.getElementById(formId).scrollIntoView({ behavior: 'smooth' });
    }
}

// Hide Task Forms
function hideTaskForms() {
    document.getElementById('taskForms').style.display = 'none';
    document.querySelectorAll('.task-form').forEach(form => {
        form.classList.remove('active');
    });
}

// Hide Task Result
function hideTaskResult() {
    document.getElementById('taskResult').style.display = 'none';
}

// Show Loading State
function setButtonLoading(button, loading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        button.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        button.disabled = false;
    }
}

// Handle Text Analysis
async function handleTextAnalysis(e) {
    e.preventDefault();
    
    const button = e.target.querySelector('button[type="submit"]');
    setButtonLoading(button, true);
    
    const query = document.getElementById('textQuery').value;
    const instruction = document.getElementById('textInstruction').value;
    
    try {
        const response = await fetch(`${API_BASE}/tasks/analyze-text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                instruction: instruction || undefined
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayTaskResult(result);
            e.target.reset();
            hideTaskForms();
            // Auto-refresh to get complete results after a delay
            setTimeout(() => viewTaskDetails(result.task_id), 3000);
        } else {
            showError(result.detail || 'Analysis failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        setButtonLoading(button, false);
    }
}

// Handle Document Analysis
async function handleDocumentAnalysis(e) {
    e.preventDefault();
    
    const button = e.target.querySelector('button[type="submit"]');
    setButtonLoading(button, true);
    
    const fileInput = document.getElementById('docFile');
    const instruction = document.getElementById('docInstruction').value;
    
    console.log('File input:', fileInput);
    console.log('Files:', fileInput.files);
    console.log('First file:', fileInput.files[0]);
    
    if (!fileInput.files[0]) {
        showError('Please select a file first');
        setButtonLoading(button, false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (instruction) {
        formData.append('instruction', instruction);
    }
    
    console.log('Sending file:', fileInput.files[0].name);
    console.log('FormData entries:', Array.from(formData.entries()));
    
    try {
        const response = await fetch(`${API_BASE}/tasks/analyze-doc`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('Response:', result);
        
        if (response.ok) {
            displayTaskResult(result);
            e.target.reset();
            const fileInfo = document.getElementById('docFileInfo');
            if (fileInfo) fileInfo.textContent = '';
            hideTaskForms();
            // Auto-refresh to get complete results after a delay
            setTimeout(() => viewTaskDetails(result.task_id), 5000);
        } else {
            showError(result.detail || 'Analysis failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError('Network error: ' + error.message);
    } finally {
        setButtonLoading(button, false);
    }
}

// Handle Data Analysis
async function handleDataAnalysis(e) {
    e.preventDefault();
    
    const button = e.target.querySelector('button[type="submit"]');
    setButtonLoading(button, true);
    
    const fileInput = document.getElementById('dataFile');
    const instruction = document.getElementById('dataInstruction').value;
    
    console.log('Data file input:', fileInput);
    console.log('Data files:', fileInput.files);
    
    if (!fileInput.files[0]) {
        showError('Please select a file first');
        setButtonLoading(button, false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (instruction) {
        formData.append('instruction', instruction);
    }
    
    console.log('Sending data file:', fileInput.files[0].name);
    
    try {
        const response = await fetch(`${API_BASE}/tasks/analyze-data`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('Data response:', result);
        
        if (response.ok) {
            displayTaskResult(result);
            e.target.reset();
            const fileInfo = document.getElementById('dataFileInfo');
            if (fileInfo) fileInfo.textContent = '';
            hideTaskForms();
            // Auto-refresh to get complete results after a delay
            setTimeout(() => viewTaskDetails(result.task_id), 5000);
        } else {
            showError(result.detail || 'Analysis failed');
        }
    } catch (error) {
        console.error('Data upload error:', error);
        showError('Network error: ' + error.message);
    } finally {
        setButtonLoading(button, false);
    }
}

// Display Task Result
function displayTaskResult(task) {
    const resultDiv = document.getElementById('taskResult');
    const contentDiv = document.getElementById('resultContent');
    
    let html = '';
    
    // Show status prominently only if still processing
    if (task.status === 'processing') {
        html += `
            <div class="result-section">
                <h4>Analysis in Progress</h4>
                <p><span class="status-badge status-${task.status}">${task.status.toUpperCase()}</span></p>
                <p>Your request is being processed. Please check back in History.</p>
            </div>
        `;
    }
    
    // Main Analysis Results - Show FULL content without truncation
    if (task.summary) {
        html += `
            <div class="result-section" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(255, 201, 168, 0.05)); border-left: 4px solid var(--primary); padding: 1.5rem;">
                <h4>Analysis Results</h4>
                <div class="analysis-content" style="font-size: 1.05rem; line-height: 1.8; color: rgba(255, 255, 255, 0.95);">${formatMarkdown(task.summary)}</div>
            </div>
        `;
    }
    
    // Skip sentiment display for news analysis - not meaningful without real-time data
    
    if (task.forecast) {
        html += `
            <div class="result-section" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(255, 201, 168, 0.05)); border-left: 4px solid var(--primary); padding: 1.5rem;">
                <h4>Forecast & Predictions</h4>
                <div class="analysis-content" style="font-size: 1.05rem; line-height: 1.8; color: rgba(255, 255, 255, 0.95);">${formatMarkdown(task.forecast)}</div>
            </div>
        `;
    }
    
    // Data Visualizations - Show chart previews inline
    if (task.charts && task.charts.length > 0) {
        html += `
            <div class="result-section" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(255, 201, 168, 0.05)); border-left: 3px solid var(--primary);">
                <h4>Data Visualizations</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; margin-top: 1.5rem;">
        `;
        
        task.charts.forEach((chart, index) => {
            const chartName = chart.includes('distribution') ? 'Distribution Chart' :
                            chart.includes('correlation') ? 'Correlation Heatmap' :
                            chart.includes('timeseries') ? 'Time Series' :
                            chart.includes('barchart') ? 'Correlation Bar Chart' :
                            chart.includes('sentiment') ? 'Sentiment Analysis' :
                            chart.includes('trend') ? 'Trend Forecast' : `Chart ${index + 1}`;
            
            const chartFilename = chart.split('/').pop();
            const chartDownloadUrl = `${window.location.protocol}//${window.location.host}/download/chart/${chartFilename}`;
            
            html += `
                <div style="background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 1rem; border: 1px solid rgba(16, 185, 129, 0.2);">
                    <h5 style="color: var(--primary); margin-bottom: 1rem; font-size: 1.1rem;">${chartName}</h5>
                    <img src="${chart}" alt="${chartName}" style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 1rem; background: white; padding: 0.5rem;">
                    <a href="${chartDownloadUrl}" class="btn btn-secondary" download="${chartFilename}" style="width: 100%; justify-content: center;">Download ${chartName}</a>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Downloads - show prominently for reports
    if (task.report_url) {
        const reportFilename = task.report_url.split('/').pop();
        const downloadUrl = `${window.location.protocol}//${window.location.host}/download/report/${reportFilename}`;
        html += `
            <div class="result-section" style="background: rgba(16, 185, 129, 0.05); border-left: 3px solid var(--primary);">
                <h4>Full Report</h4>
                <a href="${downloadUrl}" class="btn btn-primary" download="${reportFilename}">Download Complete Report (PDF)</a>
            </div>
        `;
    }
    
    contentDiv.innerHTML = html;
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Load History
async function loadHistory() {
    const contentDiv = document.getElementById('historyContent');
    contentDiv.innerHTML = '<div class="loading">Loading history...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/tasks?limit=50`);
        const result = await response.json();
        
        if (response.ok && result.tasks && result.tasks.length > 0) {
            contentDiv.innerHTML = result.tasks.map(task => {
                const taskTypeIcons = {
                    'NEWS_INSIGHT': 'News Analysis',
                    'DOCUMENT_ANALYSIS': 'Document Processing',
                    'DATA_ANALYSIS': 'Data Analysis'
                };
                const taskTypeName = taskTypeIcons[task.task_type] || task.task_type;
                const createdDate = new Date(task.created_at).toLocaleString();
                const statusClass = task.status === 'completed' ? 'success' : task.status === 'processing' ? 'warning' : 'error';
                
                return `
                <div class="history-item">
                    <div class="history-item-header">
                        <div>
                            <div class="history-item-title">${taskTypeName}</div>
                            <div class="history-item-time">${createdDate}</div>
                            ${task.query ? `<div class="history-item-query">"${task.query.substring(0, 80)}${task.query.length > 80 ? '...' : ''}"</div>` : ''}
                        </div>
                        <span class="status-badge status-${statusClass}">${task.status.toUpperCase()}</span>
                    </div>
                    ${task.summary ? `<div class="history-item-summary">${task.summary.substring(0, 200)}${task.summary.length > 200 ? '...' : ''}</div>` : ''}
                    <div class="history-item-footer">
                        <button class="btn btn-sm btn-primary" onclick="viewTaskDetails('${task.task_id}')">View Full Details</button>
                        ${task.report_url ? `<a href="${window.location.protocol}//${window.location.host}/download/report/${task.report_url.split('/').pop()}" class="btn btn-sm btn-secondary" download="${task.report_url.split('/').pop()}">Download Report</a>` : ''}
                    </div>
                </div>
            `;
            }).join('');
        } else {
            contentDiv.innerHTML = '<div class="loading">No tasks found. Start your first analysis!</div>';
        }
    } catch (error) {
        console.error('History load error:', error);
        contentDiv.innerHTML = '<div class="loading">Failed to load history: ' + error.message + '</div>';
    }
}

// View Task Details
async function viewTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        const task = await response.json();
        
        if (response.ok) {
            switchTab('tasks');
            setTimeout(() => {
                displayTaskResult(task);
            }, 300);
        } else {
            showError('Failed to load task details');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

// Show Success Message
function showSuccess(message) {
    alert('Success: ' + message);
}

// Show Error Message
function showError(message) {
    alert('Error: ' + message);
}

// Click-to-enlarge chart functionality
document.addEventListener('click', (e) => {
    if (e.target.tagName === 'IMG' && e.target.closest('.chart-preview-card')) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            cursor: pointer;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.2s ease;
        `;
        
        const img = document.createElement('img');
        img.src = e.target.src;
        img.style.cssText = `
            max-width: 95vw;
            max-height: 95vh;
            border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: scaleIn 0.3s ease;
        `;
        
        modal.appendChild(img);
        document.body.appendChild(modal);
        
        // Close on click
        modal.addEventListener('click', () => {
            modal.style.animation = 'fadeOut 0.2s ease';
            setTimeout(() => modal.remove(), 200);
        });
        
        // Close on ESC key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                modal.style.animation = 'fadeOut 0.2s ease';
                setTimeout(() => modal.remove(), 200);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }
});
