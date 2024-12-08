import unittest
from services.documentation_generator import DocumentationGenerator
from models.documentation import Documentation, CodeBlock

class TestDocumentationService(unittest.TestCase):
    def setUp(self):
        self.doc_service = DocumentationGenerator()

    def test_generate_python_documentation(self):
        test_code = '''"""
This is a test function
"""
def test():
    pass'''
        result = self.doc_service.generate(test_code.strip(), 'python')
        self.assertIsInstance(result, Documentation)
        self.assertEqual(result.language, 'python')
        self.assertTrue(len(result.code_blocks) > 0)

    def test_generate_javascript_documentation(self):
        test_code = '''// This is a test function
function test() {
    // Do nothing
}'''  # Note: removed extra indentation
        
        result = self.doc_service.generate(test_code, 'javascript')
        self.assertIsInstance(result, Documentation)
        self.assertEqual(result.language, 'javascript')
        # Check if any block contains the function definition
        self.assertTrue(any('function test()' in block.content for block in result.code_blocks))

    def test_unsupported_language(self):
        with self.assertRaises(ValueError):
            self.doc_service.generate("code", "unsupported_lang")

if __name__ == '__main__':
    unittest.main()