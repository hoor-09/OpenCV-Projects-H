class FocusGuard {
    constructor() {
        this.isRunning = false;
        this.sessionTimer = null;
        this.startTime = null;
        this.apiBaseUrl = 'http://localhost:5001';  // Using port 5001
        this.metrics = {
            productivityScore: 100,
            distractionCount: 0,
            focusTime: 0,
            sessionDuration: 0
        };
        
        this.initializeElements();
        this.initializeWebcam();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.webcamVideo = document.getElementById('webcam');
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.scoreValue = document.getElementById('score-value');
        this.distractionsValue = document.getElementById('distractions-value');
        this.timerValue = document.getElementById('timer-value');
        this.statusIndicator = document.getElementById('status-indicator');
        this.distractionTypes = document.getElementById('distraction-types');
        this.alertsContainer = document.getElementById('alerts-container');
    }
    
    async initializeWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                } 
            });
            this.webcamVideo.srcObject = stream;
            this.showAlert('Webcam connected successfully!', 'success');
        } catch (error) {
            this.showAlert('Cannot access webcam. Please check permissions.', 'error');
            console.error('Webcam error:', error);
        }
    }
    
    setupEventListeners() {
        this.startBtn.addEventListener('click', () => this.startSession());
        this.stopBtn.addEventListener('click', () => this.stopSession());
        this.resetBtn.addEventListener('click', () => this.resetSession());
        
        // Process frames periodically
        setInterval(() => {
            if (this.isRunning) {
                this.processFrame();
            }
        }, 1000); // Process every second
    }
    
    async startSession() {
        this.isRunning = true;
        this.startTime = Date.now();
        this.startBtn.disabled = true;
        this.stopBtn.disabled = false;
        
        this.sessionTimer = setInterval(() => {
            this.updateTimer();
        }, 1000);
        
        this.showAlert('Session started! Focus time begins now.', 'success');
    }
    
    stopSession() {
        this.isRunning = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        clearInterval(this.sessionTimer);
        
        this.showAlert('Session stopped. Good work!', 'success');
    }
    
    resetSession() {
        this.stopSession();
        this.metrics = {
            productivityScore: 100,
            distractionCount: 0,
            focusTime: 0,
            sessionDuration: 0
        };
        this.updateUI();
        this.clearAlerts();
        
        // Reset on server too
        fetch(`${this.apiBaseUrl}/api/reset-session`, { method: 'POST' })
            .catch(error => console.error('Reset error:', error));
            
        this.showAlert('Session reset. Ready to start fresh!', 'success');
    }
    
    async processFrame() {
        if (!this.isRunning) return;
        
        try {
            // Capture frame from webcam
            const canvas = document.createElement('canvas');
            canvas.width = 320;  // Lower resolution for faster processing
            canvas.height = 240;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(this.webcamVideo, 0, 0, 320, 240);
            
            const imageData = canvas.toDataURL('image/jpeg', 0.7);  // Lower quality for speed
            
            // Send to backend for processing
            const response = await fetch(`${this.apiBaseUrl}/api/process-frame`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateMetrics(data.metrics, data.distractions);
            }
            
        } catch (error) {
            console.error('Processing error:', error);
            if (!error.message.includes('HTTP error')) {
                this.showAlert('Connection error. Make sure backend is running.', 'error');
            }
        }
    }
    
    updateMetrics(metrics, distractions) {
        this.metrics = metrics;
        this.updateUI();
        
        // Show alerts for new distractions
        if (distractions && distractions.length > 0) {
            distractions.forEach(distraction => {
                this.showAlert(`Distraction detected: ${distraction.replace('_', ' ')}`, 'warning');
            });
        }
    }
    
    updateUI() {
        // Update metric values
        this.scoreValue.textContent = this.metrics.productivityScore;
        this.distractionsValue.textContent = this.metrics.distractionCount;
        
        // Update status indicator
        this.updateStatusIndicator();
        
        // Update distraction types
        this.updateDistractionList();
    }
    
    updateStatusIndicator() {
        const score = this.metrics.productivityScore;
        this.statusIndicator.className = 'status-indicator ';
        
        if (score >= 70) {
            this.statusIndicator.classList.add('focused');
            this.statusIndicator.innerHTML = '<span>Focused 👍</span>';
        } else if (score >= 40) {
            this.statusIndicator.classList.add('distracted');
            this.statusIndicator.innerHTML = '<span>Getting Distracted ⚠️</span>';
        } else {
            this.statusIndicator.classList.add('very-distracted');
            this.statusIndicator.innerHTML = '<span>Very Distracted ❌</span>';
        }
    }
    
    updateDistractionList() {
        if (this.metrics.distractionCount > 0) {
            this.distractionTypes.innerHTML = `
                <div class="distraction-item">Looking away from screen</div>
                <div class="distraction-item">Phone use detected</div>
                <div class="distraction-item">Not moving (possible distraction)</div>
            `;
        } else {
            this.distractionTypes.innerHTML = '<div class="no-distractions">No distractions detected</div>';
        }
    }
    
    updateTimer() {
        if (!this.startTime) return;
        
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        this.timerValue.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        this.metrics.sessionDuration = elapsed;
    }
    
    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.textContent = message;
        
        this.alertsContainer.appendChild(alert);
        
        // Remove alert after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    clearAlerts() {
        this.alertsContainer.innerHTML = '';
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new FocusGuard();
});