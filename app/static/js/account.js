document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar');
    const uploadHint = document.querySelector('.avatar-upload-hint');

    uploadHint.addEventListener('click', function() {
        avatarInput.click();
    });

    // Handle file selection
    avatarInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const reader = new FileReader();
            
            reader.onload = function(event) {
                uploadHint.textContent = file.name;
                uploadHint.style.color = '#16a34a';
            };
            
            reader.readAsDataURL(file);
        }
    });
});
