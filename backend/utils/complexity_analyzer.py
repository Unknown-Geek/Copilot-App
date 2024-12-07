
import ast
import math
from typing import Dict, Any

class ComplexityAnalyzer:
    def analyze_python(self, code: str) -> Dict[str, Any]:
        tree = ast.parse(code)
        analyzer = self._PythonComplexityVisitor()
        analyzer.visit(tree)
        
        return {
            'cyclomatic_complexity': analyzer.complexity,
            'maintainability_index': self._calculate_maintainability(code, analyzer.complexity),
            'code_to_comment_ratio': self._calculate_comment_ratio(code)
        }

    def _calculate_maintainability(self, code: str, complexity: int) -> float:
        lines = len(code.splitlines())
        volume = len(code) * math.log2(len(set(code)))
        maintainability = max(0, (171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(lines)) * 100 / 171)
        return round(maintainability, 2)

    def _calculate_comment_ratio(self, code: str) -> float:
        lines = code.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        total_lines = len(lines)
        return round(comment_lines / total_lines if total_lines > 0 else 0, 2)

    class _PythonComplexityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.complexity = 1

        def visit_If(self, node): 
            self.complexity += 1
            self.generic_visit(node)

        def visit_For(self, node):
            self.complexity += 1
            self.generic_visit(node)

        def visit_While(self, node):
            self.complexity += 1
            self.generic_visit(node)

        def visit_ExceptHandler(self, node):
            self.complexity += 1
            self.generic_visit(node)