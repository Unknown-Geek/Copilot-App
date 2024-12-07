from flask import Blueprint, request, jsonify, redirect, session
from services.code_analyzer import CodeAnalyzer
from services.github_service import GitHubService
from utils.validators import validate_code_input

api = Blueprint('api', __name__)
analyzer = CodeAnalyzer()
github = GitHubService()

@api.route('/analyze', methods=['POST'])
def analyze_code():
    print(f"Headers: {request.headers}")  # Debug headers
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    print(f"Received data: {data}")  # Debug payload
    
    if not validate_code_input(data):
        return jsonify({
            'error': 'Invalid input format',
            'required_fields': ['code', 'language']
        }), 400
        
    try:
        result = analyzer.analyze_code(data['code'], data['language'])
        print(f"Analysis result: {result}")  # Debug result
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result), 200
    except Exception as e:
        print(f"Error during analysis: {str(e)}")  # Debug error
        return jsonify({
            'error': str(e),
            'status': 'error',
            'details': 'Server processing error'
        }), 500

@api.route('/github/<owner>/<repo>', methods=['GET'])
def get_repo_info(owner, repo):
    result = github.get_repository_info(owner, repo)
    return jsonify(result)

@api.route('/auth/github')
def github_auth():
    redirect_uri = request.args.get('redirect_uri', 'http://localhost:3000/auth/callback')
    auth_url = github.get_oauth_url(redirect_uri)
    return jsonify({'auth_url': auth_url})

@api.route('/auth/callback')
def github_callback():
    code = request.args.get('code')
    redirect_uri = request.args.get('redirect_uri', 'http://localhost:3000/auth/callback')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    result = github.exchange_code_for_token(code, redirect_uri)
    if 'access_token' in result:
        return jsonify({'token': result['access_token']})
    return jsonify({'error': 'Failed to get token'}), 400