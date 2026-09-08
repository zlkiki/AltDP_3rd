/**
 * AltDP_3rd High-Precision Vertical Multi-Card Viewport Engine (graphic_viewport.js)
 * Conforms to Requirements 21-4 & docs/07 section 4.3.
 * 
 * Features:
 * - Dual stacked vertical viewport management (Top: Geometry & Detailing, Bottom: Mechanics & P-M)
 * - Independent mouse-wheel zoom (cursor-centered) and drag panning per viewport
 * - Toolbar actions: Fit, Zoom In/Out, Dimension line toggle, 3D diagram toggle, DCR bar toggle
 * - Retina High-DPI auto-scaling & ResizeObserver integration
 * - Real-time engineering hover tooltip (rebar diameter, spacing, bolt spec, force points)
 * - Reactive synchronization with EventBus and ProjectStore
 * - Legacy canvas compatibility layer (sectionCanvas, pmChartCanvas aliases)
 */

(function (global) {
  'use strict';

  class GraphicViewport {
    constructor() {
      this.initialized = false;

      // 1. Viewport DOM elements
      this.container = null;
      this.geomCard = null;
      this.mechCard = null;
      this.canvasGeom = null;
      this.canvasMech = null;
      this.ctxGeom = null;
      this.ctxMech = null;
      this.tooltip = null;
      this.captionEl = null;

      // 2. Viewport States (Independent Transform Matrices)
      this.geomState = {
        scale: 1.0,
        panX: 0,
        panY: 0,
        isDragging: false,
        startX: 0,
        startY: 0,
        showDimensions: true,
        interactiveElements: [] // Array of { type, x, y, r, title, detail }
      };

      this.mechState = {
        scale: 1.0,
        panX: 0,
        panY: 0,
        isDragging: false,
        startX: 0,
        startY: 0,
        is3DMode: false,
        showDCR: true,
        interactiveElements: [] // Array of { type, x, y, r, title, detail }
      };

      // 3. Cached Data
      this.currentMemberType = 'rc_beam';
      this.currentMemberData = null;
      this.currentCalcResult = null;
    }

    /**
     * Initialize Viewport System
     */
    init() {
      if (this.initialized) return;

      this.container = document.getElementById('center-pane-container');
      this.geomCard = document.getElementById('viewport-card-geometry');
      this.mechCard = document.getElementById('viewport-card-mechanics');
      this.canvasGeom = document.getElementById('canvas-geometry');
      this.canvasMech = document.getElementById('canvas-mechanics');
      this.captionEl = document.getElementById('canvas-caption');

      if (!this.canvasGeom || !this.canvasMech) {
        console.warn('[GraphicViewport] Canvas elements not found in DOM.');
        return;
      }

      this.ctxGeom = this.canvasGeom.getContext('2d');
      this.ctxMech = this.canvasMech.getContext('2d');

      // Create Engineering Tooltip Element
      this._createTooltip();

      // Bind Toolbar Action Buttons
      this._bindToolbarActions();

      // Bind Interactive Mouse & Wheel Events
      this._bindCanvasInteractions(this.canvasGeom, 'geom');
      this._bindCanvasInteractions(this.canvasMech, 'mech');

      // Setup High-DPI & Resize Observer
      this._setupResizeObserver();

      // Subscribe to EventBus
      this._subscribeEvents();

      // Legacy canvas bridge
      this._setupLegacyBridge();

      this.initialized = true;
      console.log('[GraphicViewport] Initialized successfully with 2-tier vertical stack.');

      // Initial redraw if data exists
      this.redrawAll();
    }

    /**
     * Create floating tooltip element in center pane
     */
    _createTooltip() {
      if (document.getElementById('viewport-canvas-tooltip')) {
        this.tooltip = document.getElementById('viewport-canvas-tooltip');
        return;
      }
      this.tooltip = document.createElement('div');
      this.tooltip.id = 'viewport-canvas-tooltip';
      this.tooltip.className = 'canvas-tooltip';
      this.tooltip.innerHTML = '<div class="tip-title"></div><div class="tip-detail"></div>';
      
      const parent = this.container || document.body;
      parent.appendChild(this.tooltip);
    }

    /**
     * Bind Toolbar Action Buttons
     */
    _bindToolbarActions() {
      // Top Geometry Viewport Actions
      const btnFitGeom = document.getElementById('btn-fit-geom');
      if (btnFitGeom) btnFitGeom.addEventListener('click', () => this.fitViewport('geom'));

      const btnZoomInGeom = document.getElementById('btn-zoom-in-geom');
      if (btnZoomInGeom) btnZoomInGeom.addEventListener('click', () => this.zoomStep('geom', 1.25));

      const btnZoomOutGeom = document.getElementById('btn-zoom-out-geom');
      if (btnZoomOutGeom) btnZoomOutGeom.addEventListener('click', () => this.zoomStep('geom', 0.8));

      const btnToggleDim = document.getElementById('btn-toggle-dim');
      if (btnToggleDim) {
        btnToggleDim.addEventListener('click', () => {
          this.geomState.showDimensions = !this.geomState.showDimensions;
          btnToggleDim.classList.toggle('active', this.geomState.showDimensions);
          this.renderGeometry();
        });
      }

      // Bottom Mechanics Viewport Actions
      const btnFitMech = document.getElementById('btn-fit-mech');
      if (btnFitMech) btnFitMech.addEventListener('click', () => this.fitViewport('mech'));

      const btnToggle3D = document.getElementById('btn-toggle-3d');
      if (btnToggle3D) {
        btnToggle3D.addEventListener('click', () => {
          this.mechState.is3DMode = !this.mechState.is3DMode;
          btnToggle3D.classList.toggle('active', this.mechState.is3DMode);
          this.renderMechanics();
        });
      }

      const btnToggleDCR = document.getElementById('btn-toggle-dcr-bar');
      if (btnToggleDCR) {
        btnToggleDCR.addEventListener('click', () => {
          this.mechState.showDCR = !this.mechState.showDCR;
          btnToggleDCR.classList.toggle('active', this.mechState.showDCR);
          const dcrCard = document.getElementById('dcrCard');
          if (dcrCard) {
            dcrCard.style.display = this.mechState.showDCR ? 'flex' : 'none';
          }
        });
      }
    }

    /**
     * Bind interactive mouse drag, zoom, and hover tooltip events
     */
    _bindCanvasInteractions(canvas, type) {
      if (!canvas) return;
      const state = type === 'geom' ? this.geomState : this.mechState;

      // 1. Mouse Down (Start Pan)
      canvas.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return; // Left click only
        state.isDragging = true;
        state.startX = e.clientX - state.panX;
        state.startY = e.clientY - state.panY;
        canvas.style.cursor = 'grabbing';
      });

      // 2. Mouse Move (Pan & Hit Testing for Tooltips)
      window.addEventListener('mousemove', (e) => {
        if (state.isDragging) {
          state.panX = e.clientX - state.startX;
          state.panY = e.clientY - state.startY;
          this._triggerRedraw(type);
          return;
        }

        // Hover Tooltip Check if mouse is over canvas
        if (e.target === canvas) {
          this._handleHoverTooltip(canvas, e, state);
        }
      });

      // 3. Mouse Up / Leave (End Pan)
      window.addEventListener('mouseup', () => {
        if (state.isDragging) {
          state.isDragging = false;
          canvas.style.cursor = 'grab';
        }
      });

      canvas.addEventListener('mouseleave', () => {
        if (this.tooltip) {
          this.tooltip.classList.remove('visible');
        }
      });

      // 4. Mouse Wheel (Cursor-Centered Zoom)
      canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
        this.zoomAt(type, zoomFactor, e.offsetX, e.offsetY);
      }, { passive: false });
    }

    /**
     * Zoom centered at specific coordinate
     */
    zoomAt(type, factor, cx, cy) {
      const state = type === 'geom' ? this.geomState : this.mechState;
      const newScale = Math.min(Math.max(state.scale * factor, 0.2), 6.0);

      // Adjust pan so the cursor point remains stationary in canvas space
      state.panX = cx - (cx - state.panX) * (newScale / state.scale);
      state.panY = cy - (cy - state.panY) * (newScale / state.scale);
      state.scale = newScale;

      this._triggerRedraw(type);
    }

    /**
     * Step zoom by factor centered at canvas midpoint
     */
    zoomStep(type, factor) {
      const canvas = type === 'geom' ? this.canvasGeom : this.canvasMech;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      this.zoomAt(type, factor, rect.width / 2, rect.height / 2);
    }

    /**
     * Reset Viewport to fit content (Scale 1.0, Pan 0, 0)
     */
    fitViewport(type) {
      const state = type === 'geom' ? this.geomState : this.mechState;
      state.scale = 1.0;
      state.panX = 0;
      state.panY = 0;
      this._triggerRedraw(type);
    }

    /**
     * Hit testing for engineering interactive tooltips
     */
    _handleHoverTooltip(canvas, event, state) {
      if (!this.tooltip || !state.interactiveElements || state.interactiveElements.length === 0) {
        if (this.tooltip) this.tooltip.classList.remove('visible');
        return;
      }

      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      // Transform mouse coordinate into transformed canvas content space
      const halfW = rect.width / 2;
      const halfH = rect.height / 2;
      const contentX = (mouseX - state.panX - halfW) / state.scale + halfW;
      const contentY = (mouseY - state.panY - halfH) / state.scale + halfH;

      let hit = null;
      for (const el of state.interactiveElements) {
        const dx = contentX - el.x;
        const dy = contentY - el.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const threshold = Math.max(el.r || 8, 8);
        if (dist <= threshold) {
          hit = el;
          break;
        }
      }

      if (hit) {
        const titleEl = this.tooltip.querySelector('.tip-title');
        const detailEl = this.tooltip.querySelector('.tip-detail');
        if (titleEl) titleEl.textContent = hit.title || '부재 상세 제원';
        if (detailEl) detailEl.textContent = hit.detail || '';

        // Position relative to viewport container
        const containerRect = (this.container || document.body).getBoundingClientRect();
        const tipX = event.clientX - containerRect.left;
        const tipY = event.clientY - containerRect.top;

        this.tooltip.style.left = `${tipX}px`;
        this.tooltip.style.top = `${tipY}px`;
        this.tooltip.classList.add('visible');
      } else {
        this.tooltip.classList.remove('visible');
      }
    }

    /**
     * High-DPI setup and ResizeObserver
     */
    _setupResizeObserver() {
      const resizeHandler = () => {
        this._updateCanvasResolution(this.canvasGeom);
        this._updateCanvasResolution(this.canvasMech);
        this.redrawAll();
      };

      if (window.ResizeObserver && this.container) {
        const ro = new ResizeObserver(() => resizeHandler());
        ro.observe(this.container);
      } else {
        window.addEventListener('resize', resizeHandler);
      }

      // Initial setup
      this._updateCanvasResolution(this.canvasGeom);
      this._updateCanvasResolution(this.canvasMech);
    }

    _updateCanvasResolution(canvas) {
      if (!canvas) return;
      const rect = canvas.parentElement ? canvas.parentElement.getBoundingClientRect() : canvas.getBoundingClientRect();
      const w = Math.max(rect.width || 400, 100);
      const h = Math.max(rect.height || 260, 100);
      const dpr = window.devicePixelRatio || 1;

      if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
        canvas.width = Math.floor(w * dpr);
        canvas.height = Math.floor(h * dpr);
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.scale(dpr, dpr);
      }
    }

    /**
     * Subscribe to EventBus and ProjectStore
     */
    _subscribeEvents() {
      if (window.EventBus) {
        const sub = (typeof window.EventBus.subscribe === 'function')
          ? window.EventBus.subscribe.bind(window.EventBus)
          : (typeof window.EventBus.on === 'function' ? window.EventBus.on.bind(window.EventBus) : null);

        if (sub) {
          sub('member:selected', (e) => {
            const data = e.detail || e;
            this.setMember(data.type || data.moduleKey || 'rc_beam', data.data || data);
          });

          sub('calculation:completed', (e) => {
            const res = e.detail || e;
            this.setCalculationResult(res);
          });

          sub('input:changed', (e) => {
            const d = e.detail || e;
            if (d && d.data) {
              this.updateMemberData(d.data);
            }
          });
        }
      }
    }

    /**
     * Legacy canvas bridge for sectionCanvas / pmChartCanvas
     */
    _setupLegacyBridge() {
      // Connect legacy window functions if they exist
      const origRedraw = window.CanvasRenderer ? window.CanvasRenderer.redrawCurrent : null;
      if (window.CanvasRenderer) {
        window.CanvasRenderer.redrawCurrent = () => {
          this.redrawAll();
          if (origRedraw) {
            try { origRedraw.call(window.CanvasRenderer); } catch (_) {}
          }
        };
      }
    }

    /**
     * Set active member type and input data
     */
    setMember(memberType, data) {
      this.currentMemberType = memberType || 'rc_beam';
      this.currentMemberData = data || {};
      this._updateCaption();
      this.redrawAll();
    }

    /**
     * Update member data in-place and redraw
     */
    updateMemberData(newData) {
      this.currentMemberData = Object.assign({}, this.currentMemberData, newData);
      this._updateCaption();
      this.redrawAll();
    }

    /**
     * Set calculation result for mechanics view
     */
    setCalculationResult(result) {
      this.currentCalcResult = result;
      this._updateDCRCard(result);
      this.renderMechanics();
    }

    /**
     * Update Caption Text
     */
    _updateCaption() {
      if (!this.captionEl) return;
      const d = this.currentMemberData || {};
      if (d.b && d.h) {
        this.captionEl.textContent = `${d.b} x ${d.h} mm`;
      } else if (d.B && d.H) {
        this.captionEl.textContent = `${d.B} x ${d.H} mm`;
      } else if (d.section_name) {
        this.captionEl.textContent = d.section_name;
      }
    }

    /**
     * Update Floating DCR Card
     */
    _updateDCRCard(result) {
      const dcrValEl = document.getElementById('dcrValue');
      const dcrBarEl = document.getElementById('dcrBar');
      if (!dcrValEl || !result) return;

      const dcr = result.max_dcr !== undefined ? result.max_dcr : (result.dcr !== undefined ? result.dcr : 0.0);
      const isOK = dcr <= 1.0;

      dcrValEl.textContent = `${dcr.toFixed(3)} ${isOK ? 'OK' : 'NG'}`;
      dcrValEl.className = isOK ? 'ok' : 'ng';

      if (dcrBarEl) {
        const fillPercent = Math.min(Math.round(dcr * 100), 100);
        dcrBarEl.style.setProperty('--dcr-fill', `${fillPercent}%`);
        dcrBarEl.className = `dcr-gauge-bar ${isOK ? 'ok' : 'ng'}`;
      }
    }

    /**
     * Redraw specific viewport
     */
    _triggerRedraw(type) {
      if (type === 'geom') this.renderGeometry();
      else this.renderMechanics();
    }

    /**
     * Redraw Both Viewports
     */
    redrawAll() {
      this.renderGeometry();
      this.renderMechanics();
    }

    /**
     * Render Top Viewport: Geometry & Detailing (Canvas-Geometry)
     */
    renderGeometry() {
      if (!this.canvasGeom) return;
      const canvas = this.canvasGeom;
      const ctx = this.ctxGeom || canvas.getContext('2d');
      const rect = canvas.getBoundingClientRect();
      const w = rect.width || canvas.width / (window.devicePixelRatio || 1) || 500;
      const h = rect.height || canvas.height / (window.devicePixelRatio || 1) || 300;

      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      const dpr = window.devicePixelRatio || 1;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      // Apply Pan & Zoom Transform
      ctx.translate(this.geomState.panX, this.geomState.panY);
      ctx.translate(w / 2, h / 2);
      ctx.scale(this.geomState.scale, this.geomState.scale);
      ctx.translate(-w / 2, -h / 2);

      // Reset interactive element list
      this.geomState.interactiveElements = [];

      const memberType = this.currentMemberType || 'rc_beam';
      const data = this.currentMemberData || { b: 400, h: 600, cover: 50 };

      // Render via Renderer2D or fallback
      if (window.Renderer2D && typeof window.Renderer2D.renderTopViewportGeometry === 'function') {
        const hits = window.Renderer2D.renderTopViewportGeometry(ctx, w, h, memberType, data, this.geomState.showDimensions);
        if (Array.isArray(hits)) {
          this.geomState.interactiveElements = hits;
        }
      } else if (window.Renderer2D && typeof window.Renderer2D.drawSection === 'function') {
        window.Renderer2D.drawSection(ctx, w, h, memberType, data);
      } else {
        this._renderDefaultGrid(ctx, w, h, '단면 및 배근 상세도');
      }

      ctx.restore();
    }

    /**
     * Render Bottom Viewport: Mechanics & P-M Diagram (Canvas-Mechanics)
     */
    renderMechanics() {
      if (!this.canvasMech) return;
      const canvas = this.canvasMech;
      const ctx = this.ctxMech || canvas.getContext('2d');
      const rect = canvas.getBoundingClientRect();
      const w = rect.width || canvas.width / (window.devicePixelRatio || 1) || 500;
      const h = rect.height || canvas.height / (window.devicePixelRatio || 1) || 300;

      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      const dpr = window.devicePixelRatio || 1;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      // Apply Pan & Zoom Transform
      ctx.translate(this.mechState.panX, this.mechState.panY);
      ctx.translate(w / 2, h / 2);
      ctx.scale(this.mechState.scale, this.mechState.scale);
      ctx.translate(-w / 2, -h / 2);

      // Reset interactive element list
      this.mechState.interactiveElements = [];

      const memberType = this.currentMemberType || 'rc_beam';
      const result = this.currentCalcResult || {};
      const data = this.currentMemberData || {};

      if (window.Renderer2D && typeof window.Renderer2D.renderBottomViewportMechanics === 'function') {
        const hits = window.Renderer2D.renderBottomViewportMechanics(ctx, w, h, memberType, data, result, this.mechState.is3DMode);
        if (Array.isArray(hits)) {
          this.mechState.interactiveElements = hits;
        }
      } else if (window.PMChartRenderer) {
        // Fallback to PMChartRenderer instance if applicable
        if (!this.pmRenderer) {
          this.pmRenderer = new window.PMChartRenderer('canvas-mechanics');
        }
        if (result.pm_curve || data.pm_curve) {
          this.pmRenderer.render(result.pm_curve ? result : data);
        } else {
          this._renderDefaultGrid(ctx, w, h, '공학 역학 및 P-M 다이어그램');
        }
      } else {
        this._renderDefaultGrid(ctx, w, h, '공학 역학 및 P-M 다이어그램');
      }

      ctx.restore();
    }

    /**
     * Fallback Clean Engineering Grid
     */
    _renderDefaultGrid(ctx, w, h, label) {
      ctx.save();
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, w, h);

      ctx.strokeStyle = 'rgba(148, 163, 184, 0.08)';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 25) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += 25) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      ctx.fillStyle = '#64748b';
      ctx.font = '12px "Pretendard", "Inter", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`📐 ${label} (준비 중)`, w / 2, h / 2);
      ctx.restore();
    }
  }

  // Export Singleton to global scope
  const instance = new GraphicViewport();
  global.GraphicViewport = instance;

  // Auto-init on DOMContentLoaded
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => instance.init());
    } else {
      setTimeout(() => instance.init(), 0);
    }
  }
})(typeof window !== 'undefined' ? window : this);
