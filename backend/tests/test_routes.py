import io

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


# ---------------------------
# Tests for the /upload endpoint
# ---------------------------
class TestUploadDocument:
    def test_upload_no_file(self, client):
        response = client.post('/upload')
        assert response.status_code == 400
        data = response.get_json()
        assert data.get('error') == 'No file part in the request'

    def test_upload_disallowed_file(self, client, monkeypatch):
        # Force allowed_file to return False regardless of input.
        monkeypatch.setattr('app.routes.allowed_file', lambda filename: False)
        data = {'file': (io.BytesIO(b'dummy data'), 'test.exe')}
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        assert response.status_code == 400
        data_response = response.get_json()
        assert data_response.get('error') == 'Selected document not allowed'

    def test_upload_file_size_exceeded(self, client, monkeypatch):
        # allowed_file returns True, but is_file_size_exceeded returns True.
        monkeypatch.setattr('app.routes.allowed_file', lambda filename: True)
        monkeypatch.setattr('app.routes.is_file_size_exceeded', lambda file, filename: True)
        data = {'file': (io.BytesIO(b'dummy data'), 'test.pdf')}
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        assert response.status_code == 400
        data_response = response.get_json()
        assert data_response.get('error') == 'Selected document is very heavy: Max 2MB'

    def test_upload_success(self, client, monkeypatch):
        # allowed_file returns True, is_file_size_exceeded returns False,
        # and upload_document returns a dummy document.
        monkeypatch.setattr('app.routes.allowed_file', lambda filename: True)
        monkeypatch.setattr('app.routes.is_file_size_exceeded', lambda file, filename: False)
        dummy_document = {'id': '123', 'filename': 'test.pdf'}
        monkeypatch.setattr('app.routes.document_service.upload_document', lambda file, filename: dummy_document)

        data = {'file': (io.BytesIO(b'dummy data'), 'test.pdf')}
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        assert response.status_code == 200
        data_response = response.get_json()
        assert data_response.get('message') == 'File uploaded successfully'
        assert data_response.get('document') == dummy_document

    def test_upload_exception(self, client, monkeypatch):
        # Simulate an exception during upload_document.
        monkeypatch.setattr('app.routes.allowed_file', lambda filename: True)
        monkeypatch.setattr('app.routes.is_file_size_exceeded', lambda file, filename: False)

        def raise_exception(file, filename):
            raise Exception('Upload error')

        monkeypatch.setattr('app.routes.document_service.upload_document', raise_exception)

        data = {'file': (io.BytesIO(b'dummy data'), 'test.pdf')}
        response = client.post('/upload', content_type='multipart/form-data', data=data)
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Internal server error'


# ---------------------------
# Tests for the /documents endpoint
# ---------------------------
class TestListDocuments:
    def test_list_documents_success(self, client, monkeypatch):
        dummy_list = [{'id': '123', 'filename': 'test.pdf'}]
        monkeypatch.setattr('app.routes.document_service.list_documents', lambda: dummy_list)
        response = client.get('/documents')
        assert response.status_code == 200
        assert response.get_json() == dummy_list

    def test_list_documents_exception(self, client, monkeypatch):
        # Force list_documents to throw an exception.
        monkeypatch.setattr(
            'app.routes.document_service.list_documents', lambda: (_ for _ in ()).throw(Exception('List error'))
        )
        response = client.get('/documents')
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Internal server error'


# ---------------------------
# Tests for the /detect endpoint
# ---------------------------
class TestDetectDocumentCategory:
    def test_detect_missing_document_id(self, client):
        response = client.post('/detect', json={})
        assert response.status_code == 400
        data_response = response.get_json()
        assert data_response.get('error') == 'Missing document_id'

    def test_detect_document_not_found(self, client, monkeypatch):
        monkeypatch.setattr(
            'app.routes.document_service.detect_and_update_category',
            lambda document_id: {'error': 'Document not found'},
        )
        payload = {'document_id': 'nonexistent'}
        response = client.post('/detect', json=payload)
        assert response.status_code == 404
        data_response = response.get_json()
        assert data_response.get('error') == 'Document not found'

    def test_detect_other_error(self, client, monkeypatch):
        monkeypatch.setattr(
            'app.routes.document_service.detect_and_update_category', lambda document_id: {'error': 'Some other error'}
        )
        payload = {'document_id': '123'}
        response = client.post('/detect', json=payload)
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Some other error'

    def test_detect_success(self, client, monkeypatch):
        result = {'document_id': '123', 'category': 'invoice'}
        monkeypatch.setattr('app.routes.document_service.detect_and_update_category', lambda document_id: result)
        payload = {'document_id': '123'}
        response = client.post('/detect', json=payload)
        assert response.status_code == 200
        assert response.get_json() == result

    def test_detect_exception(self, client, monkeypatch):
        def raise_exception(document_id):
            raise Exception('Detect error')

        monkeypatch.setattr('app.routes.document_service.detect_and_update_category', raise_exception)
        payload = {'document_id': '123'}
        response = client.post('/detect', json=payload)
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Internal server error'


# ---------------------------
# Tests for the /delete/<document_id> endpoint
# ---------------------------
class TestDeleteDocument:
    def test_delete_document_not_found(self, client, monkeypatch):
        monkeypatch.setattr(
            'app.routes.document_service.delete_document', lambda document_id: {'error': 'Document not found'}
        )
        response = client.delete('/delete/123')
        assert response.status_code == 404
        data_response = response.get_json()
        assert data_response.get('error') == 'Document not found'

    def test_delete_other_error(self, client, monkeypatch):
        monkeypatch.setattr(
            'app.routes.document_service.delete_document', lambda document_id: {'error': 'Deletion failed'}
        )
        response = client.delete('/delete/123')
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Deletion failed'

    def test_delete_success(self, client, monkeypatch):
        result = {'message': 'Document deleted successfully'}
        monkeypatch.setattr('app.routes.document_service.delete_document', lambda document_id: result)
        response = client.delete('/delete/123')
        assert response.status_code == 200
        assert response.get_json() == result

    def test_delete_exception(self, client, monkeypatch):
        def raise_exception(document_id):
            raise Exception('Delete error')

        monkeypatch.setattr('app.routes.document_service.delete_document', raise_exception)
        response = client.delete('/delete/123')
        assert response.status_code == 500
        data_response = response.get_json()
        assert data_response.get('error') == 'Internal server error'
