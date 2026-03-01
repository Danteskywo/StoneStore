class Analytics {
    constructor() {
        this.init();
    }
    
    init() {
        this.trackPageView();
        this.trackEvents();
    }
    
    trackPageView() {
        if (typeof ym !== 'undefined') {
            ym(YANDEX_METRIKA_ID, 'hit', window.location.href);
        }
        
        if (typeof gtag !== 'undefined') {
            gtag('config', GA_MEASUREMENT_ID, {
                'page_title': document.title,
                'page_path': window.location.pathname
            });
        }
    }
    
    trackEvent(category, action, label = null, value = null) {
        if (typeof ym !== 'undefined') {
            ym(YANDEX_METRIKA_ID, 'reachGoal', action);
        }
        
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': category,
                'event_label': label,
                'value': value
            });
        }
    }
    
    trackEcommerce(action, data) {
        if (typeof ym !== 'undefined') {
            ym(YANDEX_METRIKA_ID, 'params', {
                'ecommerce': {
                    [action]: data
                }
            });
        }
    }
    
    trackEvents() {
        document.querySelectorAll('[data-product-view]').forEach(el => {
            this.trackEvent('Product', 'View', el.dataset.productName);
        });
        
        document.querySelectorAll('[data-add-to-cart]').forEach(el => {
            el.addEventListener('click', () => {
                this.trackEvent('Cart', 'Add', el.dataset.productName);
            });
        });
        
        document.querySelectorAll('[data-checkout]').forEach(el => {
            el.addEventListener('click', () => {
                this.trackEvent('Checkout', 'Start');
            });
        });
        
        document.querySelectorAll('[data-search]').forEach(el => {
            el.addEventListener('submit', (e) => {
                const query = el.querySelector('input').value;
                this.trackEvent('Search', 'Query', query);
            });
        });
        
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                this.trackEvent('Form', 'Submit', form.id || 'unknown');
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.analytics = new Analytics();
});