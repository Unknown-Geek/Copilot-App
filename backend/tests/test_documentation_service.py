import unittest
from unittest.mock import patch, Mock
import tempfile
import json
import os
from services.documentation_generator import DocumentationGenerator

class TestDocumentationFeatures(unittest.TestCase):
    def setUp(self):
        self.generator = DocumentationGenerator()
        self.test_code = {
            'python': """
                def hello():
                    '''Test function docstring'''
                    print("Hello")
                    
                class TestClass:
                    '''Test class docstring'''
                    def method(self):
                        # Method comment
                        return True
            """,
            'javascript': """
                function hello() {
                    // Test function
                    console.log("Hello");
                }
                
                class TestClass {
                    // Test class
                    constructor() {
                        this.value = true;
                    }
                }
            """,
            'java': """
                public class TestClass {
                    /**
                     * Test method documentation
                     */
                    public void hello() {
                        // Test function
                        System.out.println("Hello");
                    }
                }
            """
        }

    def test_all_features(self):
        """Test all documentation features together"""
        # 1. Test Multi-Language Support
        for lang, code in self.test_code.items():
            doc = self.generator.generate(code, lang)
            self.assertEqual(doc.language, lang)
            self.assertGreater(len(doc.code_blocks), 0)

        # 2. Test Template System
        python_doc = self.generator.generate(self.test_code['python'], 'python')
        
        # Default template
        default_output = self.generator.export_documentation(python_doc, template='default')
        self.assertIn('# Python Documentation', default_output)
        self.assertIn('```python', default_output)
        
        # Detailed template
        detailed_output = self.generator.export_documentation(python_doc, template='detailed')
        self.assertIn('## Table of Contents', detailed_output)
        self.assertIn('## Code Blocks', detailed_output)
        self.assertIn('## Project Metrics', detailed_output)

        # 3. Test Export Formats
        # HTML Export
        html_output = self.generator.export_documentation(python_doc, format='html')
        self.assertIn('<!DOCTYPE html>', html_output)
        self.assertIn('<div class="code-block">', html_output)
        self.assertIn('<pre><code>', html_output)

        # JSON Export
        json_output = self.generator.export_documentation(python_doc, format='json')
        json_data = json.loads(json_output)
        self.assertEqual(json_data['language'], 'python')
        self.assertIn('code_blocks', json_data)
        self.assertIn('metrics', json_data)

        # 4. Test Export Options
        # File export
        with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as tf:
            self.generator.export_documentation(python_doc, output_path=tf.name)
            with open(tf.name, 'r') as f:
                content = f.read()
            self.assertIn('# Python Documentation', content)

        # 5. Test Metrics Generation
        self.assertIsNotNone(python_doc.metrics)
        self.assertIn('total_blocks', python_doc.metrics)
        self.assertIn('total_lines', python_doc.metrics)
        self.assertIn('average_complexity', python_doc.metrics)

        # 6. Test GitHub Integration
        with patch('services.github_service.GitHubService') as mock_github:
            mock_github.return_value.get_repository_info.return_value = {
                'name': 'test-repo',
                'description': 'Test repository'
            }
            github_doc = self.generator.export_documentation(
                python_doc,
                format='markdown',
                template='default'
            )
            self.assertIn('# Python Documentation', github_doc)
            self.assertIn('```python', github_doc)

    def test_all_export_formats(self):
        """Test all supported export formats"""
        doc = self.generator.generate(self.test_code['python'], 'python')
        formats = {
            'markdown': '.md',
            'html': '.html',
            'json': '.json',
            'pdf': '.pdf',
            'docx': '.docx'
        }
        
        for format_name, extension in formats.items():
            output_file = f'test_output{extension}'
            try:
                content = self.generator.export_documentation(doc, format=format_name, output_path=output_file)
                self.assertTrue(os.path.exists(output_file))
                if format_name in ['pdf', 'docx']:
                    self.assertIsInstance(content, bytes)
                else:
                    self.assertIsInstance(content, str)
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)

    def test_error_handling(self):
        """Test error handling across features"""
        # Test invalid language
        with self.assertRaises(ValueError):
            self.generator.generate("code", "invalid_lang")

        # Test invalid template
        doc = self.generator.generate(self.test_code['python'], 'python')
        with self.assertRaises(ValueError):
            self.generator.export_documentation(doc, template='invalid_template')

        # Test invalid format
        with self.assertRaises(ValueError):
            self.generator.export_documentation(doc, format='invalid_format')

        # Test empty code
        with self.assertRaises(ValueError):
            self.generator.generate("", "python")

    def test_pdf_export(self):
        """Test PDF export functionality"""
        doc = self.generator.generate(self.test_code['python'], 'python')
        output_file = 'test_output.pdf'
        
        try:
            content = self.generator.export_documentation(doc, format='pdf', output_path=output_file)
            self.assertIsInstance(content, bytes)
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 0)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_docx_export(self):
        """Test DOCX export functionality"""
        doc = self.generator.generate(self.test_code['python'], 'python')
        output_file = 'test_output.docx'
        
        try:
            content = self.generator.export_documentation(doc, format='docx', output_path=output_file)
            self.assertTrue(os.path.exists(output_file))
            self.assertIsInstance(content, bytes)  # DOCX should be bytes
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.remove(output_file)

if __name__ == '__main__':
    unittest.main()