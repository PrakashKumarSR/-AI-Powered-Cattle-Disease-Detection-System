// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.querySelector('.file-name');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');

    // Update file name display
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileName.textContent = this.files[0].name;
        } else {
            fileName.textContent = 'No file chosen';
        }
    });

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select an image file.');
            return;
        }

        // Show loading
        loading.classList.remove('hidden');
        result.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);

        // Submit form programmatically
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // Replace the entire page with the result page
            document.documentElement.innerHTML = html;
        })
        .catch(error => {
            console.error('Error:', error);
            loading.classList.add('hidden');
            alert('Error analyzing image. Please try again.');
        });
    });
});