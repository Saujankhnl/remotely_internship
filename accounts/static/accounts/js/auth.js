// Authentication module - handles login and register form interactions
import Utils from './utils.js';

const Auth = {
    // Initialize auth module
    init() {
        this.cacheElements();
        this.bindEvents();
    },

    // Cache DOM elements
    cacheElements() {
        // Login elements
        this.loginForm = Utils.getById('loginForm');
        this.userBtn = Utils.getById('userBtn');
        this.companyBtn = Utils.getById('companyBtn');
        this.divider = Utils.getById('divider');
        this.buttonContainer = Utils.getById('buttonContainer');
        this.userTypeInput = Utils.getById('userTypeInput');
        this.submitBtn = Utils.getById('submitBtn');

        // Register elements
        this.userForm = Utils.getById('userForm');
        this.companyForm = Utils.getById('companyForm');
    },

    // Bind click events
    bindEvents() {
        if (this.userBtn) {
            this.userBtn.addEventListener('click', () => this.selectType('user'));
        }
        if (this.companyBtn) {
            this.companyBtn.addEventListener('click', () => this.selectType('company'));
        }
    },

    // Select user type (login page)
    selectType(type) {
        // For login page
        if (this.loginForm) {
            this.handleLoginTypeSelection(type);
        }
        // For register page
        if (this.userForm && this.companyForm) {
            this.handleRegisterTypeSelection(type);
        }
    },

    // Handle login page type selection
    handleLoginTypeSelection(type) {
        Utils.setValue(this.userTypeInput, type);
        Utils.show(this.loginForm);
        Utils.hide(this.divider);
        
        Utils.removeClass(this.buttonContainer, 'flex', 'flex-col', 'sm:flex-row');
        Utils.addClass(this.buttonContainer, 'block', 'text-center');

        if (type === 'user') {
            Utils.addClass(this.userBtn, 'ring-4', 'ring-blue-300');
            Utils.hide(this.companyBtn);
            Utils.addClass(this.submitBtn, 'bg-blue-600', 'active:bg-blue-700');
            Utils.setText(this.submitBtn, 'Login as User');
        } else {
            Utils.addClass(this.companyBtn, 'ring-4', 'ring-green-300');
            Utils.hide(this.userBtn);
            Utils.addClass(this.submitBtn, 'bg-green-600', 'active:bg-green-700');
            Utils.setText(this.submitBtn, 'Login as Company');
        }
    },

    // Handle register page type selection
    handleRegisterTypeSelection(type) {
        Utils.hide(this.divider);
        Utils.addClass(this.buttonContainer, 'text-center');

        if (type === 'user') {
            Utils.show(this.userForm);
            Utils.hide(this.companyForm);
            Utils.addClass(this.userBtn, 'ring-4', 'ring-blue-300');
            Utils.hide(this.companyBtn);
        } else {
            Utils.show(this.companyForm);
            Utils.hide(this.userForm);
            Utils.addClass(this.companyBtn, 'ring-4', 'ring-green-300');
            Utils.hide(this.userBtn);
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => Auth.init());

export default Auth;
