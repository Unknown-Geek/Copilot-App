# test_documentation_generator.py

import unittest
from datetime import datetime
from unittest.mock import patch
import tempfile
import os
from services.documentation_generator import DocumentationGenerator, Documentation

class TestDocumentationGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = DocumentationGenerator()
        self.test_code = """
def hello_world():
    '''Says hello to the world'''
    print("Hello World!")
class TestClass:
    def test_method(self):
        '''Test method docstring'''
        pass
"""
    def test_empty_code(self):
        with self.assertRaises(ValueError):
            self.generator.generate("", "python")

    def test_unsupported_language(self):
        with self.assertRaises(ValueError):
            self.generator.generate(self.test_code, "unknown")

    def test_successful_generation(self):
        doc = self.generator.generate(self.test_code, "python")
        
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, "python")
        self.assertEqual(doc.title, "Python Documentation")
        self.assertTrue(len(doc.code_blocks) > 0)
        self.assertIsNotNone(doc.generated_at)

    def test_different_code_structures(self):
        test_codes = {
            'python': 'def test(): pass',
            'javascript': 'function test() {}',
            'java': 'public class Test { void test() {} }',
            'cpp': 'void test() {}',
            'csharp': 'public void Test() {}'
        }
        
        for lang, code in test_codes.items():
            with self.subTest(language=lang):
                doc = self.generator.generate(code, lang)
                self.assertEqual(doc.language, lang)
                self.assertTrue(len(doc.code_blocks) > 0)

    def test_error_handling(self):
        with self.assertRaises(ValueError):
            self.generator.generate(None, "python")

    def test_save_documentation(self):
        doc_generator = DocumentationGenerator()
        doc = Documentation(
            title="Test Doc",
            description="Test description",
            code_blocks=[],
            language="python",
            generated_at=datetime.now().isoformat()
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'doc.txt')
            doc_generator.save_documentation(doc, output_path)
            
            assert os.path.exists(output_path)
            with open(output_path, 'r') as file:
                content = file.read()
                assert "Test Doc" in content

    def test_export_to_markdown(self):
        doc_generator = DocumentationGenerator()
        doc = Documentation(
            title="Test Doc",
            description="Test description",
            code_blocks=[],
            language="python",
            generated_at=datetime.now().isoformat()
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'doc.md')
            doc_generator.export_to_markdown(doc, output_path)

    def test_advanced_metrics(self):
        """Test advanced metrics calculation"""
        doc = self.generator.generate(self.test_code, "python")
        for block in doc.code_blocks:
            metrics = self.generator._calculate_advanced_metrics(block)
            # Basic metrics should always be present
            self.assertIn('loc', metrics)
            self.assertIn('sloc', metrics)
            self.assertIn('comments', metrics)
            self.assertIn('complexity', metrics)
            self.assertIn('token_count', metrics)
            self.assertIn('char_count', metrics)
            
            # Advanced metrics may be present if radon is available
            if self.generator.RADON_AVAILABLE:
                self.assertIn('cognitive_complexity', metrics)
                self.assertIn('maintainability_index', metrics)
                self.assertIn('halstead_metrics', metrics)

    def test_language_specific_parsing(self):
        """Test language-specific parsing features"""
        test_codes = {
            'python': ('def test(): pass', ['function']),
            'javascript': ('function test() {}', ['function']),
            'java': ('public class Test { void test() {} }', ['class', 'method']),
        }
        
        for lang, (code, expected_types) in test_codes.items():
            doc = self.generator.generate(code, lang)
            self.assertTrue(len(doc.code_blocks) > 0)
            self.assertEqual(doc.language, lang)

if __name__ == '__main__':
    unittest.main()