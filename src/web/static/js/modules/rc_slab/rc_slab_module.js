/**
 * AltDP_3rd RC Slab Specialized Module Pack (rc_slab_module.js)
 */
class RCSlabModule {
    constructor() {
        this.key = 'rc_slab';
        this.name = 'RC 슬래브 (Slab)';
        this.category = 'rc';
        this.data = {
            lx: 4000,
            ly: 6000,
            thk: 200,
            cover: 30,
            rebarType: 'D13 @ 200',
            deadLoad: 5.5,
            liveLoad: 3.0,
            mu: 32.5
        };
    }

    async mount(context) {
        this.context = context;
        if (context.memberData) Object.assign(this.data, context.memberData);

        this.renderForm(context.formContainer);
        this.renderCanvas(context.canvas);
        this.renderReport(context.reportContainer);
    }

    unmount() {}

    onParamChange(payload) {
        if (payload.key) this.data[payload.key] = payload.value;
        if (this.context) {
            this.renderCanvas(this.context.canvas);
            this.renderReport(this.context.reportContainer);
        }
    }

    renderForm(container) {
        if (!container || !window.FormBuilder) return;

        const schema = {
            fields: [
                { tab: 'section', key: 'thk', label: '슬래브 두께 (thk)', default: this.data.thk, unit: 'mm' },
                { tab: 'section', key: 'lx', label: '단변 지간 (Lx)', default: this.data.lx, unit: 'mm' },
                { tab: 'section', key: 'ly', label: '장변 지간 (Ly)', default: this.data.ly, unit: 'mm' },
                { tab: 'rebar', key: 'cover', label: '피복 두께 (dc)', default: this.data.cover, unit: 'mm' },
                { tab: 'rebar', key: 'rebarType', label: '주철근 규격', default: this.data.rebarType, type: 'text' },
                { tab: 'load', key: 'deadLoad', label: '고정하중 (D)', default: this.data.deadLoad, unit: 'kN/m²' },
                { tab: 'load', key: 'liveLoad', label: '활하중 (L)', default: this.data.liveLoad, unit: 'kN/m²' },
                { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: this.data.mu, unit: 'kN·m/m' },
                { tab: 'option', key: 'type', label: '해석 방식', type: 'select', options: [{ value: '2way', label: '2방향 직접설계법' }, { value: 'fem', label: 'FEM 탄성해석' }] }
            ]
        };

        window.FormBuilder.build(container, schema, this.data, (k, v) => {
            if (k) this.data[k] = v;
            this.renderCanvas(this.context.canvas);
            this.renderReport(this.context.reportContainer);
        });
    }

    renderCanvas(canvas) {
        if (!canvas || !window.VDrawPrimitives) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;

        ctx.clearRect(0, 0, w, h);
        ctx.save();
        ctx.translate(w / 2, h / 2);

        // Slab cross-section strip (b=1000mm, h=thk)
        const b = 600;
        const thk = this.data.thk;
        const scale = 220 / b;
        ctx.scale(scale, scale);

        // Concrete strip
        window.VDrawPrimitives.drawFrameBody(ctx, b, thk);

        // Rebar rows
        const rebarY = thk / 2 - this.data.cover;
        for (let i = -b / 2 + 30; i <= b / 2 - 30; i += 70) {
            window.VDrawPrimitives.drawSolidRebar(ctx, i, rebarY, 13);
        }

        // Dimensions
        window.VDrawPrimitives.drawDimensionLine(ctx, -b / 2, thk / 2, b / 2, thk / 2, `1m Strip`, 30, false);
        window.VDrawPrimitives.drawDimensionLine(ctx, b / 2, -thk / 2, b / 2, thk / 2, `t = ${thk}`, 30, true);

        ctx.restore();
    }

    renderReport(container) {
        if (!container || !window.ReportRenderer) return;
        window.ReportRenderer.render(container, {
            ...this.data,
            b: 1000,
            h: this.data.thk,
            type: 'RC Slab'
        }, {
            dcrFlex: this.data.mu / 48.0,
            dcrShear: 0.35
        });
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_slab', new RCSlabModule());
}
