document.addEventListener('DOMContentLoaded', function() {
    const logoInput = document.getElementById('logo');
    if (logoInput) {
        logoInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    // show preview image
                    const logoPreview = document.getElementById('logo-preview');
                    if (logoPreview) {
                        logoPreview.innerHTML = `
                            <div style="position: relative; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center;">
                                <img src="${event.target.result}" 
                                     alt="Preview" 
                                     style="max-height: 100%; max-width: 100%; object-fit: contain; border: 1px solid #dee2e6; border-radius: 8px;">
                            </div>
                        `;
                    }
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
});
