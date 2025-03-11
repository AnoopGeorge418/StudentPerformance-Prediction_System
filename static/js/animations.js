document.addEventListener('DOMContentLoaded', function() {
    // Initialize particle background
    initParticles();
    
    // Add animation delays to navbar buttons
    animateNavButtons();
    
    // Add form submit animation
    setupFormAnimation();
    
    // Set up hover effects
    setupHoverEffects();
});

function initParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    
    // Random properties
    const size = Math.random() * 5 + 1;
    const posX = Math.random() * 100;
    const posY = Math.random() * 100;
    const opacity = Math.random() * 0.5 + 0.1;
    const duration = Math.random() * 20 + 10;
    const delay = Math.random() * 5;
    
    // Set styles
    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background-color: rgba(255, 255, 255, ${opacity});
        border-radius: 50%;
        top: ${posY}%;
        left: ${posX}%;
        animation: float ${duration}s ease-in-out infinite;
        animation-delay: -${delay}s;
        box-shadow: 0 0 ${size * 2}px rgba(255, 255, 255, ${opacity});
    `;
    
    container.appendChild(particle);
}

function animateNavButtons() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach((button, index) => {
        button.style.setProperty('--index', index);
        
        // Add click animation
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                pointer-events: none;
                width: ${button.offsetWidth * 2}px;
                height: ${button.offsetWidth * 2}px;
                top: ${y - button.offsetWidth}px;
                left: ${x - button.offsetWidth}px;
                transform: scale(0);
                animation: ripple 0.6s linear;
                opacity: 0.4;
            `;
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

function setupFormAnimation() {
    const form = document.getElementById('predictionForm');
    const resultsSection = document.getElementById('resultsSection');
    
    // For demonstration purposes - in a real app, this would be handled by your form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            // In development, prevent default for preview purposes
            // In production, remove this line to allow actual form submission
            e.preventDefault();
            
            const submitButton = document.getElementById('predictBtn');
            
            // Add loading state
            submitButton.innerHTML = '<span class="flex items-center justify-center"><i class="fas fa-spinner fa-spin mr-2"></i> Processing...</span>';
            submitButton.disabled = true;
            
            // Simulate processing
            setTimeout(() => {
                // Show results
                resultsSection.style.display = 'block';
                
                // Reset button
                submitButton.innerHTML = '<span class="flex items-center justify-center gap-2"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" /></svg>Predict your Maths Score</span>';
                submitButton.disabled = false;
                
                // Scroll to results if needed
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }, 1500);
        });
    }
}

function setupHoverEffects() {
    // Add animation to form inputs on focus
    const inputs = document.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('animate__animated', 'animate__pulse');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('animate__animated', 'animate__pulse');
        });
    });
}

// Add ripple animation
document.documentElement.style.cssText += `
@keyframes ripple {
    0% {
        transform: scale(0);
        opacity: 0.4;
    }
    100% {
        transform: scale(1);
        opacity: 0;
    }
}

@keyframes float {
    0%, 100% {
        transform: translateY(0) rotate(0deg);
    }
    50% {
        transform: translateY(-20px) rotate(10deg);
    }
}
`;