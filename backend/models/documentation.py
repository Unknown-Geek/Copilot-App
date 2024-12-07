
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CodeBlock:
    content: str
    language: str
    line_number: int

@dataclass
class Documentation:
    title: str
    description: str
    code_blocks: List[CodeBlock]
    generated_at: str
    language: str
    analysis: Optional[dict] = None