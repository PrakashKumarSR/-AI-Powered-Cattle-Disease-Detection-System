// Main JavaScript file for CattleCare AI

class CattleCareApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const navLinks = document.querySelector('.nav-links');
        
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', () => {
                navLinks.classList.toggle('active');
            });
        }

        // Logout confirmation
        const logoutButtons = document.querySelectorAll('.logout-btn');
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!confirm('Are you sure you want to logout?')) {
                    e.preventDefault();
                }
            });
        });
    }

    setupFileUpload() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        
        uploadAreas.forEach(area => {
            const fileInput = area.nextElementSibling;
            
            area.addEventListener('click', () => fileInput.click());
            
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0], fileInput);
                }
            });
        });
    }

    handleFileUpload(file, fileInput) {
        if (!file.type.startsWith('image/')) {
            this.showAlert('Please upload an image file.', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            this.showAlert('File size must be less than 5MB.', 'error');
            return;
        }

        // Update file input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewContainer = fileInput.closest('.upload-section').querySelector('.image-preview');
            const previewImg = previewContainer.querySelector('.preview-img');
            
            previewImg.src = e.target.result;
            previewContainer.style.display = 'block';
            
            // Enable analyze button
            const analyzeBtn = fileInput.closest('.upload-section').querySelector('.analyze-btn');
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
            }
        };
        reader.readAsDataURL(file);
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form[needs-validation]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                
                form.classList.add('was-validated');
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                this.markInvalid(input, 'This field is required.');
            } else {
                this.markValid(input);
            }
            
            // Email validation
            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    isValid = false;
                    this.markInvalid(input, 'Please enter a valid email address.');
                }
            }
            
            // Password validation
            if (input.type === 'password' && input.value) {
                if (input.value.length < 6) {
                    isValid = false;
                    this.markInvalid(input, 'Password must be at least 6 characters long.');
                }
            }
        });
        
        return isValid;
    }

    markInvalid(input, message) {
        input.style.borderColor = '#dc3545';
        let feedback = input.nextElementSibling;
        
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.style.display = 'block';
    }

    markValid(input) {
        input.style.borderColor = '#28a745';
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'none';
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'close';
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = 'background: none; border: none; font-size: 1.5em; float: right; cursor: pointer;';
        closeBtn.addEventListener('click', () => alertDiv.remove());
        
        alertDiv.appendChild(closeBtn);
        
        // Insert at top of page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // API call helper
    async apiCall(endpoint, data = null, method = 'GET') {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API call failed:', error);
            this.showAlert(error.message, 'error');
            throw error;
        }
    }

    // Image analysis
    async analyzeImage(imageFile, bodyPart) {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('body_part', bodyPart);
        
        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Analysis failed');
            }
            
            return result;
        } catch (error) {
            console.error('Image analysis failed:', error);
            throw error;
        }
    }

    // Download report
    downloadReport(data, filename = 'cattle_report') {
        const report = this.generateReport(data);
        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `${filename}_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    generateReport(data) {
        return `
CattleCare AI - Disease Detection Report
========================================

Diagnosis: ${data.diagnosis}
Confidence: ${(data.confidence * 100).toFixed(1)}%
Body Part: ${data.body_part}
Timestamp: ${new Date().toLocaleString()}

Description:
${data.description || 'No description available.'}

Treatment Protocol:
${data.treatment_protocol ? data.treatment_protocol.map(item => `• ${item}`).join('\n') : '• No specific treatment required.'}

Emergency Measures:
${data.emergency_measures ? data.emergency_measures.map(item => `• ${item}`).join('\n') : '• No emergency measures needed.'}

Additional Notes:
${data.additional_notes || 'No additional notes.'}

Important: This report is generated by AI and should be verified by a qualified veterinarian.

Generated by CattleCare AI System
        `.trim();
    }

    // Utility function to format date
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Utility function to format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cattleCareApp = new CattleCareApp();
});

// Utility functions for external use
window.CattleCareUtils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    },

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};