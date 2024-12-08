import unittest
import sys
import os
from pathlib import Path

# Ensure backend directory is in Python path
backend_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_dir)  # Insert at beginning of path to take precedence

from services.documentation_generator import DocumentationGenerator, Documentation, CodeBlock

class TestDocumentationGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = DocumentationGenerator()
        self.sample_code_python = """
        def hello_world():
            print("Hello, world!")
            
        class Calculator:
            def add(self, a, b):
                return a + b
        """
        
        self.sample_code_javascript = """
        function helloWorld() {
            console.log("Hello, world!");
        }
        
        class Calculator {
            add(a, b) {
                return a + b;
            }
        }
        """
        
        self.sample_code_java = """
        public class HelloWorld {
            public static void main(String[] args) {
                System.out.println("Hello, world!");
            }
            
            public int add(int a, int b) {
                return a + b;
            }
        }
        """
        
        self.sample_code_cpp = """
        #include <iostream>
        using namespace std;

        int main() {
            cout << "Hello, world!" << endl;
            return 0;
        }
        
        class Calculator {
        public:
            int add(int a, int b) {
                return a + b;
            }
        };
        """
        
        self.sample_code_csharp = """
        using System;

        class HelloWorld {
            static void Main() {
                Console.WriteLine("Hello, world!");
            }
            
            public int Add(int a, int b) {
                return a + b;
            }
        }
        """

    def test_generate_documentation_python(self):
        doc = self.generator.generate(self.sample_code_python, 'python', title="Python Test", description="Test description")
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, 'python')
        self.assertEqual(len(doc.code_blocks), 3)  # Updated to expect 3 blocks
        self.assertEqual(doc.title, "Python Test")
        self.assertEqual(doc.description, "Test description")
        self.assertTrue(any('hello_world' in block.content for block in doc.code_blocks))
        self.assertTrue(any('Calculator' in block.content for block in doc.code_blocks))

    def test_generate_documentation_javascript(self):
        doc = self.generator.generate(self.sample_code_javascript, 'javascript')
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, 'javascript')
        self.assertEqual(len(doc.code_blocks), 2)
        self.assertTrue(any('helloWorld' in block.content for block in doc.code_blocks))
        self.assertTrue(any('Calculator' in block.content for block in doc.code_blocks))

    def test_generate_documentation_java(self):
        doc = self.generator.generate(self.sample_code_java, 'java')
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, 'java')
        self.assertGreaterEqual(len(doc.code_blocks), 1)
        self.assertTrue(any('HelloWorld' in block.content for block in doc.code_blocks))

    def test_generate_documentation_cpp(self):
        doc = self.generator.generate(self.sample_code_cpp, 'cpp')
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, 'cpp')
        self.assertGreaterEqual(len(doc.code_blocks), 1)  # Updated to expect at least 1 block
        self.assertTrue(any('Calculator' in block.content for block in doc.code_blocks))

    def test_generate_documentation_csharp(self):
        doc = self.generator.generate(self.sample_code_csharp, 'csharp')
        self.assertIsInstance(doc, Documentation)
        self.assertEqual(doc.language, 'csharp')
        self.assertGreaterEqual(len(doc.code_blocks), 1)
        self.assertTrue(any('HelloWorld' in block.content for block in doc.code_blocks))

    def test_export_formats(self):
        doc = self.generator.generate(self.sample_code_python, 'python', title="Test Doc")
        
        # Test Markdown export
        markdown = self.generator.export_documentation(doc, format='markdown', template='default')
        self.assertIn('# Test Doc', markdown)
        self.assertIn('```python', markdown)
        
        # Updated HTML export test to accommodate raw string template
        html = self.generator.export_documentation(doc, format='html', template='default')
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<head>', html)  # Added additional HTML structure check
        self.assertIn('<body>', html)  # Added additional HTML structure check
        self.assertIn('<div class="documentation">', html)  # Added class check
        self.assertIn('<pre>', html)
        
        # Test JSON export
        json_output = self.generator.export_documentation(doc, format='json', template='default')
        self.assertIn('"language": "python"', json_output)
        self.assertIn('"code_blocks":', json_output)

    def test_metrics_generation(self):
        doc = self.generator.generate(self.sample_code_python, 'python')
        self.assertIsNotNone(doc.metrics)
        self.assertIn('total_blocks', doc.metrics)
        self.assertIn('total_lines', doc.metrics)
        self.assertIn('average_complexity', doc.metrics)
        self.assertGreater(doc.metrics['total_blocks'], 0)
        self.assertGreater(doc.metrics['total_lines'], 0)

    def test_error_handling(self):
        # Test unsupported language
        with self.assertRaises(ValueError):
            self.generator.generate("code", "unsupported_language")
        
        # Test unsupported export format
        doc = self.generator.generate(self.sample_code_python, 'python')
        with self.assertRaises(ValueError):
            self.generator.export_documentation(doc, format='invalid')
        
        # Test unsupported template
        with self.assertRaises(ValueError):
            self.generator.export_documentation(doc, template='invalid')

    def test_empty_code(self):
        doc = self.generator.generate("", 'python')
        self.assertEqual(len(doc.code_blocks), 0)
        self.assertIsNotNone(doc.metrics)
        self.assertEqual(doc.metrics['total_blocks'], 0)

    def test_detailed_template(self):
        doc = self.generator.generate(self.sample_code_python, 'python')
        content = self.generator.export_documentation(doc, format='markdown', template='detailed')
        self.assertIn('## Table of Contents', content)
        self.assertIn('## Code Blocks', content)
        self.assertIn('## Project Metrics', content)
        self.assertIn('_Generated at:', content)

    def test_code_block_line_numbers(self):
        doc = self.generator.generate(self.sample_code_python, 'python')
        for block in doc.code_blocks:
            self.assertIsInstance(block.line_number, int)
            self.assertGreater(block.line_number, 0)

if __name__ == '__main__':
    unittest.main()