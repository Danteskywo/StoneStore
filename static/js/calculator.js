class StoneCalculator {
    constructor() {
        this.stoneId = document.querySelector('[data-stone-id]')?.dataset.stoneId;
        this.pricePerSqm = parseFloat(document.querySelector('[data-price]')?.dataset.price || 0);
        this.sinkPrice = parseFloat(document.querySelector('[data-sink-price]')?.dataset.sinkPrice || 3000);
        this.hobPrice = parseFloat(document.querySelector('[data-hob-price]')?.dataset.hobPrice || 2500);
        this.installPricePerM = parseFloat(document.querySelector('[data-install-price]')?.dataset.installPrice || 1500);
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.calculate();
    }
    
    bindEvents() {
        document.getElementById('calc-length')?.addEventListener('input', () => this.calculate());
        document.getElementById('calc-width')?.addEventListener('input', () => this.calculate());
        
        document.querySelectorAll('input[name="thickness"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateSelectedClass(radio, 'thickness-options');
                this.calculate();
            });
        });
        
        document.querySelectorAll('input[name="edge_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateSelectedClass(radio, null);
                this.calculate();
            });
        });
        
        document.getElementById('has-sink')?.addEventListener('change', () => this.calculate());
        document.getElementById('has-hob')?.addEventListener('change', () => this.calculate());
        document.getElementById('need-install')?.addEventListener('change', () => this.calculate());
        
        document.getElementById('toggle-details')?.addEventListener('click', () => this.toggleDetails());
        document.getElementById('save-calculation')?.addEventListener('click', () => this.showSaveModal());
        document.getElementById('order-with-params')?.addEventListener('click', () => this.orderWithParams());
        document.getElementById('open-3d-viewer')?.addEventListener('click', () => this.open3DViewer());
        
        document.querySelector('#save-calculation-modal .modal-close')?.addEventListener('click', () => this.hideSaveModal());
        document.getElementById('cancel-save')?.addEventListener('click', () => this.hideSaveModal());
        document.getElementById('confirm-save')?.addEventListener('click', () => this.saveCalculation());
    }
    
    updateSelectedClass(radio, parentId) {
        const parent = parentId ? document.getElementById(parentId) : radio.closest('.param-options');
        parent.querySelectorAll('.param-option').forEach(opt => opt.classList.remove('selected'));
        radio.closest('.param-option').classList.add('selected');
    }
    
    calculate() {
        const length = parseFloat(document.getElementById('calc-length').value) || 0;
        const width = parseFloat(document.getElementById('calc-width').value) || 0;
        const hasSink = document.getElementById('has-sink')?.checked || false;
        const hasHob = document.getElementById('has-hob')?.checked || false;
        const needInstall = document.getElementById('need-install')?.checked || false;
        
        const area = length * width;
        const perimeter = 2 * (length + width);
        
        const stonePrice = area * this.pricePerSqm;
        const cuttingPrice = perimeter * 500;
        const edgePrice = perimeter * 800;
        const sinkPrice = hasSink ? this.sinkPrice : 0;
        const hobPrice = hasHob ? this.hobPrice : 0;
        const installPrice = needInstall ? perimeter * this.installPricePerM : 0;
        
        const total = stonePrice + cuttingPrice + edgePrice + sinkPrice + hobPrice + installPrice;
        
        document.getElementById('preview-area').textContent = area.toFixed(2) + ' м²';
        document.getElementById('preview-perimeter').textContent = perimeter.toFixed(2) + ' м';
        document.getElementById('total-price').textContent = this.formatPrice(total);
        
        document.getElementById('detail-stone').textContent = this.formatPrice(stonePrice);
        document.getElementById('detail-cutting').textContent = this.formatPrice(cuttingPrice);
        document.getElementById('detail-edge').textContent = this.formatPrice(edgePrice);
        document.getElementById('detail-sink').textContent = this.formatPrice(sinkPrice);
        document.getElementById('detail-hob').textContent = this.formatPrice(hobPrice);
        document.getElementById('detail-install').textContent = this.formatPrice(installPrice);
        
        document.getElementById('detail-sink-row').style.display = hasSink ? 'flex' : 'none';
        document.getElementById('detail-hob-row').style.display = hasHob ? 'flex' : 'none';
        document.getElementById('detail-install-row').style.display = needInstall ? 'flex' : 'none';
        
        this.currentData = {
            length, width, area, perimeter,
            stonePrice, cuttingPrice, edgePrice,
            sinkPrice, hobPrice, installPrice, total
        };
    }
    
    formatPrice(price) {
        return Math.round(price).toLocaleString('ru-RU') + ' ₽';
    }
    
    toggleDetails() {
        const details = document.getElementById('price-details');
        const btn = document.getElementById('toggle-details');
        
        if (details.style.display === 'none') {
            details.style.display = 'block';
            btn.textContent = 'Скрыть детали ▲';
        } else {
            details.style.display = 'none';
            btn.textContent = 'Показать детали ▼';
        }
    }
    
    showSaveModal() {
        document.getElementById('save-calculation-modal').style.display = 'block';
        document.getElementById('calc-name').value = `Столешница ${this.currentData?.area.toFixed(2) || 1.2}м²`;
    }
    
    hideSaveModal() {
        document.getElementById('save-calculation-modal').style.display = 'none';
    }
    
    saveCalculation() {
        const name = document.getElementById('calc-name').value;
        
        fetch('/api/save-calculation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                stone_id: this.stoneId,
                name: name,
                length: this.currentData.length,
                width: this.currentData.width,
                thickness: document.querySelector('input[name="thickness"]:checked').value,
                edge_type: document.querySelector('input[name="edge_type"]:checked').value,
                has_sink: document.getElementById('has-sink').checked,
                has_hob: document.getElementById('has-hob').checked,
                need_install: document.getElementById('need-install').checked
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('✅ Расчет успешно сохранен!', 'success');
                this.hideSaveModal();
            } else {
                this.showNotification('❌ Ошибка при сохранении', 'error');
            }
        });
    }
    
    orderWithParams() {
        const params = new URLSearchParams({
            stone: this.stoneId,
            length: this.currentData.length,
            width: this.currentData.width,
            thickness: document.querySelector('input[name="thickness"]:checked').value,
            edge_type: document.querySelector('input[name="edge_type"]:checked').value,
            has_sink: document.getElementById('has-sink').checked ? '1' : '0',
            has_hob: document.getElementById('has-hob').checked ? '1' : '0',
            need_install: document.getElementById('need-install').checked ? '1' : '0'
        });
        
        window.location.href = `/order/?${params.toString()}`;
    }
    
    open3DViewer() {
        sessionStorage.setItem('stone3d_params', JSON.stringify({
            stoneId: this.stoneId,
            length: this.currentData.length,
            width: this.currentData.width,
            thickness: document.querySelector('input[name="thickness"]:checked').value
        }));
        
        window.open('/3d-viewer/', '_blank');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new StoneCalculator();
});