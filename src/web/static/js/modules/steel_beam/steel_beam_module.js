/**
 * AltDP_3rd Steel Beam Specialized Module Pack (steel_beam_module.js)
 */
class SteelBeamModule {
    constructor() {
        this.key = 'steel_beam';
        this.name = '철골 보 / 기둥 (Steel Beam)';
        this.category = 'steel';
        this.data = {
            sectionName: 'H-400x200x8x13',
            h: 400,
            b: 200,
            tw: 8,
            tf: 13,
            fy: 275,
            lb: 3000,
            cb: 1.0,
            mu: 165.0,
            vu: 120.0
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
                { tab: 'section', key: 'sectionName', label: '단면 규격', default: this.data.sectionName, type: 'text' },
                { tab: 'section', key: 'secDbDlg', label: 'KS 형강 DB 선택기', default: 'DB 검색...', hasDialog: true, onOpenDialog: (cur, cb) => window.CommonDialogs.openSectionDb(this.data.sectionName, (sec) => {
                    this.data.sectionName = sec.name;
                    this.data.h = sec.h;
                    this.data.b = sec.b;
                    this.data.tw = sec.tw;
                    this.data.tf = sec.tf;
                    this.renderForm(this.context.formContainer);
                    this.renderCanvas(this.context.canvas);
                    this.renderReport(this.context.reportContainer);
                }) },
                { tab: 'section', key: 'fy', label: '강재 항복강도 (Fy)', default: this.data.fy, unit: 'MPa' },
                { tab: 'rebar', key: 'lb', label: '비지지길이 (Lb)', default: this.data.lb, unit: 'mm' },
                { tab: 'rebar', key: 'cb', label: '모멘트 구배계수 (Cb)', default: this.data.cb },
                { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: this.data.mu, unit: 'kN·m' },
                { tab: 'load', key: 'vu', label: '계수 전단력 (Vu)', default: this.data.vu, unit: 'kN' },
                { tab: 'option', key: 'deflLimit', label: '허용 처짐 기준', type: 'select', options: [{ value: '300', label: 'L / 300' }, { value: '400', label: 'L / 400' }] }
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

        const scale = 220 / Math.max(this.data.h, this.data.b);
        ctx.scale(scale, scale);

        const halfH = this.data.h / 2;
        const halfB = this.data.b / 2;
        const tf = this.data.tf;
        const tw = this.data.tw;

        ctx.fillStyle = '#334155';
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.8;

        // Draw I/H-Section
        ctx.beginPath();
        // Top flange
        ctx.moveTo(-halfB, -halfH);
        ctx.lineTo(halfB, -halfH);
        ctx.lineTo(halfB, -halfH + tf);
        ctx.lineTo(tw / 2, -halfH + tf);
        // Web
        ctx.lineTo(tw / 2, halfH - tf);
        // Bottom flange
        ctx.lineTo(halfB, halfH - tf);
        ctx.lineTo(halfB, halfH);
        ctx.lineTo(-halfB, halfH);
        ctx.lineTo(-halfB, halfH - tf);
        ctx.lineTo(-tw / 2, halfH - tf);
        ctx.lineTo(-tw / 2, -halfH + tf);
        ctx.lineTo(-halfB, -halfH + tf);
        ctx.closePath();

        ctx.fill();
        ctx.stroke();

        // Dimensions
        window.VDrawPrimitives.drawDimensionLine(ctx, -halfB, halfH, halfB, halfH, `B = ${this.data.b}`, 35, false);
        window.VDrawPrimitives.drawDimensionLine(ctx, halfB, -halfH, halfB, halfH, `H = ${this.data.h}`, 35, true);

        ctx.restore();
    }

    renderReport(container) {
        if (!container || !window.ReportRenderer) return;
        window.ReportRenderer.render(container, {
            ...this.data,
            name: this.data.sectionName,
            type: 'Steel Beam'
        }, {
            dcrFlex: this.data.mu / 245.0,
            dcrShear: this.data.vu / 195.0
        });
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('steel_beam', new SteelBeamModule());
}
