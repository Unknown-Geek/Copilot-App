import ast
from typing import List, Dict, Any
from models.documentation import Documentation, CodeBlock
import datetime
import re
import logging

class DocumentationGenerator:
    def __init__(self):
        self.supported_languages = {
            'python': self._parse_python,
            'javascript': self._parse_javascript
        }
        logging.basicConfig(level=logging.DEBUG)

    def generate(self, code: str, language: str) -> Documentation:
        """Generate documentation for given code"""
        try:
            logging.info(f"Generating documentation for language: {language}")
            parse_func = self.supported_languages.get(language.lower())
            if not parse_func:
                raise ValueError(f"Unsupported language: {language}")

            blocks = parse_func(code)
            return Documentation(
                title=self._extract_title(blocks),
                description=self._extract_description(blocks),
                code_blocks=blocks,
                generated_at=datetime.datetime.now(datetime.UTC).isoformat(),
                language=language
            )
        except Exception as e:
            logging.error(f"Documentation generation failed: {str(e)}")
            raise ValueError(f"Documentation generation failed: {str(e)}")

    def _parse_python(self, code: str) -> List[CodeBlock]:
        blocks = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    blocks.append(CodeBlock(
                        content=ast.get_source_segment(code, node) or str(node),
                        language='python',
                        line_number=getattr(node, 'lineno', 0)
                    ))
                # Updated for Python 3.14 compatibility
                elif isinstance(node, ast.Expr) and isinstance(node.value, (ast.Constant, ast.Str)):
                    # Handle both old ast.Str and new ast.Constant
                    docstring = (node.value.value 
                               if isinstance(node.value, ast.Constant) 
                               else node.value.s)
                    if isinstance(docstring, str):
                        blocks.append(CodeBlock(
                            content=docstring,
                            language='text',
                            line_number=getattr(node, 'lineno', 0)
                        ))
        except Exception as e:
            raise ValueError(f"Python parsing failed: {str(e)}")
        return blocks

    def _parse_javascript(self, code: str) -> List[CodeBlock]:
        blocks = []
        # Improved regex patterns
        function_pattern = r'(function\s+\w+\s*\([^)]*\)\s*\{[^}]*\})'
        class_pattern = r'(class\s+\w+\s*\{[^}]*\})'
        comment_pattern = r'(//[^\n]*|/\*(?:.|[\r\n])*?\*/)'
        
        # First collect all comments
        for match in re.finditer(comment_pattern, code):
            blocks.append(CodeBlock(
                content=match.group(1),
                language='text',
                line_number=code[:match.start()].count('\n') + 1
            ))
        
        # Then collect functions and classes
        for pattern in [function_pattern, class_pattern]:
            for match in re.finditer(pattern, code):
                blocks.append(CodeBlock(
                    content=match.group(1).strip(),
                    language='javascript',
                    line_number=code[:match.start()].count('\n') + 1
                ))
        
        return blocks

    def _extract_title(self, blocks: List[CodeBlock]) -> str:
        """Extract title from code blocks"""
        for block in blocks:
            if block.language == 'text':
                lines = block.content.split('\n')
                if lines:
                    return lines[0].strip()
        return "Generated Documentation"

    def _extract_description(self, blocks: List[CodeBlock]) -> str:
        """Extract description from code blocks"""
        for block in blocks:
            if block.language == 'text':
                lines = block.content.split('\n')
                if len(lines) > 1:
                    return '\n'.join(line.strip() for line in lines[1:])
        return "No description available"