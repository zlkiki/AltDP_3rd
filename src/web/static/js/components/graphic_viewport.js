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
      this.stationCards = [];
      this.stationCanvases = [];
      this.geomCard = null;
      this.mechCard = null;
      this.canvasGeom = null;
      this.canvasMech = null;
      this.ctxGeom = null;
      this.ctxMech = null;
      this.tooltip = null;
      this.captionEl = null;

      // 2. Viewport States (Independent Transform Matrices for 1~3 tiers)
      this.stationStates = [
        { scale: 1.0, panX: 0, panY: 0, isDragging: false, startX: 0, startY: 0, showDimensions: true, interactiveElements: [] },
        { scale: 1.0, panX: 0, panY: 0, isDragging: false, startX: 0, startY: 0, showDimensions: true, interactiveElements: [] },
        { scale: 1.0, panX: 0, panY: 0, isDragging: false, startX: 0, startY: 0, showDimensions: true, interactiveElements: [] }
      ];

      // Backward compatibility aliases
      this.geomState = this.stationStates[0];
      this.mechState = this.stationStates[1];
      this.mechState.is3DMode = false;
      this.mechState.showDCR = true;

      // 3. Cached Data
      this.currentMemberType = 'rc_beam';
      this.currentMemberData = null;
      this.currentCalcResult = null;
      this.stationCount = 3;
    }

    /**
     * Initialize Viewport System
     */
    init() {
      if (this.initialized) return;

      this.container = document.getElementById('center-pane-container');
      this.stationCards = [
        document.getElementById('viewport-card-1'),
        document.getElementById('viewport-card-2'),
        document.getElementById('viewport-card-3')
      ];
      this.stationCanvases = [
        document.getElementById('canvas-station-1'),
        document.getElementById('canvas-station-2'),
        document.getElementById('canvas-station-3')
      ];

      this.geomCard = document.getElementById('viewport-card-geometry') || this.stationCards[0];
      this.mechCard = document.getElementById('viewport-card-mechanics') || this.stationCards[1];
      this.canvasGeom = document.getElementById('canvas-geometry') || this.stationCanvases[0];
      this.canvasMech = document.getElementById('canvas-mechanics') || this.stationCanvases[1];
      this.captionEl = document.getElementById('canvas-caption');

      if (this.canvasGeom) this.ctxGeom = this.canvasGeom.getContext('2d');
      if (this.canvasMech) this.ctxMech = this.canvasMech.getContext('2d');

      // Create Engineering Tooltip Element
      this._createTooltip();

      // Bind Toolbar Action Buttons
      this._bindToolbarActions();

      // Bind Interactive Mouse & Wheel Events for Station Canvases & Legacy Canvases
      this.stationCanvases.forEach((canvas, idx) => {
        if (canvas) this._bindCanvasInteractions(canvas, idx + 1);
      });
      if (this.canvasGeom && !this.stationCanvases.includes(this.canvasGeom)) {
        this._bindCanvasInteractions(this.canvasGeom, 'geom');
      }
      if (this.canvasMech && !this.stationCanvases.includes(this.canvasMech)) {
        this._bindCanvasInteractions(this.canvasMech, 'mech');
      }

      // Setup High-DPI & Resize Observer
      this._setupResizeObserver();

      // Subscribe to EventBus
      this._subscribeEvents();

      // Legacy canvas bridge
      this._setupLegacyBridge();

      this.initialized = true;
      console.log('[GraphicViewport] Initialized successfully with multi-card vertical stack.');

      // Initial redraw if data exists
      this.redrawAll();
    }

    /**
     * Set dynamic station card visibility and title
     */
    setStationCount(count = 3, configs = []) {
      this.stationCount = Math.max(1, Math.min(3, count));
      for (let i = 1; i <= 3; i++) {
        const card = document.getElementById(`viewport-card-${i}`);
        const resizer = document.getElementById(`resizer-center-v${i - 1}`);
        const isVisible = i <= this.stationCount;
        if (card) card.style.display = isVisible ? 'flex' : 'none';
        if (resizer) resizer.style.display = (isVisible && i > 1) ? 'block' : 'none';

        if (isVisible && configs[i - 1]) {
          const cfg = configs[i - 1];
          const titleEl = document.getElementById(`title-viewport-${i}`);
          if (titleEl && cfg.title) titleEl.textContent = cfg.title;
          const captionEl = document.getElementById(`canvas-caption-${i}`);
          if (captionEl && cfg.caption) captionEl.textContent = cfg.caption;
        }
      }
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
      // 1. Station 1 / Geometry Viewport Actions
      [1, 2, 3].forEach((idx) => {
        const btnFit = document.getElementById(`btn-fit-${idx}`);
        if (btnFit) btnFit.addEventListener('click', () => this.fitViewport(idx));

        const btnZoomIn = document.getElementById(`btn-zoom-in-${idx}`);
        if (btnZoomIn) btnZoomIn.addEventListener('click', () => this.zoomStep(idx, 1.25));

        const btnZoomOut = document.getElementById(`btn-zoom-out-${idx}`);
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => this.zoomStep(idx, 0.8));

        const btnToggleDim = document.getElementById(`btn-toggle-dim-${idx}`);
        if (btnToggleDim) {
          btnToggleDim.addEventListener('click', () => {
            const st = this.stationStates[idx - 1];
            if (st) {
              st.showDimensions = !st.showDimensions;
              btnToggleDim.classList.toggle('active', st.showDimensions);
              this._triggerRedraw(idx);
            }
          });
        }
      });

      // Legacy Toolbar Actions
      const btnFitGeom = document.getElementById('btn-fit-geom');
      if (btnFitGeom) btnFitGeom.addEventListener('click', () => this.fitViewport(1));

      const btnZoomInGeom = document.getElementById('btn-zoom-in-geom');
      if (btnZoomInGeom) btnZoomInGeom.addEventListener('click', () => this.zoomStep(1, 1.25));

      const btnZoomOutGeom = document.getElementById('btn-zoom-out-geom');
      if (btnZoomOutGeom) btnZoomOutGeom.addEventListener('click', () => this.zoomStep(1, 0.8));

      const btnToggleDimLegacy = document.getElementById('btn-toggle-dim');
      if (btnToggleDimLegacy) {
        btnToggleDimLegacy.addEventListener('click', () => {
          this.geomState.showDimensions = !this.geomState.showDimensions;
          btnToggleDimLegacy.classList.toggle('active', this.geomState.showDimensions);
          this._triggerRedraw(1);
        });
      }

      const btnFitMech = document.getElementById('btn-fit-mech');
      if (btnFitMech) btnFitMech.addEventListener('click', () => this.fitViewport(2));

      const btnToggle3D = document.getElementById('btn-toggle-3d');
      if (btnToggle3D) {
        btnToggle3D.addEventListener('click', () => {
          this.mechState.is3DMode = !this.mechState.is3DMode;
          btnToggle3D.classList.toggle('active', this.mechState.is3DMode);
          this._triggerRedraw(2);
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
      const state = this._getState(type);

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

    _getState(type) {
      if (typeof type === 'number') {
        const idx = Math.max(0, Math.min(2, type - 1));
        return this.stationStates[idx];
      }
      if (type === 'geom' || type === 'station-1') return this.stationStates[0];
      if (type === 'mech' || type === 'station-2') return this.stationStates[1];
      if (type === 'station-3') return this.stationStates[2];
      return this.stationStates[0];
    }

    /**
     * Zoom centered at specific coordinate
     */
    zoomAt(type, factor, cx, cy) {
      const state = this._getState(type);
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
      let canvas = null;
      if (typeof type === 'number') {
        canvas = this.stationCanvases[type - 1] || document.getElementById(`canvas-station-${type}`);
      } else if (type === 'geom') {
        canvas = this.canvasGeom || this.stationCanvases[0];
      } else if (type === 'mech') {
        canvas = this.canvasMech || this.stationCanvases[1];
      }
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      this.zoomAt(type, factor, rect.width / 2, rect.height / 2);
    }

    /**
     * Reset Viewport to fit content (Scale 1.0, Pan 0, 0)
     */
    fitViewport(type) {
      const state = this._getState(type);
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
        this.stationCanvases.forEach((c) => this._updateCanvasResolution(c));
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
      this.stationCanvases.forEach((c) => this._updateCanvasResolution(c));
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
      const d = this.currentMemberData || {};
      const capText = (d.b && d.h) ? `${d.b} x ${d.h} mm` : ((d.B && d.H) ? `${d.B} x ${d.H} mm` : (d.section_name || ''));
      if (this.captionEl && capText) this.captionEl.textContent = capText;
      [1, 2, 3].forEach((idx) => {
        const el = document.getElementById(`canvas-caption-${idx}`);
        if (el && capText) el.textContent = capText;
      });
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
      if (this.currentMemberType === 'rc_beam') {
        if (type === 1 || type === 'geom') this.renderStation(1, 'end_i');
        else if (type === 2 || type === 'mech') this.renderStation(2, 'center_m');
        else if (type === 3) this.renderStation(3, 'end_j');
        else this.redrawAll();
      } else {
        if (type === 'geom' || type === 1) this.renderGeometry();
        else this.renderMechanics();
      }
    }

    /**
     * Redraw Both/All Viewports
     */
    redrawAll() {
      const memberType = this.currentMemberType || 'rc_beam';
      const data = this.currentMemberData || {};

      if (memberType === 'rc_beam') {
        const cap = (data.b && data.h) ? `${data.b} x ${data.h} mm` : '400 x 600 mm';
        this.setStationCount(3, [
          { title: '📐 단부( i ) 단면 배근도 (End-I Section)', caption: cap },
          { title: '📐 중앙( m ) 단면 배근도 (Center-M Section)', caption: cap },
          { title: '📐 단부( j ) 단면 배근도 (End-J Section)', caption: cap }
        ]);
        this.renderStation(1, 'end_i');
        this.renderStation(2, 'center_m');
        this.renderStation(3, 'end_j');
      } else {
        this.setStationCount(2, [
          { title: '📐 단면 형상 및 배근도 (Geometry)', caption: this.captionEl?.textContent || '' },
          { title: '📐 역학 해석 및 P-M 상관도 (Mechanics)', caption: 'KDS 기준' }
        ]);
        this.renderGeometry();
        this.renderMechanics();
      }
    }

    /**
     * Render Dedicated Station Section Canvas
     */
    renderStation(stationIndex, stationKey) {
      const canvas = this.stationCanvases[stationIndex - 1] || document.getElementById(`canvas-station-${stationIndex}`);
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const rect = canvas.parentElement ? canvas.parentElement.getBoundingClientRect() : canvas.getBoundingClientRect();
      const w = rect.width || canvas.width / (window.devicePixelRatio || 1) || 500;
      const h = rect.height || canvas.height / (window.devicePixelRatio || 1) || 300;

      const stIdx = Math.max(0, Math.min(2, stationIndex - 1));
      const state = this.stationStates[stIdx];

      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      const dpr = window.devicePixelRatio || 1;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      // Apply Pan & Zoom Transform
      ctx.translate(state.panX, state.panY);
      ctx.translate(w / 2, h / 2);
      ctx.scale(state.scale, state.scale);
      ctx.translate(-w / 2, -h / 2);

      state.interactiveElements = [];

      const data = this.currentMemberData || { b: 400, h: 600, cover: 40 };
      const result = this.currentCalcResult || {};

      if (window.VectorRCBeam && typeof window.VectorRCBeam.renderStationSection === 'function') {
        const hits = window.VectorRCBeam.renderStationSection(ctx, w, h, stationKey, data, result, state.showDimensions);
        if (Array.isArray(hits)) {
          state.interactiveElements = hits;
        }
      } else {
        this._renderDefaultGrid(ctx, w, h, `${stationKey} 단면 상세도`);
      }

      ctx.restore();
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
