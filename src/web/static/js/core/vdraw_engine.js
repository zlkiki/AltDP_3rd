/**
 * AltDP_3rd VDraw Canvas Engine (VDrawEngine)
 * Implements CAD viewport transformations, Pan/Zoom, and coordinate mapping
 */
class VDrawEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        
        // Viewport transformation state
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        
        // Display toggles
        this.showDimensions = true;
        this.showRebarTags = true;
        this.showGrid = true;

        if (this.canvas) {
            this._setupDPI();
            this._setupInteractions();
        }
    }

    _setupDPI() {
        if (!this.canvas) return;
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        const w = rect.width || this.canvas.width || 400;
        const h = rect.height || this.canvas.height || 400;
        
        this.canvas.width = w * dpr;
        this.canvas.height = h * dpr;
        this.ctx = this.canvas.getContext('2d');
        this.ctx.scale(dpr, dpr);
        this.width = w;
        this.height = h;
    }

    _setupInteractions() {
        if (!this.canvas) return;

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
            this.zoom(zoomFactor, e.offsetX, e.offsetY);
        }, { passive: false });

        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left click drag
                this.isDragging = true;
                this.dragStartX = e.clientX - this.offsetX;
                this.dragStartY = e.clientY - this.offsetY;
                this.canvas.style.cursor = 'grabbing';
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.offsetX = e.clientX - this.dragStartX;
                this.offsetY = e.clientY - this.dragStartY;
                this.redraw();
            }
        });

        window.addEventListener('mouseup', () => {
            if (this.isDragging) {
                this.isDragging = false;
                if (this.canvas) this.canvas.style.cursor = 'default';
            }
        });

        this.canvas.addEventListener('dblclick', () => {
            this.fitToScreen();
        });
    }

    zoom(factor, centerX, centerY) {
        const cx = centerX ?? this.width / 2;
        const cy = centerY ?? this.height / 2;

        const newScale = Math.max(0.2, Math.min(5.0, this.scale * factor));
        this.offsetX = cx - (cx - this.offsetX) * (newScale / this.scale);
        this.offsetY = cy - (cy - this.offsetY) * (newScale / this.scale);
        this.scale = newScale;
        this.redraw();
    }

    fitToScreen() {
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.redraw();
    }

    clear() {
        if (!this.ctx) return;
        this.ctx.save();
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.restore();
    }

    beginDraw() {
        this.clear();
        if (!this.ctx) return;
        this.ctx.save();
        this.ctx.translate(this.width / 2 + this.offsetX, this.height / 2 + this.offsetY);
        this.ctx.scale(this.scale, this.scale);
    }

    endDraw() {
        if (!this.ctx) return;
        this.ctx.restore();
    }

    redraw() {
        if (this.onRedrawCallback) {
            this.onRedrawCallback(this);
        }
    }

    setRedrawCallback(cb) {
        this.onRedrawCallback = cb;
    }
}

// Global Singleton Instance
window.VDrawEngine = VDrawEngine;
