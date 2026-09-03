/**
 * AltDP_3rd RC Beam Specialized Module Pack (rc_beam_module.js)
 * Implements CODABeamBase 1:1 migration
 */
class RCBeamModule {
    constructor() {
        this.key = 'rc_beam';
        this.name = 'RC 보 (Beam)';
        this.category = 'rc';
        this.data = {
            b: 400,
            h: 600,
            cover: 50,
            fck: 27,
            fy: 400,
            fys: 400,
            topBars: '4-D25',
            botBars: '4-D25',
            stirrup: 'D10 @ 150',
            mu: 240.0,
            vu: 180.0
        };
    }

    async mount(context) {
        this.context = context;
        if (context.memberData) Object.assign(this.data, context.memberData);

        this.renderForm(context.formContainer);
        this.renderCanvas(context.canvas);
        this.renderReport(context.reportContainer);
    }

    unmount() {
        // Cleanup resources
    }

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
                { tab: 'section', key: 'hasTFlange', label: 'T형 플랜지 상세', default: '설정', hasDialog: true, onOpenDialog: (cur, cb) => window.CommonDialogs.openBeamSectionDetail(cur, cb) },
                { tab: 'rebar', key: 'cover', label: '피복 두께 (dc)', default: this.data.cover, unit: 'mm' },
                { tab: 'rebar', key: 'topBars', label: '상부 주철근', default: this.data.topBars, type: 'text' },
                { tab: 'rebar', key: 'botBars', label: '하부 주철근', default: this.data.botBars, type: 'text' },
                { tab: 'rebar', key: 'stirrup', label: '전단 스터럽', default: this.data.stirrup, type: 'text' },
                { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: this.data.mu, unit: 'kN·m' },
                { tab: 'load', key: 'vu', label: '계수 전단력 (Vu)', default: this.data.vu, unit: 'kN' },
                { tab: 'load', key: 'lcbDlg', label: '하중조합 생성기', default: '설정...', hasDialog: true, onOpenDialog: (cur, cb) => window.CommonDialogs.openLoadCombination(cur, cb) },
                { tab: 'option', key: 'seismic', label: '내진 등급', type: 'select', options: [{ value: 'special', label: '특수 모멘트 골조' }, { value: 'normal', label: '보통 모멘트 골조' }] }
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

        // Scale fit
        const scale = 220 / Math.max(this.data.b, this.data.h);
        ctx.scale(scale, scale);

        // 1. Concrete body
        window.VDrawPrimitives.drawFrameBody(ctx, this.data.b, this.data.h);

        // 2. 135-deg hook stirrup
        window.VDrawPrimitives.drawStirrupWithHooks(ctx, this.data.b, this.data.h, this.data.cover, 10);

        // 3. Rebars (Top 4, Bot 4)
        const innerLeft = -this.data.b / 2 + this.data.cover + 10;
        const innerRight = this.data.b / 2 - this.data.cover - 10;
        const topY = -this.data.h / 2 + this.data.cover + 10;
        const botY = this.data.h / 2 - this.data.cover - 10;

        for (let i = 0; i < 4; i++) {
            const x = innerLeft + (innerRight - innerLeft) * (i / 3);
            window.VDrawPrimitives.drawSolidRebar(ctx, x, topY, 25);
            window.VDrawPrimitives.drawSolidRebar(ctx, x, botY, 25);
        }

        // 4. Dimension lines
        window.VDrawPrimitives.drawDimensionLine(ctx, -this.data.b / 2, this.data.h / 2, this.data.b / 2, this.data.h / 2, `b = ${this.data.b}`, 35, false);
        window.VDrawPrimitives.drawDimensionLine(ctx, this.data.b / 2, -this.data.h / 2, this.data.b / 2, this.data.h / 2, `h = ${this.data.h}`, 35, true);

        ctx.restore();
    }

    renderReport(container) {
        if (!container || !window.ReportRenderer) return;
        window.ReportRenderer.render(container, {
            ...this.data,
            type: 'RC Beam'
        }, {
            dcrFlex: this.data.mu / 335.2,
            dcrShear: this.data.vu / 232.8
        });
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_beam', new RCBeamModule());
}
