// Main JavaScript file for Scale AI Clone

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in animation to cards
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(function() {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Handle file upload preview
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var files = e.target.files;
            var previewContainer = document.getElementById('file-preview');
            
            if (previewContainer && files.length > 0) {
                previewContainer.innerHTML = '';
                
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    var preview = document.createElement('div');
                    preview.className = 'alert alert-info';
                    preview.innerHTML = `
                        <i class="fas fa-file me-2"></i>
                        ${file.name} (${formatFileSize(file.size)})
                    `;
                    previewContainer.appendChild(preview);
                }
            }
        });
    });

    // Handle form submissions with loading states
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            }
        });
    });

    // Handle notification mark as read
    var notificationCheckboxes = document.querySelectorAll('.notification-checkbox');
    notificationCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                var notificationId = this.value;
                markNotificationAsRead(notificationId);
            }
        });
    });

    // Handle project progress updates
    var progressBars = document.querySelectorAll('.project-progress-bar');
    progressBars.forEach(function(bar) {
        var progress = bar.getAttribute('data-progress');
        if (progress) {
            setTimeout(function() {
                bar.style.width = progress + '%';
            }, 500);
        }
    });

    // Handle annotation tool interactions
    var annotationLabels = document.querySelectorAll('.annotation-label');
    annotationLabels.forEach(function(label) {
        label.addEventListener('click', function() {
            // Remove active class from all labels
            annotationLabels.forEach(function(l) {
                l.classList.remove('active');
            });
            
            // Add active class to clicked label
            this.classList.add('active');
            
            // Update annotation data
            var labelName = this.getAttribute('data-label');
            updateAnnotationData(labelName);
        });
    });

    // Handle search functionality
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var items = document.querySelectorAll('.searchable-item');
            
            items.forEach(function(item) {
                var text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Handle modal confirmations
    var confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            var saveBtn = document.querySelector('.save-btn');
            if (saveBtn) {
                saveBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            var modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                var modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    var k = 1024;
    var sizes = ['Bytes', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function markNotificationAsRead(notificationId) {
    fetch('/notifications/mark-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            notification_id: notificationId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.remove('unread');
            }
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

function updateAnnotationData(labelName) {
    // This function would update the annotation data based on the selected label
    console.log('Selected label:', labelName);
    // Implementation would depend on the specific annotation tool being used
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Export functions for use in other modules
window.ScaleAI = {
    formatFileSize: formatFileSize,
    markNotificationAsRead: markNotificationAsRead,
    updateAnnotationData: updateAnnotationData,
    getCookie: getCookie
};
