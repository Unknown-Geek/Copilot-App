
from flask import Blueprint, request, jsonify
from services.code_analyzer import CodeAnalyzer
from services.github_service import GitHubService
from utils.validators import validate_code_input

api = Blueprint('api', __name__)
analyzer = CodeAnalyzer()
github = GitHubService()

@api.route('/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    if not validate_code_input(data):
        return jsonify({"error": "Invalid input"}), 400
        
    result = analyzer.analyze_code(data['code'], data['language'])
    return jsonify(result)

@api.route('/github/<owner>/<repo>', methods=['GET'])
def get_repo_info(owner, repo):
    result = github.get_repository_info(owner, repo)
    return jsonify(result)