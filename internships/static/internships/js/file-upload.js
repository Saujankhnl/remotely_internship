// File Upload module - handles CV/file upload interactions
const FileUpload = {
    init() {
        this.bindCVUpload();
    },

    // Handle CV file input change
    bindCVUpload() {
        const cvInput = document.getElementById('id_cv');
        if (!cvInput) return;

        cvInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name || 'Click to upload your CV';
            const fileNameEl = document.getElementById('cvFileName');
            const uploadArea = document.getElementById('cvUploadArea');

            if (fileNameEl) {
                fileNameEl.textContent = fileName;
            }
            if (uploadArea && e.target.files[0]) {
                uploadArea.classList.add('border-green-500');
                uploadArea.classList.remove('border-gray-600');
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => FileUpload.init());

export default FileUpload;
