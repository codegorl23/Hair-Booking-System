from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging


logger = logging.getLogger(__name__)

def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({'error': str(e)}), 409

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f'Internal server error: {e}', exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({'error': e.description}), e.code
        logger.error(f'Unhandled exception: {e}', exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500