import logging

from app.detection.document_classifier import DocumentClassifier
from app.storage.s3_file_storage import S3FileStorage

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.storage = S3FileStorage()
        self.classifier = DocumentClassifier()

    def upload_document(self, file, file_name):
        """Uploads a document to S3."""
        document = self.storage.upload_file(file=file, file_name=file_name)
        logger.info(f'File {file_name} uploaded successfully.')
        return document

    def list_documents(self):
        """Retrieves a list of documents from S3."""
        return self.storage.retrieve_s3_objects()

    def detect_and_update_category(self, document_id):
        """Detects document category and updates metadata in S3."""
        document_object = self.storage.find_file_object_by_document_id(document_id)

        if not document_object:
            logger.error(f'Document {document_id} has no content.')
            return {'error': 'Document not found'}

        # Read document content
        document_content = document_object['Body'].read()

        # Detect document category
        category = self.classifier.detect_category(file_name=document_id, content=document_content)

        # Update document metadata with detected category
        self.storage.update_document_category(document_key=document_id, category=category)

        logger.info(f'Document {document_id} categorized as {category}')

        return {'document_id': document_id, 'detected_category': category}

    def delete_document(self, document_id):
        """Delete a document from S3."""
        deleted = self.storage.remove_file_object_by_document_id(document_id=document_id)
        logger.info(f'File {document_id} uploaded successfully.')
        return {'message': 'Document deleted' if deleted else 'Error while deleting document'}
