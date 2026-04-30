document.addEventListener('DOMContentLoaded', function() {
    const uploadSection = document.getElementById('upload-section');
    const fileInput = document.getElementById('resume-file-input');

    if (uploadSection && fileInput) {
        // Click to select file
        uploadSection.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('drag-over');
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('drag-over');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
            fileInput.files = e.dataTransfer.files;
            handleFileSelection();
        });

        // File selection change
        fileInput.addEventListener('change', handleFileSelection);
    }
});

function updateUploadDisplay(fileName = null) {
    const fileInput = document.getElementById('resume-file-input');
    const uploadSection = document.getElementById('upload-section');

    if (fileName) {
        uploadSection.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
            </div>
            <p class="upload-text-sub">${fileName}</p>
        `;
    } else if (fileInput.files.length > 0) {
        const name = fileInput.files[0].name;
        updateUploadDisplay(name);
    }
}

function handleFileSelection() {
    const fileInput = document.getElementById('resume-file-input');
    
    if (fileInput.files.length === 0) {
        return;
    }

    const file = fileInput.files[0];
    updateUploadDisplay(file.name);

    // Show loading state
    const uploadSection = document.getElementById('upload-section');
    uploadSection.innerHTML = `
        <div class="upload-icon">
            <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p class="upload-text-main">Đang xử lý CV...</p>
        <p class="upload-text-sub">Vui lòng đợi</p>
    `;

    // Call preview
    const formData = new FormData();
    formData.append('resume_file', file);

    fetch('/preview-resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('title').value = data.cv_data.title || '';
            document.getElementById('summary').value = data.cv_data.summary || '';
            document.getElementById('skills').value = data.cv_data.skills || '';
            document.getElementById('education').value = data.cv_data.education || '';
            document.getElementById('experience').value = data.cv_data.experience || '';
            document.getElementById('cv_url').value = data.cv_url || '';

            updateUploadDisplay(file.name);
            showNotification('CV đã được quét thành công. Hãy kiểm tra và chỉnh sửa thông tin nếu cần.', 'success');
        } else {
            updateUploadDisplay(file.name);
            showNotification(data.message || 'Không thể xử lý file. Vui lòng thử lại.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        updateUploadDisplay(file.name);
        showNotification('Lỗi xử lý file. Vui lòng thử lại.', 'error');
    });
}

function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.content-card');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}