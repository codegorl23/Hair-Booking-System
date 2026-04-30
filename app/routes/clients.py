from flask import Blueprint, jsonify, request
from app.services.client_service import create_client

clients_bp = Blueprint('clients', __name__)

# Access Control:
# POST /clients   - No auth required - Public (registration)

@clients_bp.route('/clients', methods=['POST'])
def post_client():
    data = request.get_json()

    # Validate body exists
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Validate required fields are present
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Call the service layer
    client, error, status_code = create_client(
        name=data['name'],
        email=data['email']
    )

    if error:
        return jsonify({'error': error}), status_code

    return jsonify(client.to_dict()), status_code
