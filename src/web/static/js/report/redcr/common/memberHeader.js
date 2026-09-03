// web/js/report/redcr/common/memberHeader.js
/**
 * AltDP Member Designer - Member Header & Identification Blocks
 * Zero-Build Vanilla JavaScript & Browser Global Namespace
 */

(function () {
    const H = (typeof window !== 'undefined' ? (window.RedcrFormat || (window.RedcrCommon && window.RedcrCommon.formatHelpers)) : null) || {
        esc: s => String(s || ''),
        nf: (v, d = 3) => Number(v || 0).toFixed(d),
        dcrColor: d => (d <= 1.0 ? '#1a7a4a' : '#b00020')
    };

    const V = (typeof window !== 'undefined' ? (window.RedcrVerdict || (window.RedcrCommon && window.RedcrCommon.verdictBadge)) : null) || {
        levelBadge: l => `<span>${l}</span>`,
        worstPerf: (a, b) => a || b || '—'
    };

    /** RC 보 상세 헤더 (단일 부재 및 내진 양단 I/J) */
    function memberHeaderRcBeam(input) {
        if (!input) return '';
        const { level, endI, endJ, sourceLabel, story, sectionLabel, dcrFlex, dcrShear, memberName } = input;
        
        const name = memberName || sourceLabel || 'RC Beam';
        const st = story || '1F';
        const sect = sectionLabel || 'RC-BEAM';

        // 일반 KDS 설계 모드 헤더
        if (!level) {
            const df = dcrFlex !== undefined ? Number(dcrFlex) : (endI?.dcr_flex ?? endI?.DCR_flex ?? 0);
            const dv = dcrShear !== undefined ? Number(dcrShear) : (endI?.dcr_shear ?? endI?.DCR_shear ?? 0);
            const maxDcr = Math.max(df, dv);
            const isOk = maxDcr <= 1.0;
            const badgeCls = isOk ? 'badge-ok' : 'badge-ng';
            const badgeText = isOk ? 'PASS (O.K)' : 'FAIL (N.G)';

            return `
<div class="detail-set-header" style="padding:6px 0 8px;border-bottom:2px solid #1a3a5c;margin-bottom:12px;">
  <table style="width:100%;border-collapse:collapse;border:none;">
    <tr>
      <td style="border:none;padding:0;width:60%;vertical-align:middle;">
        <div style="font-size:13pt;font-weight:700;color:#1a3a5c;margin-bottom:2px;">
          ${H.esc(name)} <span style="font-size:10pt;font-weight:500;color:#666;">(${H.esc(sect)})</span>
        </div>
        <div style="color:#555;font-size:9.5pt;">
          위치: <b>${H.esc(st)}</b> &nbsp;|&nbsp; 설계기준: <b>KDS 14 20 (콘크리트구조설계기준)</b>
        </div>
      </td>
      <td style="border:none;padding:0;width:40%;text-align:right;vertical-align:middle;">
        <div style="margin-bottom:3px;">
          <span class="${badgeCls}" style="display:inline-block;padding:3px 10px;border-radius:3px;font-weight:700;font-size:10pt;border:1.5px solid ${isOk ? '#1a7a4a' : '#b00020'};color:${isOk ? '#1a7a4a' : '#b00020'};background:${isOk ? '#e8f5e9' : '#ffebee'};">
            ${badgeText}
          </span>
        </div>
        <div style="color:#555;font-size:9.5pt;">
          휨 DCR: <b style="color:${H.dcrColor(df)}">${H.nf(df, 3)}</b> &nbsp;|&nbsp;
          전단 DCR: <b style="color:${H.dcrColor(dv)}">${H.nf(dv, 3)}</b>
        </div>
      </td>
    </tr>
  </table>
</div>`;
        }

        // 내진 1차 평가 모드 헤더 (I/J 양단)
        const target = level.performanceLevel || 'LS';
        const perfI = endI?.perfLevel ?? '—';
        const perfJ = endJ?.perfLevel ?? '—';
        const memberPerf = V.worstPerf(perfI, perfJ);
        const pickDcrFlex = (r) => (target === 'IO' ? r?.DCR_IO : target === 'LS' ? r?.DCR_LS : r?.DCR_CP) || 0;
        const dcrFlexI = endI ? pickDcrFlex(endI) : NaN;
        const dcrFlexJ = endJ ? pickDcrFlex(endJ) : NaN;
        const dcrVI = endI?.DCR_shear ?? NaN;
        const dcrVJ = endJ?.DCR_shear ?? NaN;

        return `
<div class="detail-set-header" style="padding:6px 0 8px;border-bottom:2px solid #1a3a5c;margin-bottom:12px;">
  <table style="width:100%;border-collapse:collapse;border:none;">
    <tr>
      <td style="border:none;padding:0;width:60%;vertical-align:top;">
        <div style="font-size:12pt;font-weight:700;color:#1a3a5c;margin-bottom:2px;">
          Story <b>${H.esc(st)}</b> &nbsp;|&nbsp; Member <b>${H.esc(name)}</b> &nbsp;|&nbsp; Section <b>${H.esc(sect)}</b>
        </div>
        <div style="color:#666;font-size:9.5pt;">
          양단 검토구간: <b>I단 &amp; J단</b> &nbsp;|&nbsp; 하중조합: <code>LCB${endI?.comboId || 1}</code>
        </div>
      </td>
      <td style="border:none;padding:0;width:40%;text-align:right;vertical-align:top;">
        <div style="color:#666;font-size:9pt;margin-bottom:3px;">
          재현주기 ${level.returnPeriod || 2400}yr &middot; 목표수준 <b>${target}</b>
        </div>
        <div style="margin-bottom:3px;">
          I: ${V.levelBadge(perfI)} &nbsp; J: ${V.levelBadge(perfJ)} &nbsp;&rarr;&nbsp; <b>부재판정:</b> ${V.levelBadge(memberPerf)}
        </div>
        <div style="color:#555;font-size:9pt;">
          DCR_flex: I=<span style="color:${H.dcrColor(dcrFlexI)};font-weight:700">${H.nf(dcrFlexI, 3)}</span>,
          J=<span style="color:${H.dcrColor(dcrFlexJ)};font-weight:700">${H.nf(dcrFlexJ, 3)}</span>
          &nbsp;|&nbsp; DCR_V:
          I=<span style="color:${H.dcrColor(dcrVI)};font-weight:700">${H.nf(dcrVI, 3)}</span>,
          J=<span style="color:${H.dcrColor(dcrVJ)};font-weight:700">${H.nf(dcrVJ, 3)}</span>
        </div>
      </td>
    </tr>
  </table>
</div>`;
    }

    /** RC 기둥 상세 헤더 (My/Mz 이중 축 포함) */
    function memberHeaderRcColumn(input) {
        if (!input) return '';
        const { level, rI_My, rI_Mz, rJ_My, rJ_Mz, sourceLabel, story, sectionLabel, memberName, dcrPM, dcrShear } = input;
        
        const name = memberName || sourceLabel || 'RC Column';
        const st = story || '1F';
        const sect = sectionLabel || 'RC-COL';

        // 일반 KDS 설계 모드 헤더
        if (!level) {
            const dpm = dcrPM !== undefined ? Number(dcrPM) : (rI_My?.dcr_pm ?? rI_My?.dcr ?? 0);
            const dv = dcrShear !== undefined ? Number(dcrShear) : (rI_My?.dcr_shear ?? 0);
            const maxDcr = Math.max(dpm, dv);
            const isOk = maxDcr <= 1.0;
            const badgeCls = isOk ? 'badge-ok' : 'badge-ng';
            const badgeText = isOk ? 'PASS (O.K)' : 'FAIL (N.G)';

            return `
<div class="detail-set-header" style="padding:6px 0 8px;border-bottom:2px solid #1a3a5c;margin-bottom:12px;">
  <table style="width:100%;border-collapse:collapse;border:none;">
    <tr>
      <td style="border:none;padding:0;width:60%;vertical-align:middle;">
        <div style="font-size:13pt;font-weight:700;color:#1a3a5c;margin-bottom:2px;">
          ${H.esc(name)} <span style="font-size:10pt;font-weight:500;color:#666;">(${H.esc(sect)})</span>
        </div>
        <div style="color:#555;font-size:9.5pt;">
          위치: <b>${H.esc(st)}</b> &nbsp;|&nbsp; 설계기준: <b>KDS 14 20 (콘크리트구조기준 - P-M 축력휨검토)</b>
        </div>
      </td>
      <td style="border:none;padding:0;width:40%;text-align:right;vertical-align:middle;">
        <div style="margin-bottom:3px;">
          <span class="${badgeCls}" style="display:inline-block;padding:3px 10px;border-radius:3px;font-weight:700;font-size:10pt;border:1.5px solid ${isOk ? '#1a7a4a' : '#b00020'};color:${isOk ? '#1a7a4a' : '#b00020'};background:${isOk ? '#e8f5e9' : '#ffebee'};">
            ${badgeText}
          </span>
        </div>
        <div style="color:#555;font-size:9.5pt;">
          P-M DCR: <b style="color:${H.dcrColor(dpm)}">${H.nf(dpm, 3)}</b> &nbsp;|&nbsp;
          전단 DCR: <b style="color:${H.dcrColor(dv)}">${H.nf(dv, 3)}</b>
        </div>
      </td>
    </tr>
  </table>
</div>`;
        }

        // 이중 축 4슬롯 내진 평가 모드 헤더
        const target = level.performanceLevel || 'LS';
        const slots = [
            { lbl: 'I_My', r: rI_My },
            { lbl: 'I_Mz', r: rI_Mz },
            { lbl: 'J_My', r: rJ_My },
            { lbl: 'J_Mz', r: rJ_Mz }
        ];
        const memberPerf = slots.reduce((acc, s) => V.worstPerf(acc, s.r?.perfLevel), undefined) ?? '—';
        const pickDcrFlex = (r) => (target === 'IO' ? r?.DCR_IO : target === 'LS' ? r?.DCR_LS : r?.DCR_CP) || 0;
        const perfBadges = slots.map(s => `${s.lbl}: ${V.levelBadge(s.r?.perfLevel ?? '—')}`).join(' &nbsp; ');

        return `
<div class="detail-set-header" style="padding:6px 0 8px;border-bottom:2px solid #1a3a5c;margin-bottom:12px;">
  <table style="width:100%;border-collapse:collapse;border:none;">
    <tr>
      <td style="border:none;padding:0;width:55%;vertical-align:top;">
        <div style="font-size:12pt;font-weight:700;color:#1a3a5c;margin-bottom:2px;">
          Story <b>${H.esc(st)}</b> &nbsp;|&nbsp; Member <b>${H.esc(name)}</b> &nbsp;|&nbsp; Section <b>${H.esc(sect)}</b>
        </div>
        <div style="color:#666;font-size:9.5pt;">
          검토 축: <b>I &amp; J단 (My 및 Mz 이중 축 4슬롯)</b>
        </div>
      </td>
      <td style="border:none;padding:0;width:45%;text-align:right;vertical-align:top;">
        <div style="color:#666;font-size:9pt;margin-bottom:3px;">
          재현주기 ${level.returnPeriod || 2400}yr &middot; 목표 <b>${target}</b>
        </div>
        <div style="margin-bottom:3px;">${perfBadges} &rarr; <b>종합:</b> ${V.levelBadge(memberPerf)}</div>
      </td>
    </tr>
  </table>
</div>`;
    }

    const MemberHeader = {
        memberHeaderRcBeam,
        memberHeaderRcColumn
    };

    if (typeof window !== 'undefined') {
        window.RedcrCommon = window.RedcrCommon || {};
        window.RedcrCommon.memberHeader = MemberHeader;
        window.RedcrHeader = MemberHeader;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = MemberHeader;
    }
})();
