import sys
sys.path.insert(0, '.')
from services.documentation_generator import DocumentationGenerator

sample_code = """
def calculate_fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number recursively.\"\"\"
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

class Calculator:
    \"\"\"A simple calculator class with basic operations.\"\"\"
    
    def add(self, a: float, b: float) -> float:
        \"\"\"Add two numbers together.\"\"\"
        return a + b
    
    def multiply(self, a: float, b: float) -> float:
        \"\"\"Multiply two numbers together.\"\"\"
        return a * b
"""

generator = DocumentationGenerator()
doc = generator.generate(sample_code, 'python')

print('=' * 60)
print('DOCUMENTATION GENERATOR OUTPUT')
print('=' * 60)
print(f'Title: {doc.title}')
print(f'Language: {doc.language}')
print(f'Code Blocks Found: {len(doc.code_blocks)}')
print(f'Metrics: {doc.metrics}')
print()
print('--- MARKDOWN EXPORT ---')
print(generator.export_documentation(doc, 'markdown', 'default'))
print()
print('=' * 60)
print('Advanced Metrics for First Block:')
print('=' * 60)
if doc.code_blocks:
    adv_metrics = generator._calculate_advanced_metrics(doc.code_blocks[0])
    for key, value in adv_metrics.items():
        print(f'  {key}: {value}')
