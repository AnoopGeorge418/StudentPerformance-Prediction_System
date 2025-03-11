document.addEventListener('DOMContentLoaded', function() {
    // Form validation and enhanced UI interactions
    const form = document.getElementById('predictionForm');
    const inputs = form.querySelectorAll('input, select');
    
    // Add input validation and styling
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            validateInput(this);
        });
        
        input.addEventListener('blur', function() {
            validateInput(this);
        });
    });
    
    // Validate individual input
    function validateInput(input) {
        const parent = input.parentElement;
        
        if (input.value) {
            // Valid input
            input.classList.add('border-green-500');
            input.classList.remove('border-red-500');
        } else if (input.hasAttribute('required')) {
            // Invalid required input
            input.classList.add('border-red-500');
            input.classList.remove('border-green-500');
        }
    }
    
    // Add smooth scrolling for all anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add active state to form elements
    const formControls = document.querySelectorAll('.input-focus-effect');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.classList.add('active');
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            this.classList.remove('active');
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
    
    // Form submission handling
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate all inputs
        let isValid = true;
        inputs.forEach(input => {
            validateInput(input);
            if (input.hasAttribute('required') && !input.value) {
                isValid = false;
            }
        });
        
        if (isValid) {
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner"></span> Processing...';
            
            // Collect form data
            const formData = new FormData(this);
            const formObject = {};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });
            
            // Send data to server or process it
            setTimeout(() => {
                // Replace with actual API call
                console.log('Form data:', formObject);
                
                // Show success message
                const resultSection = document.getElementById('resultSection');
                resultSection.classList.remove('hidden');
                resultSection.scrollIntoView({ behavior: 'smooth' });
                
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerHTML = 'Submit';
            }, 1500);
        } else {
            // Show error message for invalid form
            const errorMessage = document.getElementById('formErrorMessage');
            errorMessage.classList.remove('hidden');
            setTimeout(() => {
                errorMessage.classList.add('hidden');
            }, 3000);
        }
    });
});

