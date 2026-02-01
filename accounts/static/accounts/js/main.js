// Main entry point - imports and initializes all modules
// This file can be used as a single entry point if needed

import Utils from './utils.js';
import Auth from './auth.js';
import Dashboard from './dashboard.js';

// App namespace
const App = {
    Utils,
    Auth,
    Dashboard,

    // Initialize app
    init() {
        console.log('Remotely App initialized');
    }
};

// Make App available globally for debugging
window.App = App;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());

export default App;
