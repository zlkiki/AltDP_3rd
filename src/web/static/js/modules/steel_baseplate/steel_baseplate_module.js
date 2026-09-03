/**
 * AltDP_3rd Steel Baseplate Specialized Module Pack (steel_baseplate_module.js)
 */
class SteelBaseplateModule {
    constructor() {
        this.key = 'steel_baseplate';
        this.name = '철골 주각부 (Baseplate)';
        this.category = 'steel';
        this.data = {
            bpWidth: 500,
            bpHeight: 500,
            bpThk: 30,
            boltDia: 'M24',
            boltCount: 4,
            fck: 27,
            fyPlate: 275,
            pu: 600.0,
            mu: 95.0,
            vu: 80.0
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
                { tab: 'section', key: 'bpWidth', label: '플레이트 가로 (B)', default: this.data.bpWidth, unit: 'mm' },
                { tab: 'section', key: 'bpHeight', label: '플레이트 세로 (N)', default: this.data.bpHeight, unit: 'mm' },
                { tab: 'section', key: 'bpThk', label: '플레이트 두께 (tp)', default: this.data.bpThk, unit: 'mm' },
                { tab: 'rebar', key: 'boltDia', label: '앵커볼트 규격', default: this.data.boltDia, type: 'text' },
                { tab: 'rebar', key: 'boltCount', label: '볼트 개수', default: this.data.boltCount, unit: '개' },
                { tab: 'section', key: 'fck', label: '기초 콘크리트 강도 (fck)', default: this.data.fck, unit: 'MPa' },
                { tab: 'load', key: 'pu', label: '계수 축력 (Pu)', default: this.data.pu, unit: 'kN' },
                { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: this.data.mu, unit: 'kN·m' },
                { tab: 'load', key: 'vu', label: '계수 전단력 (Vu)', default: this.data.vu, unit: 'kN' },
                { tab: 'option', key: 'groutThk', label: '무수축 그라우트 두께', default: 30, unit: 'mm' }
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

        const scale = 200 / Math.max(this.data.bpWidth, this.data.bpHeight);
        ctx.scale(scale, scale);

        const halfB = this.data.bpWidth / 2;
        const halfN = this.data.bpHeight / 2;

        // 1. Baseplate Body (Plan view)
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 2.0;
        ctx.fillRect(-halfB, -halfN, this.data.bpWidth, this.data.bpHeight);
        ctx.strokeRect(-halfB, -halfN, this.data.bpWidth, this.data.bpHeight);

        // 2. Central H-Column Outline Sketch
        const colH = 250;
        const colB = 125;
        ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.2;
        ctx.fillRect(-colB / 2, -colH / 2, colB, colH);
        ctx.strokeRect(-colB / 2, -colH / 2, colB, colH);

        // 3. 4 Anchor Bolt Holes
        const boltOffset = 60;
        const bolts = [
            [-halfB + boltOffset, -halfN + boltOffset],
            [halfB - boltOffset, -halfN + boltOffset],
            [-halfB + boltOffset, halfN - boltOffset],
            [halfB - boltOffset, halfN - boltOffset]
        ];

        bolts.forEach(([bx, by]) => {
            ctx.beginPath();
            ctx.arc(bx, by, 12, 0, Math.PI * 2);
            ctx.fillStyle = '#f59e0b';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Crosshair
            ctx.beginPath();
            ctx.moveTo(bx - 16, by); ctx.lineTo(bx + 16, by);
            ctx.moveTo(bx, by - 16); ctx.lineTo(bx, by + 16);
            ctx.strokeStyle = '#0f172a';
            ctx.lineWidth = 1.0;
            ctx.stroke();
        });

        // 4. Dimensions
        window.VDrawPrimitives.drawDimensionLine(ctx, -halfB, halfN, halfB, halfN, `B = ${this.data.bpWidth}`, 35, false);
        window.VDrawPrimitives.drawDimensionLine(ctx, halfB, -halfN, halfB, halfN, `N = ${this.data.bpHeight}`, 35, true);

        ctx.restore();
    }

    renderReport(container) {
        if (!container || !window.ReportRenderer) return;
        window.ReportRenderer.render(container, {
            ...this.data,
            name: 'Steel Baseplate',
            b: this.data.bpWidth,
            h: this.data.bpHeight,
            type: 'Steel Baseplate'
        }, {
            dcrFlex: this.data.mu / 125.0,
            dcrShear: this.data.vu / 110.0
        });
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('steel_baseplate', new SteelBaseplateModule());
}
