// Jolly Cabs Operations Management Suite (JOMS) - Global Javascript Logic

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initGlobalSearch();
    initNotificationsAlerts();
});

/**
 * Theme Manager (Dark / Light Mode)
 */
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Read saved theme or default to light
    const currentTheme = localStorage.getItem('joms-theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(themeToggle, currentTheme);
    
    themeToggle.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('joms-theme', newTheme);
        updateThemeIcon(themeToggle, newTheme);
        
        // Dispatch custom event to let charts re-draw with appropriate grid colors
        window.dispatchEvent(new Event('theme-changed'));
    });
}

function updateThemeIcon(btn, theme) {
    const icon = btn.querySelector('i');
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
        btn.title = 'Switch to Light Mode';
    } else {
        icon.className = 'fas fa-moon';
        btn.title = 'Switch to Dark Mode';
    }
}

/**
 * Sidebar collapsing and responsive controls
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const container = document.querySelector('.app-container');
    const menuToggle = document.getElementById('menu-toggle');
    
    if (!menuToggle || !sidebar || !container) return;
    
    // Load collapse state
    const isCollapsed = localStorage.getItem('joms-sidebar-collapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        container.classList.add('expanded');
    }
    
    // Toggle action
    const toggleSidebar = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (window.innerWidth > 768) {
            sidebar.classList.toggle('collapsed');
            container.classList.toggle('expanded');
            localStorage.setItem('joms-sidebar-collapsed', sidebar.classList.contains('collapsed'));
        } else {
            sidebar.classList.toggle('mobile-open');
        }
    };
    
    // Bind both click and touch events for absolute responsiveness on mobile devices
    menuToggle.addEventListener('click', toggleSidebar);
    menuToggle.addEventListener('touchend', toggleSidebar, { passive: false });
    
    // Close sidebar on mobile clicking outside
    const handleOutsideClick = (e) => {
        if (window.innerWidth <= 768 && sidebar.classList.contains('mobile-open')) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
            }
        }
    };
    
    document.addEventListener('click', handleOutsideClick);
    document.addEventListener('touchend', handleOutsideClick, { passive: true });
}

/**
 * Global search routing and real-time list filtering
 */
function initGlobalSearch() {
    const searchInput = document.getElementById('global-search-input');
    if (!searchInput) return;
    
    // Real-time table filtering if we are on a listing page
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        const tableRows = document.querySelectorAll('.data-table tbody tr');
        
        tableRows.forEach(row => {
            const textContent = row.textContent.toLowerCase();
            if (textContent.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
    
    // Trigger global search redirect on Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query.length > 0) {
                // If it's a number, try navigating to booking details, otherwise default search route
                if (/^\d+$/.test(query)) {
                    window.location.href = `/bookings/detail/${query}`;
                } else {
                    window.location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        }
    });
}

/**
 * Fades out flash notification alerts automatically
 */
function initNotificationsAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

/**
 * Common modal delete confirmation dialog
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}
