// Profile module - handles profile page interactions
import Utils from './utils.js';

const Profile = {
    // Initialize profile module
    init() {
        this.cacheElements();
        this.bindEvents();
    },

    // Cache DOM elements
    cacheElements() {
        // Try both id_profile_photo (user) and id_logo (company)
        this.imageInput = Utils.getById('id_profile_photo') || Utils.getById('id_logo');
        this.previewImg = Utils.getById('previewImg');
        this.initialText = Utils.getById('initialText');
        this.imagePreview = Utils.getById('imagePreview');
        
        // LinkedIn modal elements
        this.importLinkedInBtn = Utils.getById('importLinkedIn');
        this.linkedinModal = Utils.getById('linkedinModal');
        this.closeModalBtn = Utils.getById('closeModal');
    },

    // Bind events
    bindEvents() {
        if (this.imageInput) {
            this.imageInput.addEventListener('change', (e) => this.handleImageChange(e));
        }
        
        // LinkedIn modal events
        if (this.importLinkedInBtn) {
            this.importLinkedInBtn.addEventListener('click', () => this.openLinkedInModal());
        }
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeLinkedInModal());
        }
        if (this.linkedinModal) {
            this.linkedinModal.addEventListener('click', (e) => {
                if (e.target === this.linkedinModal) {
                    this.closeLinkedInModal();
                }
            });
        }
    },
    
    // Open LinkedIn modal
    openLinkedInModal() {
        if (this.linkedinModal) {
            Utils.removeClass(this.linkedinModal, 'hidden');
        }
    },
    
    // Close LinkedIn modal
    closeLinkedInModal() {
        if (this.linkedinModal) {
            Utils.addClass(this.linkedinModal, 'hidden');
        }
    },

    // Handle image selection
    handleImageChange(event) {
        const file = event.target.files[0];
        
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                if (this.previewImg) {
                    this.previewImg.src = e.target.result;
                    Utils.removeClass(this.previewImg, 'hidden');
                }
                if (this.initialText) {
                    Utils.addClass(this.initialText, 'hidden');
                }
            };
            
            reader.readAsDataURL(file);
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => Profile.init());

export default Profile;
