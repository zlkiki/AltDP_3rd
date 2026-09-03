"""A4 Structural Calculation Report Generator for AltDP_3rd.

Adheres to KDS 14 20 00 / KDS 14 31 00 calculation reporting standards.
Utilizes Jinja2 templating, KaTeX LaTeX formulas, and CSS Paged Media.
"""

import os
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.report.options import ReportOptions
from src.report.unit_converter import UnitConverter


# Custom Jinja2 Filters
def fmt_num(val: Any, precision: int = 2) -> str:
    """Format float or int to formatted string with specified precision."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return "-"
    try:
        f_val = float(val)
        if precision == 0:
            return f"{f_val:,.0f}"
        return f"{f_val:,.{precision}f}"
    except (ValueError, TypeError, Exception):
        return str(val)


def fmt_force(val: Any, precision: int = 2) -> str:
    """Format force value to kN string."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return "-"
    try:
        f_val = float(val)
        return f"{f_val:,.{precision}f} kN"
    except (ValueError, TypeError, Exception):
        return f"{val} kN"


def fmt_moment(val: Any, precision: int = 2) -> str:
    """Format moment value to kN*m string."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return "-"
    try:
        f_val = float(val)
        return f"{f_val:,.{precision}f} kN·m"
    except (ValueError, TypeError, Exception):
        return f"{val} kN·m"


def fmt_stress(val: Any, precision: int = 2) -> str:
    """Format stress value to MPa string."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return "-"
    try:
        f_val = float(val)
        return f"{f_val:,.{precision}f} MPa"
    except (ValueError, TypeError, Exception):
        return f"{val} MPa"


def fmt_dcr(val: Any, precision: int = 3) -> str:
    """Format Demand-Capacity Ratio (DCR)."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return "-"
    try:
        f_val = float(val)
        return f"{f_val:.{precision}f}"
    except (ValueError, TypeError, Exception):
        return str(val)


def dcr_badge(val: Any, limit: float = 1.0) -> str:
    """Generate HTML badge for DCR status (OK / NG / WARNING)."""
    if val is None or hasattr(val, '_undefined_name') or str(type(val)).find('Undefined') != -1:
        return '<span class="badge badge-na">N/A</span>'
    try:
        dcr = float(val)
        if dcr <= 0.0:
            return '<span class="badge badge-pass">OK (0.000)</span>'
        elif dcr <= limit:
            return f'<span class="badge badge-pass">OK ({dcr:.3f})</span>'
        elif dcr <= limit * 1.05:
            return f'<span class="badge badge-warn">WARN ({dcr:.3f})</span>'
        else:
            return f'<span class="badge badge-fail">NG ({dcr:.3f})</span>'
    except (ValueError, TypeError, Exception):
        return f'<span class="badge badge-na">{val}</span>'


def katex_inline(formula: str) -> str:
    """Wrap formula with inline math delimiter."""
    return f"${formula}$"


def katex_block(formula: str) -> str:
    """Wrap formula with block math delimiter."""
    return f"$${formula}$$"


class ReportGenerator:
    """Core Structural Calculation Report Generation Engine."""

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(base_dir, "templates")
        
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["fmt_num"] = fmt_num
        self.env.filters["fmt_force"] = fmt_force
        self.env.filters["fmt_moment"] = fmt_moment
        self.env.filters["fmt_stress"] = fmt_stress
        self.env.filters["fmt_dcr"] = fmt_dcr
        self.env.filters["dcr_badge"] = dcr_badge
        self.env.filters["katex_inline"] = katex_inline
        self.env.filters["katex_block"] = katex_block
        self.env.filters["unit_force"] = UnitConverter.format_force
        self.env.filters["unit_moment"] = UnitConverter.format_moment
        self.env.filters["unit_stress"] = UnitConverter.format_stress

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render calculation report HTML from template and context dict."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_with_options(
        self,
        context: Dict[str, Any],
        options: Optional[ReportOptions] = None,
        default_template: str = "base_report.html",
    ) -> str:
        """Render calculation report according to ReportOptions (summary, detail, input_data)."""
        opts = options or ReportOptions()
        ctx = dict(context)
        ctx["options"] = opts

        if opts.report_mode == "summary":
            return self.render("summary_report.html", ctx)
        elif opts.report_mode == "detail":
            return self.render("detail_report.html", ctx)
        elif opts.report_mode == "input_data":
            return self.render("input_data_report.html", ctx)
        return self.render(default_template, ctx)

    def render_summary_report(self, context: Dict[str, Any], options: Optional[ReportOptions] = None) -> str:
        """Render 1-2 page compact summary report."""
        opts = options or ReportOptions(report_mode="summary")
        opts.report_mode = "summary"
        return self.render_with_options(context, opts)

    def render_detail_report(self, context: Dict[str, Any], options: Optional[ReportOptions] = None) -> str:
        """Render detailed audit report with step-by-step formula derivations."""
        opts = options or ReportOptions(report_mode="detail")
        opts.report_mode = "detail"
        return self.render_with_options(context, opts)

    def render_input_data_report(self, context: Dict[str, Any], options: Optional[ReportOptions] = None) -> str:
        """Render user input raw data sheet."""
        opts = options or ReportOptions(report_mode="input_data")
        opts.report_mode = "input_data"
        return self.render_with_options(context, opts)


    def render_generic_report(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        checks: list,
        summary_dcr: float,
        is_safe: bool,
        svg_diagram: Optional[str] = None,
        pm_chart_svg: Optional[str] = None,
    ) -> str:
        """Render a standardized generic A4 calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "checks": checks,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
            "svg_diagram": svg_diagram,
            "pm_chart_svg": pm_chart_svg,
        }
        return self.render("base_report.html", context)

    def render_rc_beam(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        flexure_check: Dict[str, Any],
        shear_check: Dict[str, Any],
        service_check: Optional[Dict[str, Any]] = None,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
        svg_diagram: Optional[str] = None,
    ) -> str:
        """Render detailed RC Beam calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "flexure_check": flexure_check,
            "shear_check": shear_check,
            "service_check": service_check,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
            "svg_diagram": svg_diagram,
        }
        return self.render("rc_beam_report.html", context)

    def render_rc_column(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        pm_check: Dict[str, Any],
        shear_check: Optional[Dict[str, Any]] = None,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
        svg_diagram: Optional[str] = None,
        pm_chart_svg: Optional[str] = None,
    ) -> str:
        """Render detailed RC Column calculation report with P-M diagram."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "pm_check": pm_check,
            "shear_check": shear_check,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
            "svg_diagram": svg_diagram,
            "pm_chart_svg": pm_chart_svg,
        }
        return self.render("rc_column_report.html", context)

    def render_rc_wall_slab(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        checks: list,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
    ) -> str:
        """Render detailed RC Wall & Slab calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "checks": checks,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
        }
        return self.render("rc_wall_slab_report.html", context)

    def render_rc_foundation(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        checks: list,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
    ) -> str:
        """Render detailed RC Foundation & Retaining Wall calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "checks": checks,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
        }
        return self.render("rc_foundation_report.html", context)

    def render_steel_member(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        checks: list,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
        svg_diagram: Optional[str] = None,
    ) -> str:
        """Render detailed Steel Member (Beam/Column/Brace) calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "checks": checks,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
            "svg_diagram": svg_diagram,
        }
        return self.render("steel_member_report.html", context)

    def render_steel_connection(
        self,
        project_info: Dict[str, Any],
        member_info: Dict[str, Any],
        material_info: Dict[str, Any],
        section_info: Dict[str, Any],
        loads_info: Dict[str, Any],
        checks: list,
        summary_dcr: float = 0.0,
        is_safe: bool = True,
    ) -> str:
        """Render detailed Steel Connection / Baseplate calculation report."""
        context = {
            "project": project_info,
            "member": member_info,
            "material": material_info,
            "section": section_info,
            "loads": loads_info,
            "checks": checks,
            "summary_dcr": summary_dcr,
            "is_safe": is_safe,
        }
        return self.render("steel_connection_report.html", context)
