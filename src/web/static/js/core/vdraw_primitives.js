/**
 * AltDP_3rd VDraw Geometric Primitives (vdraw_primitives.js)
 * Implements 135-degree hooked stirrups, solid round rebars, and CAD dimensions
 */
const VDrawPrimitives = {
    /**
     * Draw concrete rectangular body with hatching
     */
    drawFrameBody(ctx, b, h, options = {}) {
        const halfB = b / 2;
        const halfH = h / 2;
        ctx.save();

        // 1. Fill body with engineering gradient / hatching
        const grad = ctx.createLinearGradient(-halfB, -halfH, halfB, halfH);
        grad.addColorStop(0, options.bgStart || '#1e293b');
        grad.addColorStop(1, options.bgEnd || '#0f172a');
        ctx.fillStyle = grad;
        ctx.fillRect(-halfB, -halfH, b, h);

        // 2. Concrete boundary outline
        ctx.strokeStyle = options.borderColor || '#64748b';
        ctx.lineWidth = options.borderWidth || 2.0;
        ctx.strokeRect(-halfB, -halfH, b, h);

        ctx.restore();
    },

    /**
     * Draw closed rectangular stirrup with 135-degree hooks
     */
    drawStirrupWithHooks(ctx, b, h, cover, stirrupDia = 10, options = {}) {
        const halfB = b / 2;
        const halfH = h / 2;
        const innerLeft = -halfB + cover;
        const innerRight = halfB - cover;
        const innerTop = -halfH + cover;
        const innerBottom = halfH - cover;

        ctx.save();
        ctx.strokeStyle = options.color || '#f59e0b';
        ctx.lineWidth = options.lineWidth || 2.5;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        // 1. Closed rectangular loop
        ctx.beginPath();
        ctx.rect(innerLeft, innerTop, innerRight - innerLeft, innerBottom - innerTop);
        ctx.stroke();

        // 2. 135-degree hooks at top corners
        // Hook tail length = 6 * db (min 20px in display scale)
        const hookLen = Math.max(16, stirrupDia * 1.5);
        const hookAngle = (135 * Math.PI) / 180; // 135 deg to rad
        const dx = Math.cos(hookAngle) * hookLen;
        const dy = Math.sin(hookAngle) * hookLen;

        // Top-Left Corner 135° Hook
        ctx.beginPath();
        ctx.moveTo(innerLeft, innerTop);
        ctx.lineTo(innerLeft - dx, innerTop + dy);
        ctx.stroke();

        // Top-Right Corner 135° Hook
        ctx.beginPath();
        ctx.moveTo(innerRight, innerTop);
        ctx.lineTo(innerRight + dx, innerTop + dy);
        ctx.stroke();

        ctx.restore();
    },

    /**
     * Draw solid circular rebar with white outline
     */
    drawSolidRebar(ctx, x, y, barDia = 25, options = {}) {
        const radius = Math.max(3, barDia / 2);
        ctx.save();

        // Solid inner circle
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = options.color || '#38bdf8';
        ctx.fill();

        // Crisp white border
        ctx.strokeStyle = options.borderColor || '#ffffff';
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // Specular highlight dot
        ctx.beginPath();
        ctx.arc(x - radius * 0.3, y - radius * 0.3, radius * 0.25, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.fill();

        ctx.restore();
    },

    /**
     * Draw engineering dimension line with arrowheads
     */
    drawDimensionLine(ctx, x1, y1, x2, y2, text, offset = 30, isVertical = false) {
        ctx.save();
        ctx.strokeStyle = '#94a3b8';
        ctx.fillStyle = '#cbd5e1';
        ctx.lineWidth = 1.2;
        ctx.font = '11px "Inter", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        const arrow = 5;

        if (isVertical) {
            const x = x1 + offset;
            ctx.beginPath();
            ctx.moveTo(x1, y1); ctx.lineTo(x + (offset > 0 ? 6 : -6), y1);
            ctx.moveTo(x2, y2); ctx.lineTo(x + (offset > 0 ? 6 : -6), y2);
            ctx.moveTo(x, y1); ctx.lineTo(x, y2);
            ctx.stroke();

            // Arrows
            ctx.beginPath();
            ctx.moveTo(x - arrow, y1 + arrow * 1.5); ctx.lineTo(x, y1); ctx.lineTo(x + arrow, y1 + arrow * 1.5);
            ctx.moveTo(x - arrow, y2 - arrow * 1.5); ctx.lineTo(x, y2); ctx.lineTo(x + arrow, y2 - arrow * 1.5);
            ctx.stroke();

            // Text with rotated baseline
            ctx.save();
            ctx.translate(x + (offset > 0 ? 14 : -14), (y1 + y2) / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText(text, 0, 0);
            ctx.restore();
        } else {
            const y = y1 + offset;
            ctx.beginPath();
            ctx.moveTo(x1, y1); ctx.lineTo(x1, y + (offset > 0 ? 6 : -6));
            ctx.moveTo(x2, y2); ctx.lineTo(x2, y + (offset > 0 ? 6 : -6));
            ctx.moveTo(x1, y); ctx.lineTo(x2, y);
            ctx.stroke();

            // Arrows
            ctx.beginPath();
            ctx.moveTo(x1 + arrow * 1.5, y - arrow); ctx.lineTo(x1, y); ctx.lineTo(x1 + arrow * 1.5, y + arrow);
            ctx.moveTo(x2 - arrow * 1.5, y - arrow); ctx.lineTo(x2, y); ctx.lineTo(x2 - arrow * 1.5, y + arrow);
            ctx.stroke();

            ctx.fillText(text, (x1 + x2) / 2, y + (offset > 0 ? 14 : -14));
        }

        ctx.restore();
    },

    /**
     * Draw leader text pointing to rebar or element
     */
    drawLeaderText(ctx, targetX, targetY, textX, textY, text) {
        ctx.save();
        ctx.strokeStyle = '#38bdf8';
        ctx.fillStyle = '#f8fafc';
        ctx.lineWidth = 1.0;
        ctx.font = '11px "Inter", monospace';

        // Leader line
        ctx.beginPath();
        ctx.arc(targetX, targetY, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.moveTo(targetX, targetY);
        ctx.lineTo(textX, textY);
        const tailX = textX > targetX ? textX + 30 : textX - 30;
        ctx.lineTo(tailX, textY);
        ctx.stroke();

        // Text
        ctx.textAlign = textX > targetX ? 'left' : 'right';
        ctx.textBaseline = 'bottom';
        ctx.fillText(text, textX > targetX ? textX + 5 : textX - 5, textY - 2);

        ctx.restore();
    }
};

window.VDrawPrimitives = VDrawPrimitives;
