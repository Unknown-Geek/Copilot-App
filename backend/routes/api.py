from flask import Blueprint, request, jsonify, redirect, session, current_app
from typing import Dict, Any
from services.code_analyzer import CodeAnalyzer
from services.github_service import GitHubService
from utils.validators import validate_code_input
from services.documentation_generator import DocumentationGenerator
from services.translator import TranslatorService  # Changed from TranslationService
from utils.middleware import RateLimiter, rate_limit, require_auth

api = Blueprint('api', __name__)
analyzer = CodeAnalyzer()  # Only creates instance, doesn't initialize yet
github = GitHubService(validate_on_init=False)  # Initialize without validation
doc_generator = DocumentationGenerator()
translator = TranslatorService()  # Changed from TranslationService
rate_limiter = RateLimiter(requests_per_minute=60)

@api.route('/analyze', methods=['POST'])
@rate_limit(rate_limiter)
def analyze():
    """Analyze code using Azure Text Analytics and return sentiment analysis."""
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
        
        analysis_result = analyzer.analyze_code(code, language)
        
        if isinstance(analysis_result, dict) and 'error' in analysis_result:
            return jsonify({
                'status': 'error',
                'error': analysis_result['error']
            }), 500
            
        formatted_result = {
            'status': 'success',
            'analysis': {
                'sentiment': analysis_result.get('sentiment'),
                'confidence': analysis_result.get('confidence_scores', {}),
                'details': [
                    {
                        'text': sent.get('text'),
                        'sentiment': sent.get('sentiment'),
                        'confidence': sent.get('confidence_scores', {})
                    }
                    for sent in analysis_result.get('sentences', [])
                ]
            }
        }
        
        return jsonify(formatted_result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api.route('/analyze/documentation', methods=['POST'])
def documentation():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not validate_code_input(data):
        return jsonify({
            'error': 'Invalid input format',
            'required_fields': ['code', 'language']
        }), 400

    try:
        result = analyzer.analyze_code(data['code'], data['language'])
        if 'error' in result:
            return jsonify(result), 500
        return jsonify({"documentation": result}), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'details': 'Documentation generation failed'
        }), 500

@api.route('/analyze/documentation/generate', methods=['POST'])
@rate_limit(rate_limiter)
def generate_documentation():
    """Generate comprehensive documentation for code"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    try:
        data = request.get_json()
        if not validate_code_input(data):
            return jsonify({
                'error': 'Invalid input format',
                'required_fields': ['code', 'language']
            }), 400

        documentation = doc_generator.generate(data['code'], data['language'])
        return jsonify({
            'status': 'success',
            'documentation': documentation.__dict__
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api.route('/translate', methods=['POST'])
def translate():
    """Translate text to target language"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    try:
        data = request.get_json()
        if not all(k in data for k in ['text', 'target_language']):
            return jsonify({
                'error': 'Invalid input format',
                'required_fields': ['text', 'target_language']
            }), 400

        result = translator.translate(
            data['text'],
            data['target_language'],
            data.get('source_language')
        )
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify({
            'status': 'success',
            'translation': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api.route('/github/<owner>/<repo>', methods=['GET'])
@rate_limit(rate_limiter)
@require_auth
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