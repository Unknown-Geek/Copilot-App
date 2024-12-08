from flask import jsonify, request, Blueprint
import logging

api = Blueprint('api', __name__)

try:
    from flask_limiter import Limiter
    rate_limiter = Limiter(key_func=lambda: request.remote_addr)
except ImportError:
    # Mock rate limiter if package not available
    class MockLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    rate_limiter = MockLimiter()

# Change relative imports to absolute
from services import DocumentationGenerator
from utils import validate_code_input, rate_limit
from services.github_service import GitHubService
from services.documentation_generator import DocumentationGenerator

@api.route('/analyze/documentation/generate', methods=['POST'])
@rate_limit(rate_limiter)
def generate_documentation():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    try:
        data = request.get_json()
        if not validate_code_input(data):
            return jsonify({
                'error': 'Invalid input format',
                'required_fields': ['code', 'language']
            }), 400

        template = data.get('template', 'default')
        export_format = data.get('format', 'markdown')
        
        doc = doc_generator.generate(
            data['code'], 
            data['language'],
            title=data.get('title'),
            description=data.get('description')
        )
        
        result = doc_generator.export_documentation(
            doc,
            format=export_format,
            template=template
        )
        
        return jsonify({
            'status': 'success',
            'documentation': result,
            'format': export_format,
            'template': template
        })

    except ValueError as e:
        return jsonify({'status': 'error', 'error': str(e)}), 400
    except NotImplementedError as e:
        return jsonify({'status': 'error', 'error': str(e)}), 501
    except Exception as e:
        logging.error(f"Documentation generation failed: {str(e)}")
        return jsonify({'status': 'error', 'error': 'Internal server error'}), 500
    

github_service = GitHubService()
doc_generator = DocumentationGenerator()

@api.route('/scan', methods=['POST'])
@rate_limit(rate_limiter)
def scan_repository():
    try:
        data = request.get_json()
        if not data or 'repo_path' not in data:
            return jsonify({'error': 'repo_path is required'}), 400
        
        repo_path = data['repo_path']
        files = github_service.scan_repository(repo_path)
        return jsonify({'files': files})
    except Exception as e:
        logging.error(f"Repository scan failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/save', methods=['POST'])
@rate_limit(rate_limiter)
def save_documentation():
    try:
        data = request.get_json()
        if not all(k in data for k in ['code', 'language', 'output_path']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        doc = doc_generator.generate(data['code'], data['language'])
        doc_generator.save_documentation(doc, data['output_path'])
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/export/markdown', methods=['POST'])
@rate_limit(rate_limiter)
def export_markdown():
    try:
        data = request.get_json()
        if not all(k in data for k in ['code', 'language', 'output_path']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        doc = doc_generator.generate(data['code'], data['language'])
        doc_generator.export_to_markdown(doc, data['output_path'])
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500