from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class CodeBlock:
    content: str
    language: str
    line_number: int
    complexity: Optional[float] = None

@dataclass
class DocumentationMetrics:
    complexity: float
    maintainability: float
    code_to_comment_ratio: float
    generated_at: datetime

@dataclass
class Documentation:
    title: str
    description: str
    code_blocks: List[CodeBlock]
    generated_at: str
    language: str
    metrics: Optional[DocumentationMetrics] = None
    translations: Optional[dict] = None