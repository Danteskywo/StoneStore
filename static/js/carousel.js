class StoneCarousel {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.items = this.container.querySelectorAll('.carousel-item');
        this.currentIndex = 0;
        this.autoRotate = options.autoRotate !== false;
        this.rotationSpeed = options.speed || 30;
        this.isPaused = false;
        
        this.init();
    }
    
    init() {
        this.createControls();
        this.createPagination();
        this.bindEvents();
        this.startAutoRotate();
    }
    
    createControls() {
        const controls = document.createElement('div');
        controls.className = 'carousel-controls';
        controls.innerHTML = `
            <button class="carousel-btn prev">←</button>
            <button class="carousel-btn pause">⏸</button>
            <button class="carousel-btn next">→</button>
        `;
        
        this.container.parentElement.appendChild(controls);
        
        this.prevBtn = controls.querySelector('.prev');
        this.pauseBtn = controls.querySelector('.pause');
        this.nextBtn = controls.querySelector('.next');
    }
    
    createPagination() {
        const pagination = document.createElement('div');
        pagination.className = 'carousel-pagination';
        
        for (let i = 0; i < this.items.length; i++) {
            const dot = document.createElement('span');
            dot.className = 'pagination-dot';
            dot.dataset.index = i;
            pagination.appendChild(dot);
        }
        
        this.container.parentElement.appendChild(pagination);
        this.paginationDots = pagination.querySelectorAll('.pagination-dot');
        this.updatePagination();
    }
    
    bindEvents() {
        this.prevBtn.addEventListener('click', () => this.rotate(-1));
        this.nextBtn.addEventListener('click', () => this.rotate(1));
        
        this.pauseBtn.addEventListener('click', () => this.togglePause());
        
        this.paginationDots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.goToIndex(index);
            });
        });
        
        this.items.forEach((item, index) => {
            item.addEventListener('click', () => {
                window.location.href = item.dataset.url;
            });
        });
        
        this.container.addEventListener('mouseenter', () => this.pause());
        this.container.addEventListener('mouseleave', () => this.resume());
    }
    
    rotate(direction) {
        const currentRotation = this.getCurrentRotation();
        const newRotation = currentRotation - direction * 60;
        this.container.style.transform = `rotateY(${newRotation}deg)`;
        this.currentIndex = (this.currentIndex + direction + this.items.length) % this.items.length;
        this.updatePagination();
    }
    
    goToIndex(index) {
        const diff = index - this.currentIndex;
        this.rotate(diff);
    }
    
    getCurrentRotation() {
        const transform = this.container.style.transform;
        const match = transform.match(/rotateY\(([-\d.]+)deg\)/);
        return match ? parseFloat(match[1]) : 0;
    }
    
    updatePagination() {
        this.paginationDots.forEach((dot, i) => {
            dot.classList.toggle('active', i === this.currentIndex);
        });
    }
    
    togglePause() {
        if (this.isPaused) {
            this.resume();
        } else {
            this.pause();
        }
    }
    
    pause() {
        this.isPaused = true;
        this.container.classList.add('paused');
        this.pauseBtn.innerHTML = '▶';
    }
    
    resume() {
        this.isPaused = false;
        this.container.classList.remove('paused');
        this.pauseBtn.innerHTML = '⏸';
    }
    
    startAutoRotate() {
        if (!this.autoRotate) return;
        
        setInterval(() => {
            if (!this.isPaused) {
                this.rotate(1);
            }
        }, this.rotationSpeed * 1000 / 6);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new StoneCarousel('stone-carousel', {
        autoRotate: true,
        speed: 30
    });
});