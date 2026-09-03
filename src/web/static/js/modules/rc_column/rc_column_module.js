/**
 * AltDP_3rd RC Column Specialized Module Pack (rc_column_module.js)
 * Implements CODABaseColumn 1:1 migration with P-M diagram
 */
class RCColumnModule {
    constructor() {
        this.key = 'rc_column';
        this.name = 'RC 기둥 (Column)';
        this.category = 'rc';
        this.data = {
            b: 500,
            h: 500,
            cover: 50,
            fck: 30,
            fy: 400,
            rebarPattern: '8-D25',
            pu: 850.0,
            mu: 220.0,
            kl_r: 28.5
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
                { tab: 'section', key: 'b', label: '단면 폭 (b)', default: this.data.b, unit: 'mm' },
                { tab: 'section', key: 'h', label: '단면 높이 (h)', default: this.data.h, unit: 'mm' },
                { tab: 'section', key: 'fck', label: '콘크리트 강도 (fck)', default: this.data.fck, unit: 'MPa' },
                { tab: 'rebar', key: 'cover', label: '피복 두께 (dc)', default: this.data.cover, unit: 'mm' },
                { tab: 'rebar', key: 'rebarPattern', label: '주철근 배열', default: this.data.rebarPattern, type: 'text' },
                { tab: 'load', key: 'pu', label: '계수 축력 (Pu)', default: this.data.pu, unit: 'kN' },
                { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: this.data.mu, unit: 'kN·m' },
                { tab: 'load', key: 'lcbDlg', label: '하중조합 생성기', default: '설정...', hasDialog: true, onOpenDialog: (cur, cb) => window.CommonDialogs.openLoadCombination(cur, cb) },
                { tab: 'option', key: 'kl_r', label: '장주 세장비 (kL/r)', default: this.data.kl_r }
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

        const scale = 220 / Math.max(this.data.b, this.data.h);
        ctx.scale(scale, scale);

        // 1. Concrete body
        window.VDrawPrimitives.drawFrameBody(ctx, this.data.b, this.data.h);

        // 2. 135-deg hook stirrup (tie)
        window.VDrawPrimitives.drawStirrupWithHooks(ctx, this.data.b, this.data.h, this.data.cover, 10);

        // 3. 8 Peripheral Rebars
        const halfB = this.data.b / 2 - this.data.cover - 10;
        const halfH = this.data.h / 2 - this.data.cover - 10;
        const pts = [
            [-halfB, -halfH], [0, -halfH], [halfB, -halfH],
            [-halfB, 0], [halfB, 0],
            [-halfB, halfH], [0, halfH], [halfB, halfH]
        ];
        pts.forEach(([x, y]) => window.VDrawPrimitives.drawSolidRebar(ctx, x, y, 25));

        // 4. Dimensions
        window.VDrawPrimitives.drawDimensionLine(ctx, -this.data.b / 2, this.data.h / 2, this.data.b / 2, this.data.h / 2, `B = ${this.data.b}`, 35, false);
        window.VDrawPrimitives.drawDimensionLine(ctx, this.data.b / 2, -this.data.h / 2, this.data.b / 2, this.data.h / 2, `H = ${this.data.h}`, 35, true);

        ctx.restore();
    }

    renderReport(container) {
        if (!container || !window.ReportRenderer) return;
        window.ReportRenderer.render(container, {
            ...this.data,
            type: 'RC Column'
        }, {
            dcrFlex: this.data.mu / 320.0,
            dcrShear: 0.45
        });
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_column', new RCColumnModule());
}
