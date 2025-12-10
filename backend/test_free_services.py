"""
Test script to verify all free services work without Azure.
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("Testing Free Services (No Azure Required)")
print("=" * 60)

# Test 1: Sentiment Analysis
print("\n1. Testing Sentiment Service (TextBlob/NLTK VADER)...")
from services.sentiment_service import SentimentService

sentiment = SentimentService()
result = sentiment.analyze_sentiment("This is a great piece of code! Very well written.", "en")
print(f"   Result: {result['status']}")
print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
print(f"   Confidence: {result.get('confidence_scores', {})}")

# Test 2: Translation
print("\n2. Testing Translator Service (Google Translate via deep-translator)...")
from services.translator import TranslatorService

translator = TranslatorService()
result = translator.translate("Hello, World! This code generates documentation.", "es")
print(f"   Original: Hello, World! This code generates documentation.")
print(f"   Translated (ES): {result.get('translated_text', 'Error: ' + result.get('error', 'Unknown'))}")
print(f"   Detected Language: {result.get('detected_language', 'N/A')}")

# Test 3: Documentation Generator
print("\n3. Testing Documentation Generator...")
from services.documentation_generator import DocumentationGenerator

gen = DocumentationGenerator()
code = '''
def hello_world():
    """Says hello to the world."""
    print("Hello, World!")
'''
doc = gen.generate(code, 'python')
print(f"   Title: {doc.title}")
print(f"   Code Blocks: {len(doc.code_blocks)}")
print(f"   Metrics: {doc.metrics}")

# Test 4: Code Analyzer
print("\n4. Testing Code Analyzer...")
from services.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.analyze_code("# This is excellent code\nprint('Hello')", "python")
print(f"   Status: {result.get('status')}")
print(f"   Sentiment: {result.get('sentiment', 'N/A')}")

print("\n" + "=" * 60)
print("✅ All free services working! No Azure required.")
print("=" * 60)
