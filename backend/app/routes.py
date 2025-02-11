import logging

from flask import Blueprint, jsonify, request

from app.services.document_service import DocumentService
from app.utils.document_utils import allowed_file, is_file_size_exceeded

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Blueprints
main_bp = Blueprint('documents', __name__)
upload_bp = Blueprint('upload', __name__)
detect_bp = Blueprint('detect', __name__)

# Initialize Document Service
document_service = DocumentService()


@upload_bp.route('/upload', methods=['POST'])
def upload_document():
    """Handles document uploads."""
    logger.info('Uploading document')

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    file_name = file.filename

    if not allowed_file(file_name):
        return jsonify({'error': 'Selected document not allowed'}), 400

    if is_file_size_exceeded(file, file_name):
        return jsonify({'error': 'Selected document is very heavy: Max 2MB'}), 400

    try:
        document_service.upload_file(file, file_name)
        return jsonify({'message': 'File uploaded successfully'}), 200
    except Exception as e:
        logger.exception('Error uploading file: %s', e)
        return jsonify({'error': 'Internal server error'}), 500


@main_bp.route('/documents', methods=['GET'])
def list_documents():
    """Lists all documents stored in S3."""
    try:
        document_list = document_service.list_files()
        return jsonify(document_list), 200
    except Exception as e:
        logger.exception('Error listing documents: %s', e)
        return jsonify({'error': 'Internal server error'}), 500


@detect_bp.route('/detect', methods=['POST'])
def detect_document_category():
    """Detects and updates document category."""
    try:
        document_id = request.json.get('document_id')
        if not document_id:
            return jsonify({'error': 'Missing document_id'}), 400

        logger.info('Detecting category for document %s', document_id)

        result = document_service.detect_and_update_category(document_id)

        if 'error' in result:
            return jsonify(result), 404 if result['error'] == 'Document not found' else 500

        return jsonify(result), 200

    except Exception as e:
        logger.exception('Error detecting/updating category for document: %s', e)
        return jsonify({'error': 'Internal server error'}), 500
