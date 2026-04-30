from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
import logging
import json
from datetime import datetime
import os

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'P@$$w0rd12345'
jwt = JWTManager(app)

logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

users = {
    "admin": {"password": "password123", "role": "admin"},
    "user": {"password": "password123", "role": "user"}
}

projects = [
    {"id": 1, "name": "Project One", "description": "First project"},
    {"id": 2, "name": "Project Two", "description": "Second project"}
]

# Log incoming requests, IPs, timestamps, and errors
@app.after_request
def log_request(response):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "status": response.status_code
    }
    logger.info(json.dumps(log_entry))
    return response

# Logging endpoint to retrieve last 20 logs
@app.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        with open('api.log', 'r') as f:
            logs = f.readlines()
        return jsonify(logs[-20:]), 200 
    except FileNotFoundError:
        return jsonify([]), 200

# Token-based authentication (JWT)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users.get(username)
    if user and user['password'] == password:
        token = create_access_token(identity=username, additional_claims={"role": user['role']})
        return jsonify(access_token=token), 200
    
    return jsonify({"msg": "Bad username or password"}), 401

# CRUD operations

@app.route('/projects', methods=['POST'])
@jwt_required() 
def create_project():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    new_data = request.get_json() 
    new_project = {
        "id": len(projects) + 1,
        "name": new_data['name'],
        "description": new_data.get('description', '')
    }
    projects.append(new_project)
    return jsonify(new_project), 201 

@app.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    return jsonify(projects)

@app.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required() 
def update_project(project_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    project = next((p for p in projects if p["id"] == project_id), None)
    
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    new_data = request.get_json()

    project['name'] = new_data.get('name', project['name'])
    project['description'] = new_data.get('description', project['description'])
    
    return jsonify(project), 200

@app.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    global projects
    projects = [p for p in projects if p["id"] != project_id]
    return jsonify({"message": "Project deleted"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context=('cert.pem', 'key.pem'))
    app.after_request(log_request)
