from flask import Blueprint, request, jsonify, redirect, session, current_app
from typing import Dict, Any
from services.azure_service import AzureService
from services.github_service import GitHubService
from utils.validators import validate_code_input
from services.documentation_generator import DocumentationGenerator
from services.translator import TranslatorService
from utils.middleware import RateLimiter, rate_limit, require_auth
import logging


api = Blueprint('api', __name__)
azure_service = AzureService()
github = GitHubService(validate_on_init=False)
doc_generator = DocumentationGenerator()
translator = TranslatorService()
rate_limiter = RateLimiter(requests_per_minute=60)

@api.route('/analyze', methods=['POST'])
@rate_limit(rate_limiter)
def analyze():
    """Analyze code using free sentiment analysis (TextBlob/NLTK VADER)."""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    try:
        data = request.get_json()
        if not validate_code_input(data):
            return jsonify({
                'error': 'Invalid input format',
                'required_fields': ['code', 'language']
            }), 400
            
        code = data.get('code')
        language = data.get('language')
        
        analysis_result = azure_service.analyze_sentiment(code, language)
        
        if 'error' in analysis_result:
            return jsonify({
                'status': 'error',
                'error': analysis_result['error']
            }), 500
            
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api.route('/analyze/documentation', methods=['POST'])
@rate_limit(rate_limiter)
def documentation():
    """Generate documentation for code"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    try:
        data = request.get_json()
        if not validate_code_input(data):
            return jsonify({
                'error': 'Invalid input format',
                'required_fields': ['code', 'language']
            }), 400

        result = doc_generator.generate(data['code'], data['language'])
        return jsonify({
            'status': 'success',
            'documentation': result.__dict__ if hasattr(result, '__dict__') else result
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

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


@api.route('/translate', methods=['POST'])
@rate_limit(rate_limiter)
def translate():
    """Translate text to target language with improved validation and response handling"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    text = data.get('text')
    target_language = data.get('target_language')

    # Enhanced input validation
    if not text or not isinstance(text, str):
        return jsonify({'error': 'Invalid or missing text field'}), 400
    if not target_language or not isinstance(target_language, str):
        return jsonify({'error': 'Invalid or missing target_language field'}), 400
    
    try:
        translation_result = translator.translate(text, target_language)
        
        if 'error' in translation_result:
            return jsonify({
                'status': 'error',
                'error': translation_result['error']
            }), 500

        return jsonify({
            'status': 'success',
            'translated_text': translation_result['translated_text'],
            'detected_language': translation_result['detected_language'],
            'confidence': translation_result['confidence'],
            'metrics': {
                'input_length': len(text),
                'translation_length': len(translation_result['translated_text'])
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Translation service error occurred'
        }), 500

@api.route('/translate/batch', methods=['POST'])
@rate_limit(rate_limiter)
def batch_translate():
    """Batch translate multiple texts"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    texts = data.get('texts', [])
    target_language = data.get('target_language')

    if not texts or not isinstance(texts, list):
        return jsonify({'error': 'Invalid or missing texts field'}), 400
    if not target_language or not isinstance(target_language, str):
        return jsonify({'error': 'Invalid or missing target_language field'}), 400

    try:
        translations = translator.batch_translate(texts, target_language)
        return jsonify({
            'status': 'success',
            'translations': translations
        }), 200
    except Exception as e:
        logging.error(f"Batch translation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Translation service error occurred'
        }), 500

@api.route('/translate/terminology', methods=['POST'])
@rate_limit(rate_limiter)
def add_custom_terminology():
    """Add custom terminology for translation"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')
    terms = data.get('terms', {})

    if not all([source_lang, target_lang, terms]):
        return jsonify({'error': 'Missing required fields'}), 400
    if not isinstance(terms, dict):
        return jsonify({'error': 'Terms must be a dictionary'}), 400

    try:
        translator.add_custom_terminology(source_lang, target_lang, terms)
        return jsonify({
            'status': 'success',
            'message': 'Custom terminology added'
        }), 200
    except Exception as e:
        logging.error(f"Failed to add custom terminology: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api.route('/github/<owner>/<repo>', methods=['GET'])
@rate_limit(rate_limiter)
def github_info(owner, repo):
    try:
        if not github.token:
            return jsonify({'error': 'GitHub token not configured'}), 401
        result = github.get_repository_info(owner, repo)
        if 'error' in result:
            return jsonify(result), 401 if 'credentials' in result.get('error', '') else 500
        return jsonify({"repo": f"{owner}/{repo}", "info": result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/github/<owner>/<repo>/analyze', methods=['GET'])
@rate_limit(rate_limiter)
def analyze_repository(owner: str, repo: str):
    """Get detailed repository analysis"""
    try:
        analysis = github.analyze_repository(owner, repo)
        if 'error' in analysis:
            return jsonify(analysis), 500
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/github/batch', methods=['POST'])
@rate_limit(rate_limiter)
@require_auth
def batch_analyze_repositories():
    """Batch process multiple repositories"""
    try:
        data = request.get_json()
        if not data or 'repositories' not in data:
            return jsonify({'error': 'repositories list is required'}), 400
            
        results = github.batch_process_repositories(data['repositories'])
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/github')
def github_auth():
    redirect_uri = request.args.get('redirect_uri', 'http://127.0.0.1:3000/auth/callback')
    auth_url = github.get_oauth_url(redirect_uri)
    return jsonify({'auth_url': auth_url})

@api.route('/auth/callback')
def github_callback():
    code = request.args.get('code')
    redirect_uri = request.args.get('redirect_uri', 'http://127.0.0.1:3000/auth/callback')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    result = github.exchange_code_for_token(code, redirect_uri)
    if 'error' in result:
        return jsonify(result), 500
    if 'access_token' in result:
        return jsonify({'token': result['access_token']})
    return jsonify({'error': 'Failed to get token'}), 400

@api.route('/scan', methods=['POST'])
@rate_limit(rate_limiter)
def scan_repository():
    try:
        data = request.get_json()
        if not data or 'repo_path' not in data:
            return jsonify({'error': 'repo_path is required'}), 400
        
        repo_path = data['repo_path']
        files = github.scan_repository(repo_path)
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
def export_documentation_markdown():  # Changed function name from export_markdown to export_documentation_markdown
    try:
        data = request.get_json()
        if not all(k in data for k in ['code', 'language', 'output_path']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        doc = doc_generator.generate(data['code'], data['language'])
        doc_generator.export_to_markdown(doc, data['output_path'])
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500