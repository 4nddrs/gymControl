/**
 * GYM CONTROL - JavaScript Principal
 */

// Cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏋️ Gym Control - Sistema iniciado');
    
    // Resaltar el enlace activo en la navegación
    highlightActiveNavLink();
    
    // Inicializar tooltips si existen
    initTooltips();
});

/**
 * Resalta el enlace activo en la navegación
 */
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--primary-color)';
            link.style.fontWeight = '600';
        }
    });
}

/**
 * Inicializa tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Muestra tooltip
 */
function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#333';
    tooltip.style.color = '#fff';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '14px';
    tooltip.style.zIndex = '1000';
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
    tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';
}

/**
 * Oculta tooltip
 */
function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Función helper para hacer peticiones AJAX
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en la petición:', error);
        throw error;
    }
}

/**
 * Muestra un mensaje de notificación
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '1rem 1.5rem';
    notification.style.borderRadius = '8px';
    notification.style.zIndex = '9999';
    notification.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    
    // Colores según el tipo
    const colors = {
        success: { bg: '#10b981', color: '#fff' },
        error: { bg: '#ef4444', color: '#fff' },
        warning: { bg: '#f59e0b', color: '#fff' },
        info: { bg: '#2563eb', color: '#fff' }
    };
    
    notification.style.backgroundColor = colors[type].bg;
    notification.style.color = colors[type].color;
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Formatea una fecha
 */
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

/**
 * Formatea un número como moneda
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Exportar funciones para uso global
window.gymControl = {
    fetchAPI,
    showNotification,
    formatDate,
    formatCurrency
};
