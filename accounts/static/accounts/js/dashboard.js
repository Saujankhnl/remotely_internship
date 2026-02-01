// Dashboard module - handles dashboard interactions
import Utils from './utils.js';

const Dashboard = {
    // Initialize dashboard module
    init() {
        this.cacheElements();
        this.bindEvents();
    },

    // Cache DOM elements
    cacheElements() {
        this.profileSidebar = Utils.getById('profileSidebar');
        this.overlay = Utils.getById('overlay');
        this.profileBtn = Utils.getById('profileBtn');
        this.closeBtn = Utils.getById('closeProfileBtn');
    },

    // Bind events
    bindEvents() {
        if (this.profileBtn) {
            this.profileBtn.addEventListener('click', () => this.toggleProfile());
        }
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.toggleProfile());
        }
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.toggleProfile());
        }

        // Close sidebar on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isProfileOpen()) {
                this.toggleProfile();
            }
        });
    },

    // Toggle profile sidebar
    toggleProfile() {
        if (this.profileSidebar && this.overlay) {
            const willOpen = !this.isProfileOpen();
            
            Utils.toggleClass(this.profileSidebar, 'translate-x-full');
            Utils.toggleClass(this.overlay, 'hidden');
            
            // Prevent body scroll when sidebar is open
            document.body.style.overflow = willOpen ? 'hidden' : '';
        }
    },

    // Check if profile sidebar is open
    isProfileOpen() {
        return this.profileSidebar && !this.profileSidebar.classList.contains('translate-x-full');
    },

    // Close profile sidebar
    closeProfile() {
        if (this.isProfileOpen()) {
            this.toggleProfile();
        }
    },

    // Open profile sidebar
    openProfile() {
        if (!this.isProfileOpen()) {
            this.toggleProfile();
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => Dashboard.init());

export default Dashboard;
