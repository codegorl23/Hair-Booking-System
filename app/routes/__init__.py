from flask import request, jsonify

def validate_request():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    required_fields = ['client_id', 'service_id', 'start_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    if not isinstance(data['client_id'], int):
        return jsonify({'error': 'client_id must be an integer'}), 400

    if not isinstance(data['service_id'], int):
        return jsonify({'error': 'service_id must be an integer'}), 400
    
    return data