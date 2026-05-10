from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.appointment_service import create_appointment, get_all_appointments, get_appointment_by_id, update_appointment_status, get_client_appointments, get_appointment_by_id_for_client
from app.utils.auth import require_role

# Access Control:
# POST   /appointments          - Auth required - Clients only
# GET    /appointments          - Auth required - Stylist (full history) or Client (upcoming only)
# GET    /appointments/<id>     - Auth required - Stylist (any) or Client (own upcoming only)
# PATCH  /appointments/<id>     - Auth required - Stylist or Client who owns it

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
@require_role('client')
def post_appointment():
    data = request.get_json()

    # Validate body exists
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Validate required fields are present
    required_fields = ['client_id', 'service_id', 'start_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

          # Validate types
    if not isinstance(data['client_id'], int):
        return jsonify({'error': 'client_id must be an integer'}), 400

    if not isinstance(data['service_id'], int):
        return jsonify({'error': 'service_id must be an integer'}), 400

    # Call the service layer
    appointment, error, status_code = create_appointment(
        client_id=data['client_id'],
        service_id=data['service_id'],
        start_time_str=data['start_time']
    )


    if error:
        return jsonify({'error': error}), status_code

    return jsonify(appointment.to_dict()), status_code



@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    claims = get_jwt()
    current_user_id = get_jwt_identity()

    if claims['role'] == 'stylist':
        appointments = get_all_appointments()
    else:
        appointments = get_client_appointments(current_user_id)

    return jsonify([a.to_dict() for a in appointments]), 200

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    claims = get_jwt()
    current_user_id = get_jwt_identity()

    if claims['role'] == 'stylist':
        appointment, error, status_code = get_appointment_by_id(appointment_id)
    else:
        appointment, error, status_code = get_appointment_by_id_for_client(appointment_id, current_user_id)

    if error:
        return jsonify({'error': error}), status_code
    
    return jsonify(appointment.to_dict()), status_code


@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PATCH'])
@jwt_required()
def patch_appointment(appointment_id):
    claims = get_jwt()
    current_user_id = get_jwt_identity()

    data = request.get_json()

    # Validate body exists
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Validate status field is present
    if 'status' not in data:
        return jsonify({'error': 'status is required'}), 400

    appointment, error, status_code = get_appointment_by_id(appointment_id)

    if error:
        return jsonify({'error': error}), status_code

    if claims['role'] == 'client' and str(appointment.client_id) != current_user_id:
        return jsonify({'error': 'Access forbidden'}), 403

    appointment, error, status_code = update_appointment_status(
        appointment_id=appointment_id,
        status=data['status']
    )

    if error:
        return jsonify({'error': error}), status_code

    return jsonify(appointment.to_dict()), status_code


