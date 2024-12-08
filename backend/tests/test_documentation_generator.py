# test_documentation_generator.py

import unittest
from datetime import datetime
from unittest.mock import patch
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

if __name__ == '__main__':
    unittest.main()