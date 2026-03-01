class ScrollReveal {
    constructor() {
        this.items = document.querySelectorAll('.scroll-reveal');
        this.init();
    }
    
    init() {
        this.checkVisibility();
        window.addEventListener('scroll', () => this.checkVisibility());
    }
    
    checkVisibility() {
        this.items.forEach(item => {
            const rect = item.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            
            if (rect.top < windowHeight * 0.8) {
                item.classList.add('revealed');
            }
        });
    }
}

class CounterAnimation {
    constructor() {
        this.counters = document.querySelectorAll('.counter');
        this.init();
    }
    
    init() {
        this.counters.forEach(counter => {
            const target = parseInt(counter.dataset.target);
            const duration = parseInt(counter.dataset.duration) || 2000;
            const startTime = performance.now();
            
            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                const current = Math.round(target * easeOutQuart);
                
                counter.textContent = current;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    counter.textContent = target;
                }
            };
            
            requestAnimationFrame(animate);
        });
    }
}

class ParticleEffect {
    constructor(container) {
        this.container = container;
        this.particles = [];
        this.init();
    }
    
    init() {
        this.createParticles();
        this.animate();
    }
    
    createParticles() {
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: var(--secondary);
                border-radius: 50%;
                pointer-events: none;
                opacity: 0;
            `;
            this.container.appendChild(particle);
            this.particles.push({
                element: particle,
                x: Math.random() * 100,
                y: Math.random() * 100,
                speedX: (Math.random() - 0.5) * 2,
                speedY: (Math.random() - 0.5) * 2,
                life: Math.random()
            });
        }
    }
    
    animate() {
        this.particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            p.life += 0.01;
            
            if (p.life > 1) {
                p.life = 0;
                p.x = Math.random() * 100;
                p.y = Math.random() * 100;
            }
            
            p.element.style.left = p.x + '%';
            p.element.style.top = p.y + '%';
            p.element.style.opacity = Math.sin(p.life * Math.PI);
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ScrollReveal();
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                new CounterAnimation(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    document.querySelectorAll('.counter-container').forEach(container => {
        observer.observe(container);
    });
    
    document.querySelectorAll('.particle-effect').forEach(el => {
        new ParticleEffect(el);
    });
});