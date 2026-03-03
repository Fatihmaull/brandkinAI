"""
BrandKin AI - Local Development Server
Flask wrapper around the FC handler for local testing.

Usage:
    cd backend/fc-functions
    python local_dev.py

Requires:
    - .env file in backend/ or project root with MODELSTUDIO_API_KEY
    - pip install flask python-dotenv
    - For full functionality: MySQL running locally or RDS access
"""

import os
import sys
import json
import logging

# Load environment variables from .env file
from dotenv import load_dotenv

# Look for .env in backend/ or project root
env_paths = [
    os.path.join(os.path.dirname(__file__), '..', '.env'),
    os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
]
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded env from: {os.path.abspath(env_path)}")
        break

# Verify critical env vars
if not os.environ.get('MODELSTUDIO_API_KEY'):
    print("⚠️  WARNING: MODELSTUDIO_API_KEY not set. AI calls will fail.")
    print("   Create a .env file in backend/ with: MODELSTUDIO_API_KEY=your-key-here")

# Add fc-functions to Python path (mimics FC runtime)
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import the FC handler
from orchestrator.api_handler import handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('local_dev')

app = Flask(__name__)
CORS(app)

# Local storage directory for serving assets without OSS
LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'local_storage')


@app.route('/local-assets/<path:filepath>')
def serve_local_asset(filepath):
    """Serve locally stored assets (fallback when OSS is not available)."""
    return send_from_directory(LOCAL_STORAGE_DIR, filepath)


def flask_to_fc_event(flask_request):
    """Convert Flask request to FC event format."""
    # Get path and extract project ID if present
    path = flask_request.path
    path_params = {}
    
    # Extract {id} from /api/v1/projects/{id}/...
    import re
    match = re.match(r'/api/v1/projects/([^/]+)', path)
    if match:
        path_params['id'] = match.group(1)
    
    # Build FC-compatible event
    event = {
        'httpMethod': flask_request.method,
        'path': path,
        'pathParameters': path_params,
        'queryParameters': dict(flask_request.args),
        'headers': dict(flask_request.headers),
        'body': flask_request.get_data(as_text=True) or '{}'
    }
    
    return event


@app.route('/health', methods=['GET'])
@app.route('/api/v1/projects', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>', methods=['GET', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>/assets', methods=['GET', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>/code', methods=['GET', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>/select', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>/revise', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/projects/<project_id>/finalize', methods=['POST', 'OPTIONS'])
def api_proxy(**kwargs):
    """Route all API requests through the FC handler."""
    try:
        event = flask_to_fc_event(request)
        
        # Call the FC handler
        result = handler(event, None)
        
        status_code = result.get('statusCode', 200)
        headers = result.get('headers', {})
        body = result.get('body', '{}')
        
        # Parse body if it's a string
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Log errors from the handler
        if status_code >= 400:
            logger.warning(f"{request.method} {request.path} -> {status_code}: {body}")
        
        response = jsonify(body)
        response.status_code = status_code
        
        for key, value in headers.items():
            if key.lower() != 'content-type':  # Flask handles this
                response.headers[key] = value
        
        return response
        
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"""
╔══════════════════════════════════════════════╗
║         BrandKin AI - Local Dev Server       ║
╠══════════════════════════════════════════════╣
║  API:  http://localhost:{port}                 ║
║  Health: http://localhost:{port}/health         ║
╚══════════════════════════════════════════════╝
    """)
    
    # Check env status
    env_status = {
        'MODELSTUDIO_API_KEY': '✅ Set' if os.environ.get('MODELSTUDIO_API_KEY') else '❌ Missing',
        'RDS_HOST': '✅ Set' if os.environ.get('RDS_HOST') else '⚠️  Missing (DB calls will fail)',
        'OSS_BUCKET': '✅ Set' if os.environ.get('OSS_BUCKET') else '⚠️  Missing (OSS calls will fail)',
    }
    
    print("Environment:")
    for key, status in env_status.items():
        print(f"  {key}: {status}")
    print()
    
    app.run(host='0.0.0.0', port=port, debug=True)
