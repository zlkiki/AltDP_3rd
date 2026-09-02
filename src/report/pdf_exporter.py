"""PDF Structural Calculation Report Exporter for AltDP_3rd.

Converts generated A4 HTML calculation reports into standard PDF documents.
Supports WeasyPrint integration and headless print-ready HTML generation.
"""

from typing import Optional


class PDFReportExporter:
    """PDF Document Generator for Structural Calculation Reports."""

    def __init__(self):
        self._weasyprint_available = False
        try:
            import weasyprint  # noqa
            self._weasyprint_available = True
        except (ImportError, OSError):
            self._weasyprint_available = False

    @property
    def is_weasyprint_available(self) -> bool:
        """Check if native WeasyPrint PDF renderer is available in system."""
        return self._weasyprint_available

    def export_pdf_bytes(self, html_content: str, base_url: Optional[str] = None) -> bytes:
        """Convert HTML string into PDF byte buffer.
        
        If WeasyPrint is available, renders direct PDF binary.
        Otherwise, returns UTF-8 encoded print-optimized HTML buffer.
        """
        if self._weasyprint_available:
            import weasyprint
            doc = weasyprint.HTML(string=html_content, base_url=base_url)
            return doc.write_pdf()
        else:
            # Fallback to UTF-8 encoded HTML stream ready for browser PDF printing
            return html_content.encode("utf-8")
