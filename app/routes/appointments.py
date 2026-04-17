from flask import Blueprint, jsonify, request
from app.services.appointment_service import create_appointment, get_all_appointments, get_appointment_by_id

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments', methods=['POST'])
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
def get_appointments():
    appointments = get_all_appointments()
    return jsonify([a.to_dict() for a in appointments]), 200

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment, error, status_code = get_appointment_by_id(appointment_id)

    if error:
        return jsonify({'error': error}), status_code

    return jsonify(appointment.to_dict()), status_code


