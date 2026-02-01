// Utility functions module
const Utils = {
    // Toggle class on element
    toggleClass(element, className) {
        if (element) {
            element.classList.toggle(className);
        }
    },

    // Add class to element
    addClass(element, ...classNames) {
        if (element) {
            element.classList.add(...classNames);
        }
    },

    // Remove class from element
    removeClass(element, ...classNames) {
        if (element) {
            element.classList.remove(...classNames);
        }
    },

    // Get element by ID
    getById(id) {
        return document.getElementById(id);
    },

    // Show element
    show(element) {
        if (element) {
            element.classList.remove('hidden');
        }
    },

    // Hide element
    hide(element) {
        if (element) {
            element.classList.add('hidden');
        }
    },

    // Set text content
    setText(element, text) {
        if (element) {
            element.textContent = text;
        }
    },

    // Set input value
    setValue(element, value) {
        if (element) {
            element.value = value;
        }
    }
};

export default Utils;
