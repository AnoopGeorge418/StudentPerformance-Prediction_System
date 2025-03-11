document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const themeIcon = themeToggle.querySelector('i');
    
    // Initialize theme
    const currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme);
    
    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Add transition effect to body
        document.body.classList.add('theme-transition');
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 500);
    });
    
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        
        // Update icon
        if (theme === 'dark') {
            themeIcon.className = 'fas fa-sun';
        } else {
            themeIcon.className = 'fas fa-moon';
        }
        
        // Update background elements
        updateBackgroundElements(theme);
    }
    
    function updateBackgroundElements(theme) {
        const bgElements = document.querySelectorAll('#background-effects div');
        
        if (theme === 'dark') {
            bgElements[0].className = 'absolute w-96 h-96 rounded-full bg-blue-600/10 -top-10 -left-10 blur-3xl floating';
            bgElements[1].className = 'absolute w-96 h-96 rounded-full bg-cyan-900/10 bottom-20 right-10 blur-3xl floating';
            bgElements[2].className = 'absolute w-64 h-64 rounded-full bg-blue-900/15 top-1/2 left-1/4 blur-3xl floating';
        } else {
            bgElements[0].className = 'absolute w-96 h-96 rounded-full bg-blue-300/20 -top-10 -left-10 blur-3xl floating';
            bgElements[1].className = 'absolute w-96 h-96 rounded-full bg-cyan-300/20 bottom-20 right-10 blur-3xl floating';
            bgElements[2].className = 'absolute w-64 h-64 rounded-full bg-blue-200/30 top-1/2 left-1/4 blur-3xl floating';
        }
    }
});