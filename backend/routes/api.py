from flask import Blueprint, request, jsonify, redirect, session, current_app
from typing import Dict, Any
from services.azure_service import AzureService
from services.github_service import GitHubService
from utils.validators import validate_code_input
from services.documentation_generator import DocumentationGenerator
from services.translator import TranslatorService
from utils.middleware import RateLimiter, rate_limit, require_auth

api = Blueprint('api', __name__)
azure_service = AzureService()
github = GitHubService(validate_on_init=False)
doc_generator = DocumentationGenerator()
translator = TranslatorService()
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