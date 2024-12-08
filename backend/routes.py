from flask import jsonify, request
from .services import DocumentationGenerator
from .utils import validate_code_input, rate_limit

# ...existing imports and setup...

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