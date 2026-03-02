"""
BrandKin AI - Local Development Server
Flask server for local testing without Function Compute
"""

import os
import sys

# Set environment variables BEFORE importing any modules
# Choose AI provider: 'mock' or 'modelstudio'
os.environ['AI_PROVIDER'] = os.getenv('AI_PROVIDER', 'modelstudio')  # Using Model Studio with your API key

# Model Studio (Alibaba Cloud International) - Primary AI provider
os.environ['MODELSTUDIO_API_KEY'] = os.getenv('MODELSTUDIO_API_KEY', 'sk-6a088b68d8ef46c180cbc84fd987aba9')
os.environ['OSS_BUCKET'] = os.getenv('OSS_BUCKET', 'brandkin-ai-assets-local')
os.environ['OSS_ENDPOINT'] = os.getenv('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
os.environ['OSS_REGION'] = os.getenv('OSS_REGION', 'cn-hangzhou')

# MySQL Database Configuration for Local phpMyAdmin
os.environ['RDS_HOST'] = os.getenv('RDS_HOST', 'localhost')
os.environ['RDS_PORT'] = os.getenv('RDS_PORT', '3306')
os.environ['RDS_DATABASE'] = os.getenv('RDS_DATABASE', 'brandkin_ai_local')
os.environ['RDS_USER'] = os.getenv('RDS_USER', 'root')
os.environ['RDS_PASSWORD'] = os.getenv('RDS_PASSWORD', '')  # Default phpMyAdmin has no password
os.environ['USE_MOCK_DB'] = os.getenv('USE_MOCK_DB', 'false')  # Use real MySQL by default

# Alibaba Cloud credentials (not needed for local dev)
os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID', 'local-access-key')
os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET', 'local-secret')
os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'] = os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN', 'local-token')

import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Add fc-functions to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fc-functions'))

# Import stage handlers
from stage_handlers import (
    stage0_init,
    stage1_dna,
    stage2_visual,
    stage3_selection,
    stage4_poses,
    stage5_code,
    stage6_revision,
    stage7_assembly
)
from orchestrator import api_handler

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001'])


@app.route('/api/v1/projects', methods=['POST', 'OPTIONS'])
def create_project():
    """Stage 0: Create new project"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'POST',
        'path': '/api/v1/projects',
        'body': request.get_json()
    }
    result = stage0_init.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/projects/<project_id>', methods=['GET', 'OPTIONS'])
def get_project(project_id):
    """Get project status"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'GET',
        'path': f'/api/v1/projects/{project_id}',
        'pathParameters': {'id': project_id}
    }
    result = api_handler.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/projects/<project_id>/assets', methods=['GET', 'OPTIONS'])
def get_assets(project_id):
    """Get project assets"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'GET',
        'path': f'/api/v1/projects/{project_id}/assets',
        'pathParameters': {'id': project_id}
    }
    result = api_handler.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/projects/<project_id>/select', methods=['POST', 'OPTIONS'])
def select_character(project_id):
    """Stage 3: Select character"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'POST',
        'path': f'/api/v1/projects/{project_id}/select',
        'pathParameters': {'id': project_id},
        'body': request.get_json()
    }
    result = stage3_selection.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/projects/<project_id>/revise', methods=['POST', 'OPTIONS'])
def request_revision(project_id):
    """Stage 6: Request revision"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'POST',
        'path': f'/api/v1/projects/{project_id}/revise',
        'pathParameters': {'id': project_id},
        'body': request.get_json()
    }
    result = stage6_revision.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/projects/<project_id>/finalize', methods=['POST', 'OPTIONS'])
def finalize_project(project_id):
    """Stage 7: Finalize brand kit"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'POST',
        'path': f'/api/v1/projects/{project_id}/finalize',
        'pathParameters': {'id': project_id},
        'body': request.get_json()
    }
    result = stage7_assembly.handler(event, None)
    
    # Save ZIP file to local storage for download
    import os
    result_body = json.loads(result['body'])
    if result['statusCode'] == 200 and 'zip_data' in result_body:
        local_storage = os.path.join(os.path.dirname(__file__), 'local_storage')
        os.makedirs(local_storage, exist_ok=True)
        zip_path = os.path.join(local_storage, f"brandkit_{project_id}.zip")
        import base64
        zip_data = base64.b64decode(result_body['zip_data'])
        with open(zip_path, 'wb') as f:
            f.write(zip_data)
        print(f"Saved brand kit to {zip_path}")
    
    return jsonify(result_body), result['statusCode']


@app.route('/api/v1/projects/<project_id>/code', methods=['GET', 'OPTIONS'])
def get_code_exports(project_id):
    """Get code exports"""
    if request.method == 'OPTIONS':
        return '', 200
    
    event = {
        'httpMethod': 'GET',
        'path': f'/api/v1/projects/{project_id}/code',
        'pathParameters': {'id': project_id}
    }
    result = api_handler.handler(event, None)
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/v1/download/<project_id>', methods=['GET'])
def download_brand_kit(project_id):
    """Download brand kit ZIP file (for mock mode local files)"""
    import os
    local_storage = os.path.join(os.path.dirname(__file__), 'local_storage')
    zip_path = os.path.join(local_storage, f"brandkit_{project_id}.zip")
    
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f"brandkit_{project_id}.zip")
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'BrandKin AI Local Server'})


if __name__ == '__main__':
    print("=" * 60)
    print("BrandKin AI - Local Development Server")
    print("=" * 60)
    print("API Base URL: http://localhost:5000")
    print("Frontend should connect to: http://localhost:5000")
    print("=" * 60)
    
    # Note: For full functionality, you need:
    # 1. Valid DashScope API key
    # 2. OSS bucket configured
    # 3. RDS MySQL database running
    
    app.run(host='0.0.0.0', port=5000, debug=True)
