# services/documentation_service.py
from exporters import MarkdownExporter, HTMLExporter, JSONExporter, PDFExporter, DOCXExporter

class DocumentationService:
    def validate_export_format(self, format: str) -> bool:
        valid_formats = ['markdown', 'html', 'json', 'pdf', 'docx']
        return format.lower() in valid_formats
    
    def export_documentation(self, doc, format='markdown', output_path=None):
        if not self.validate_export_format(format):
            raise ValueError(f"Unsupported export format: {format}")
            
        exporters = {
            'markdown': MarkdownExporter(),
            'html': HTMLExporter(),
            'json': JSONExporter(),
            'pdf': PDFExporter(),
            'docx': DOCXExporter()
        }
        
        return exporters[format].export(doc, output_path)