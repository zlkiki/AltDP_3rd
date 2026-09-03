// web/js/components/theme_manager.js
/**
 * Theme Manager (Dark / Light Dual Theme Controller)
 * Handles theme toggling, persistence, and visual canvas synchronization.
 */

(function () {
    const THEME_KEY = 'altdp_theme_mode';

    class ThemeManager {
        constructor() {
            this.currentTheme = localStorage.getItem(THEME_KEY) || localStorage.getItem('altdp_custom_default_theme') || 'dark';
        }

        init() {
            this.applyTheme(this.currentTheme);
            this.bindEvents();
        }

        bindEvents() {
            const toggleBtn = document.getElementById('btn-theme-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => {
                    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
                    this.setTheme(newTheme);
                });
            }
        }

        setTheme(theme) {
            this.currentTheme = theme;
            localStorage.setItem(THEME_KEY, theme);
            this.applyTheme(theme);

            // Re-render canvas with new theme background if needed
            if (window.CanvasRenderer && typeof window.CanvasRenderer.redrawCurrent === 'function') {
                window.CanvasRenderer.redrawCurrent();
            }
        }

        applyTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            const toggleBtn = document.getElementById('btn-theme-toggle');
            if (toggleBtn) {
                toggleBtn.innerText = theme === 'dark' ? '🌙' : '☀️';
                toggleBtn.title = theme === 'dark' ? '라이트 테마로 변경' : '다크 테마로 변경';
            }
        }

        getTheme() {
            return this.currentTheme;
        }
    }

    window.ThemeManager = new ThemeManager();
})();
