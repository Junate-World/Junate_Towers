// Main JavaScript functionality for Tower Documentation System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSearch();
    initializePDFViewer();
    initializeMobileMenu();
    initializeTooltips();
    initializeFileUploads();
    initializeConfirmations();
});

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = document.querySelector('form[action*="search"]');
    
    if (searchInput && searchForm) {
        // Add search suggestions or autocomplete if needed
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.trim();
            if (query.length > 2) {
                // Could implement autocomplete here
                console.log('Search query:', query);
            }
        }, 300));
    }
}

// PDF viewer enhancements
function initializePDFViewer() {
    const pdfFrames = document.querySelectorAll('iframe[src*=".pdf"]');
    
    pdfFrames.forEach(frame => {
        // Add loading indicator
        frame.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        
        // Set initial opacity for smooth loading
        frame.style.opacity = '0';
        frame.style.transition = 'opacity 0.3s ease';
        
        // Add error handling
        frame.addEventListener('error', function() {
            console.error('Failed to load PDF:', this.src);
            this.parentElement.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-yellow-500 mb-4"></i>
                    <p class="text-gray-600 mb-4">Failed to load PDF document</p>
                    <a href="${this.src}" target="_blank" class="inline-flex items-center px-4 py-2 bg-engineering-600 text-white rounded hover:bg-engineering-700">
                        <i class="fas fa-external-link-alt mr-2"></i>
                        Open in New Tab
                    </a>
                </div>
            `;
        });
    });
}

// Mobile menu functionality
function initializeMobileMenu() {
    const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            this.removeAttribute('title');
            
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg';
            tooltip.textContent = title;
            tooltip.style.top = '-30px';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translateX(-50%)';
            
            this.style.position = 'relative';
            this.appendChild(tooltip);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
                this.setAttribute('title', title);
            }, { once: true });
        });
    });
}

// File upload enhancements
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file, input);
            }
        });
    });
}

// File validation
function validateFile(file, input) {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = ['application/pdf'];
    
    if (file.size > maxSize) {
        showNotification('File size must be less than 50MB', 'error');
        input.value = '';
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        showNotification('Only PDF files are allowed', 'error');
        input.value = '';
        return false;
    }
    
    return true;
}

// Confirmation dialogs
function initializeConfirmations() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (message && !confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${getNotificationIcon(type)} mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scroll for anchor links
function smoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Print functionality
function printPDF(url) {
    const printWindow = window.open(url, '_blank');
    printWindow.onload = function() {
        printWindow.print();
    };
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Loading state management
function setLoadingState(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.classList.add('btn-loading');
        element.dataset.originalText = element.textContent;
        element.textContent = 'Loading...';
    } else {
        element.disabled = false;
        element.classList.remove('btn-loading');
        element.textContent = element.dataset.originalText || element.textContent;
    }
}

// Form validation enhancements
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                showFormErrors(form);
            }
        });
    });
}

function showFormErrors(form) {
    const invalidInputs = form.querySelectorAll(':invalid');
    
    invalidInputs.forEach(input => {
        input.classList.add('border-red-500');
        
        const error = document.createElement('div');
        error.className = 'text-red-500 text-sm mt-1';
        error.textContent = input.validationMessage;
        
        input.parentElement.appendChild(error);
        
        // Remove error when input is corrected
        input.addEventListener('input', function() {
            if (this.validity.valid) {
                this.classList.remove('border-red-500');
                error.remove();
            }
        });
    });
}

// Export functions for global use
window.TowerDocs = {
    showNotification,
    copyToClipboard,
    printPDF,
    setLoadingState,
    smoothScroll
};
