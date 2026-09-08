// web/js/components/zoom_controller.js
/**
 * Zoom Controller for A4 Fixed Report Sheet
 * Supports Zoom Slider, Buttons (-, 100%, +, Fit), and Ctrl + Mouse Wheel
 */

(function () {
    class ZoomController {
        constructor() {
            this.currentScale = 1.0;
            this.minScale = 0.5;
            this.maxScale = 2.0;
            this.step = 0.1;
        }

        init() {
            this.bindControls();
            // Initial auto-fit on next animation frame
            requestAnimationFrame(() => {
                this.fitToWidth();
            });
        }

        bindControls() {
            const slider = document.getElementById('report-zoom-slider');
            const btnIn = document.getElementById('btn-zoom-in');
            const btnOut = document.getElementById('btn-zoom-out');
            const btnReset = document.getElementById('btn-zoom-reset');
            const btnFit = document.getElementById('btn-zoom-fit');

            if (slider) {
                slider.addEventListener('input', (e) => {
                    this.setScale(parseFloat(e.target.value));
                });
            }

            if (btnIn) {
                btnIn.addEventListener('click', () => {
                    this.setScale(this.currentScale + this.step);
                });
            }

            if (btnOut) {
                btnOut.addEventListener('click', () => {
                    this.setScale(this.currentScale - this.step);
                });
            }

            if (btnReset) {
                btnReset.addEventListener('click', () => {
                    this.setScale(1.0);
                });
            }

            if (btnFit) {
                btnFit.addEventListener('click', () => {
                    this.fitToWidth();
                });
            }

            // Ctrl + Mouse Wheel Zoom
            const container = document.getElementById('result-container') || document.getElementById('right-pane');
            if (container) {
                container.addEventListener('wheel', (e) => {
                    if (e.ctrlKey) {
                        e.preventDefault();
                        const delta = e.deltaY < 0 ? this.step : -this.step;
                        this.setScale(this.currentScale + delta);
                    }
                }, { passive: false });
            }

            // Window resize auto fit if configured
            window.addEventListener('resize', () => {
                if (this.isFitMode) {
                    this.fitToWidth();
                }
            });
        }

        getTarget() {
            return document.getElementById('main-result-viewport') ||
                document.querySelector('.a4-sheet-container') ||
                document.querySelector('.report-sheet-container') ||
                document.querySelector('.kds-report-sheet') ||
                document.querySelector('.pure-white-sheet');
        }

        setScale(scale) {
            this.currentScale = Math.round(Math.max(this.minScale, Math.min(this.maxScale, scale)) * 100) / 100;
            const target = this.getTarget();
            const label = document.getElementById('zoom-level-label');
            const slider = document.getElementById('report-zoom-slider');

            if (target) {
                target.style.transform = `scale(${this.currentScale})`;
                target.style.transformOrigin = 'top center';
                target.style.transition = 'transform 0.12s ease';
            }

            if (label) {
                label.innerText = `${Math.round(this.currentScale * 100)}%`;
            }

            if (slider && Math.abs(parseFloat(slider.value) - this.currentScale) > 0.01) {
                slider.value = this.currentScale.toFixed(2);
            }
        }

        reapply() {
            this.setScale(this.currentScale);
        }

        fitToWidth() {
            const container = document.getElementById('result-container') || document.getElementById('right-pane') || document.getElementById('pane-right-report');
            if (!container) return;
            const containerWidth = container.clientWidth - 32;
            const targetWidth = 794; // A4 fixed standard width in px
            if (containerWidth > 0) {
                const fitScale = Math.max(this.minScale, Math.min(1.5, Math.floor((containerWidth / targetWidth) * 100) / 100));
                this.isFitMode = true;
                this.setScale(fitScale);
            }
        }
    }

    window.ZoomController = new ZoomController();
})();
