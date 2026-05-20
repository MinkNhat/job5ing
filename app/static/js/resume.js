const itemConfig = {
    education: {
        containerId: 'education-container',
        prefix: 'education',
        icon: 'fa-graduation-cap',
        fields: ['school', 'major', 'start_date', 'end_date'],
        fieldMap: {
            school: { label: 'Trường/Đại học', id: 'school', type: 'text' },
            major: { label: 'Ngành học', id: 'major', type: 'text' },
            start_date: { label: 'Ngày bắt đầu', id: 'startDate', type: 'month' },
            end_date: { label: 'Ngày kết thúc', id: 'endDate', type: 'month' }
        },
        displayTemplate: (data, icon) => `
            <div class="col-md-10">
                <div class="d-flex gap-3 align-items-center">
                    <div class="rounded-circle d-flex align-items-center justify-content-center item-icon">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div>
                        <div class="mb-2"><strong>${data.school || 'Trường/Đại học'}</strong></div>
                        <small class="text-muted">Ngành học: ${data.major || ''}</small><br>
                        <small class="text-muted">
                            ${data.start_date ? formatDateDisplay(data.start_date) : ''} 
                            ${data.end_date ? ' - ' + formatDateDisplay(data.end_date) : ' - Hiện tại'}
                        </small>
                    </div>
                </div>
            </div>
        `,
        title: 'thông tin học tập',
        validation: (data) => {
            if (!data.school?.trim()) return 'Vui lòng nhập tên trường/đại học';
            if (!data.major?.trim()) return 'Vui lòng nhập ngành học';
            if (!data.start_date?.trim()) return 'Vui lòng chọn ngày bắt đầu';
            return null;
        }
    },
    experience: {
        containerId: 'experience-container',
        prefix: 'exp',
        icon: 'fa-briefcase',
        fields: ['job_title', 'company_name', 'position', 'description', 'start_date', 'end_date'],
        fieldMap: {
            job_title: { label: 'Tên công việc', id: 'jobTitle', type: 'text' },
            company_name: { label: 'Tên công ty', id: 'company', type: 'text' },
            position: { label: 'Cấp bậc/Chức vụ', id: 'position', type: 'text' },
            description: { label: 'Mô tả công việc', id: 'description', type: 'textarea' },
            start_date: { label: 'Ngày bắt đầu', id: 'startDate', type: 'month' },
            end_date: { label: 'Ngày kết thúc', id: 'endDate', type: 'month' }
        },
        displayTemplate: (data, icon) => `
            <div class="col-md-10">
                <div class="d-flex gap-3 align-items-center">
                    <div class="rounded-circle d-flex align-items-center justify-content-center item-icon">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div>
                        <div class="mb-1">
                            <strong>${data.job_title || 'Tên công việc'}</strong>
                            <div class="text-muted">${data.company_name || 'Công ty'}</div>
                        </div>
                        <small class="text-muted">Vị trí: ${data.position || ''}</small><br>
                        <small class="text-muted">
                            ${data.start_date ? formatDateDisplay(data.start_date) : ''} 
                            ${data.end_date ? ' - ' + formatDateDisplay(data.end_date) : ' - Hiện tại'}
                        </small>
                    </div>
                </div>
            </div>
        `,
        title: 'thông tin kinh nghiệm',
        validation: (data) => {
            if (!data.job_title?.trim()) return 'Vui lòng nhập tên công việc';
            if (!data.company_name?.trim()) return 'Vui lòng nhập tên công ty';
            if (!data.position?.trim()) return 'Vui lòng nhập cấp bậc/chức vụ';
            if (!data.start_date?.trim()) return 'Vui lòng chọn ngày bắt đầu';
            return null;
        },
        modalSize: 'modal-lg'
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const uploadSection = document.getElementById('upload-section');
    const fileInput = document.getElementById('resume-file-input');

    // Upload, Drag and Drop
    if (uploadSection && fileInput) {
        uploadSection.addEventListener('click', () => fileInput.click());
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('drag-over');
        });
        uploadSection.addEventListener('dragleave', () => uploadSection.classList.remove('drag-over'));
        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
            fileInput.files = e.dataTransfer.files;
            handleFileSelection();
        });
        fileInput.addEventListener('change', handleFileSelection);
    }

    initializeDynamicSections();
    populateExistingData();
});

function initializeDynamicSections() {
    document.querySelectorAll('.add-item-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const type = this.dataset.target;
            openAddModal(type);
        });
    });
}

function populateExistingData() {
    const hasFormData = restoreFromFormHiddenInputs();
    
    if (!hasFormData && typeof existingCVData !== 'undefined') {
        if (existingCVData.education?.length) {
            existingCVData.education.forEach(edu => {
                addItem('education', {
                    school: edu.school || '',
                    major: edu.major || '',
                    start_date: formatDateForInput(edu.start_date),
                    end_date: formatDateForInput(edu.end_date)
                });
            });
        }
        
        if (existingCVData.experience?.length) {
            existingCVData.experience.forEach(exp => {
                addItem('experience', {
                    job_title: exp.job_title || '',
                    company_name: exp.company_name || '',
                    position: exp.position || '',
                    description: exp.description || '',
                    start_date: formatDateForInput(exp.start_date),
                    end_date: formatDateForInput(exp.end_date)
                });
            });
        }
    }
}

function restoreFromFormHiddenInputs() {
    const educationInputs = document.querySelectorAll('input[name^="education_"]');
    const experienceInputs = document.querySelectorAll('input[name^="exp_"]');
    
    if (educationInputs.length === 0 && experienceInputs.length === 0) {
        return false;
    }
    
    // Extract education items
    const educationIndices = new Set();
    educationInputs.forEach(input => {
        const match = input.name.match(/education_\w+_(\d+)/);
        if (match) educationIndices.add(parseInt(match[1]));
    });
    
    educationIndices.forEach(idx => {
        const data = {
            school: document.querySelector(`input[name="education_school_${idx}"]`)?.value || '',
            major: document.querySelector(`input[name="education_major_${idx}"]`)?.value || '',
            start_date: document.querySelector(`input[name="education_start_${idx}"]`)?.value || '',
            end_date: document.querySelector(`input[name="education_end_${idx}"]`)?.value || ''
        };
        if (data.school) addItem('education', data);
    });
    
    // Extract experience items
    const experienceIndices = new Set();
    experienceInputs.forEach(input => {
        const match = input.name.match(/exp_\w+_(\d+)/);
        if (match) experienceIndices.add(parseInt(match[1]));
    });
    
    experienceIndices.forEach(idx => {
        const data = {
            job_title: document.querySelector(`input[name="exp_job_title_${idx}"]`)?.value || '',
            company_name: document.querySelector(`input[name="exp_company_${idx}"]`)?.value || '',
            position: document.querySelector(`input[name="exp_position_${idx}"]`)?.value || '',
            description: document.querySelector(`textarea[name="exp_description_${idx}"]`)?.value || '',
            start_date: document.querySelector(`input[name="exp_start_${idx}"]`)?.value || '',
            end_date: document.querySelector(`input[name="exp_end_${idx}"]`)?.value || ''
        };
        if (data.job_title) addItem('experience', data);
    });
    
    return educationIndices.size > 0 || experienceIndices.size > 0;
}

function addItem(type, data = {}) {
    const config = itemConfig[type];
    const container = document.getElementById(config.containerId);
    const index = container.children.length;
    
    const fieldMapping = {
        education: { school: 'school', major: 'major', start_date: 'start', end_date: 'end' },
        experience: { job_title: 'job_title', company_name: 'company', position: 'position', description: 'description', start_date: 'start', end_date: 'end' }
    };
    
    const fieldMap = fieldMapping[type];
    const hiddenInputs = config.fields.map(field => {
        const fieldName = fieldMap[field] || field;
        return `<input type="hidden" name="${config.prefix}_${fieldName}_${index}" value="${data[field] || ''}">`;
    }).join('');
    
    const itemHtml = `
        <div class="dynamic-item card p-3 mb-3" data-index="${index}">
            <div class="row">
                ${config.displayTemplate(data, config.icon)}
                <div class="col-md-2 d-flex justify-content-end gap-2 h-50">
                    <button type="button" class="btn btn-sm edit-btn" data-type="${type}" data-index="${index}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-sm delete-btn" data-type="${type}" data-index="${index}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
            ${hiddenInputs}
        </div>
    `;
    
    const fragment = document.createElement('div');
    fragment.innerHTML = itemHtml;
    const newItem = fragment.querySelector('.dynamic-item');
    container.appendChild(newItem);
    
    newItem.querySelector('.edit-btn').addEventListener('click', () => openEditModal(type, newItem, index));
    newItem.querySelector('.delete-btn').addEventListener('click', () => {
        newItem.remove();
        renumberItems(type);
    });
}

function renumberItems(type) {
    const config = itemConfig[type];
    const container = document.getElementById(config.containerId);
    container.querySelectorAll('.dynamic-item').forEach((item, index) => {
        item.querySelectorAll('input[type="hidden"]').forEach(input => {
            const nameMatch = input.name.match(/^(.+?)_\d+$/);
            if (nameMatch) input.name = `${nameMatch[1]}_${index}`;
        });
    });
}

function buildFieldsHtml(config, prefix = 'add') {
    return config.fields.map(field => {
        const fieldConfig = config.fieldMap[field];
        const fieldId = `${prefix}${fieldConfig.id.charAt(0).toUpperCase() + fieldConfig.id.slice(1)}`;
        if (fieldConfig.type === 'textarea') {
            return `<div class="mb-3">
                <label class="form-label">${fieldConfig.label}</label>
                <textarea class="form-control" id="${fieldId}" rows="4"></textarea>
            </div>`;
        }
        return `<div class="mb-3">
            <label class="form-label">${fieldConfig.label}</label>
            <input type="${fieldConfig.type}" class="form-control" id="${fieldId}">
        </div>`;
    }).join('');
}

function openAddModal(type) {
    const config = itemConfig[type];
    const fieldsHtml = buildFieldsHtml(config, 'add');
    
    const modalHtml = `
        <div class="modal fade" id="itemModal" tabindex="-1">
            <div class="modal-dialog ${config.modalSize || ''}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Thêm ${config.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">${fieldsHtml}</div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                        <button type="button" class="btn btn-primary" id="saveItem">Thêm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    removeExistingModal();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('itemModal'));
    modal.show();
    
    document.getElementById('saveItem').addEventListener('click', () => {
        const formData = {};
        config.fields.forEach(field => {
            const fieldConfig = config.fieldMap[field];
            const fieldId = `add${fieldConfig.id.charAt(0).toUpperCase() + fieldConfig.id.slice(1)}`;
            const inputEl = document.getElementById(fieldId);
            formData[field] = inputEl.value;
        });
        
        const error = config.validation(formData);
        if (error) {
            showNotification(error, 'error');
            return;
        }
        
        addItem(type, formData);
        modal.hide();
        showNotification(`Thêm ${config.title} thành công`, 'success');
    });
}

function openEditModal(type, itemElement, index) {
    const config = itemConfig[type];
    const data = {};
    
    const fieldMapping = {
        education: { school: 'school', major: 'major', start_date: 'start', end_date: 'end' },
        experience: { job_title: 'job_title', company_name: 'company', position: 'position', description: 'description', start_date: 'start', end_date: 'end' }
    };
    
    const fieldMap = fieldMapping[type];
    config.fields.forEach(field => {
        const fieldName = fieldMap[field] || field;
        const inputEl = itemElement.querySelector(`input[name="${config.prefix}_${fieldName}_${index}"]`);
        data[field] = inputEl?.value || '';
    });
    
    const fieldsHtml = config.fields.map(field => {
        const fieldConfig = config.fieldMap[field];
        const value = data[field];
        const fieldId = `edit${fieldConfig.id.charAt(0).toUpperCase() + fieldConfig.id.slice(1)}`;
        if (fieldConfig.type === 'textarea') {
            return `<div class="mb-3">
                <label class="form-label">${fieldConfig.label}</label>
                <textarea class="form-control" id="${fieldId}" rows="4">${value}</textarea>
            </div>`;
        }
        return `<div class="mb-3">
            <label class="form-label">${fieldConfig.label}</label>
            <input type="${fieldConfig.type}" class="form-control" id="${fieldId}" value="${value}">
        </div>`;
    }).join('');
    
    const modalHtml = `
        <div class="modal fade" id="itemModal" tabindex="-1">
            <div class="modal-dialog ${config.modalSize || ''}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Chỉnh sửa ${config.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">${fieldsHtml}</div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                        <button type="button" class="btn btn-primary" id="saveEdit">Lưu</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    removeExistingModal();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('itemModal'));
    modal.show();
    
    document.getElementById('saveEdit').addEventListener('click', () => {
        const newData = {};
        const fieldMap = fieldMapping[type];
        config.fields.forEach(field => {
            const fieldConfig = config.fieldMap[field];
            const fieldId = `edit${fieldConfig.id.charAt(0).toUpperCase() + fieldConfig.id.slice(1)}`;
            newData[field] = document.getElementById(fieldId).value;
        });
        
        config.fields.forEach(field => {
            const fieldName = fieldMap[field] || field;
            const input = itemElement.querySelector(`input[name="${config.prefix}_${fieldName}_${index}"]`);
            if (input) input.value = newData[field];
        });
        
        const displayHtml = `
            <div class="row">
                ${config.displayTemplate(newData, config.icon)}
                <div class="col-md-2 d-flex justify-content-end gap-2 h-50">
                    <button type="button" class="btn btn-sm edit-btn" data-type="${type}" data-index="${index}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-sm delete-btn" data-type="${type}" data-index="${index}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;
        
        while (itemElement.firstChild?.tagName !== 'INPUT') {
            itemElement.removeChild(itemElement.firstChild);
        }
        itemElement.insertAdjacentHTML('afterbegin', displayHtml);
        
        itemElement.querySelector('.edit-btn').addEventListener('click', () => openEditModal(type, itemElement, index));
        itemElement.querySelector('.delete-btn').addEventListener('click', () => {
            itemElement.remove();
            renumberItems(type);
        });
        
        modal.hide();
    });
}

function removeExistingModal() {
    const oldModal = document.getElementById('itemModal');
    if (oldModal) oldModal.remove();
}

function updateUploadDisplay(fileName = null) {
    const fileInput = document.getElementById('resume-file-input');
    const uploadSection = document.getElementById('upload-section');

    if (fileName) {
        uploadSection.innerHTML = `
            <div class="upload-icon"><i class="fas fa-check-circle" style="color: #28a745;"></i></div>
            <p class="upload-text-sub">${fileName}</p>
        `;
    } else if (fileInput.files.length > 0) {
        updateUploadDisplay(fileInput.files[0].name);
    }
}

function handleFileSelection() {
    const fileInput = document.getElementById('resume-file-input');
    if (fileInput.files.length === 0) return;

    const file = fileInput.files[0];
    const uploadSection = document.getElementById('upload-section');
    uploadSection.innerHTML = `
        <div class="upload-icon"><i class="fas fa-spinner fa-spin"></i></div>
        <p class="upload-text-main">Đang xử lý CV...</p>
        <p class="upload-text-sub">Vui lòng đợi</p>
    `;

    const formData = new FormData();
    formData.append('resume_file', file);

    fetch('/preview-resume', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('title').value = data.cv_data.title || '';
                document.getElementById('summary').value = data.cv_data.summary || '';
                document.getElementById('skills').value = (Array.isArray(data.cv_data.skills) 
                    ? data.cv_data.skills.join(', ') : data.cv_data.skills) || '';
                document.getElementById('cv_url').value = data.cv_url || '';

                document.getElementById('education-container').innerHTML = '';
                if (data.cv_data.education?.length) {
                    data.cv_data.education.forEach(edu => {
                        addItem('education', {
                            school: edu.school || '',
                            major: edu.major || '',
                            start_date: formatDateForInput(edu.start_date),
                            end_date: formatDateForInput(edu.end_date)
                        });
                    });
                }

                document.getElementById('experience-container').innerHTML = '';
                if (data.cv_data.experience?.length) {
                    data.cv_data.experience.forEach(exp => {
                        addItem('experience', {
                            job_title: exp.job_title || '',
                            company_name: exp.company_name || '',
                            position: exp.position || '',
                            description: exp.description || '',
                            start_date: formatDateForInput(exp.start_date),
                            end_date: formatDateForInput(exp.end_date)
                        });
                    });
                }

                updateUploadDisplay(file.name);
                showNotification('CV đã được quét thành công. Hãy kiểm tra và chỉnh sửa thông tin nếu cần.', 'success');
            } else {
                updateUploadDisplay(file.name);
                showNotification(data.message || 'Không thể xử lý file. Vui lòng thử lại.', 'error');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            updateUploadDisplay(file.name);
            showNotification('Lỗi xử lý file. Vui lòng thử lại.', 'error');
        });
}

function formatDateForInput(dateStr) {
    if (!dateStr || typeof dateStr !== 'string') return '';
    return dateStr.includes('-') ? dateStr.substring(0, 7) : dateStr;
}

function formatDateDisplay(dateStr) {
    if (!dateStr || typeof dateStr !== 'string') return '';
    // Convert YYYY-MM to MM/YYYY
    const parts = dateStr.split('-');
    if (parts.length === 2) {
        return `${parts[1]}/${parts[0]}`;
    }
    return dateStr;
}

function showNotification(message, type = 'success') {
    if (typeof showToast === 'function') {
        showToast(message, type === 'success' ? 'success' : 'danger');
    } else {
        alert(message);
    }
}
