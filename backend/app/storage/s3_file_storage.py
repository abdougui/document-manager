import logging
import uuid
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

from app.config import Config
from app.storage.document_storage_interface import IDocumentStorage
from app.utils.document_utils import extract_metadata

logger = logging.getLogger(__name__)


class S3FileStorage(IDocumentStorage):
    def __init__(self):
        self._config = Config()
        self._client = self._create_client()

    def _create_client(self):
        aws_access_key_id = self._config._aws_access_key
        aws_secret_access_key = self._config._aws_secret_access_key
        region_name = self._config._aws_region
        self._bucket = self._config._s3_bucket

        if not aws_access_key_id or not aws_secret_access_key or not region_name:
            raise ValueError('AWS credentials are not set in the environment.')

        try:
            return boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        except Exception as e:
            logger.error(f'Error while trying to connect to AWS: {e}')

    def upload_file(self, file, file_name: str) -> Dict[str, Any]:
        try:
            document_id = f'{str(uuid.uuid4())}_{secure_filename(file_name)}'
            s3_key = f'documents/{document_id}'
            self._client.upload_fileobj(
                file,
                self._bucket,
                s3_key,
                ExtraArgs={
                    'Metadata': extract_metadata(
                        file_multipart=file,
                        file_name=file_name,
                        document_id=document_id,
                    )
                },
            )
            logger.info(f'File "{file_name}" has been uploaded to bucket "{self._bucket}".')
            return document_id

        except ClientError as e:
            logger.error(f'Error uploading file to S3: {e}')
            raise Exception('Error uploading file to S3')
        except Exception as e:
            logger.error(f'Unexpected error uploading file: {e}')
            raise Exception('Unexpected error uploading file', e)

    def retrieve_s3_objects(self, prefix: str = 'documents') -> list:
        try:
            logger.info(f'Listing objects in bucket "{self._bucket}" with prefix "{prefix}"')
            response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
            # If there are no objects, return an empty list
            if 'Contents' not in response:
                return []
            # Build file details for each object found
            return [self._build_file_data(obj) for obj in response['Contents']]

        except Exception as e:
            logger.error('Error retrieving S3 objects', exc_info=e)
            raise

    def _build_file_data(self, obj) -> dict:
        file_key = obj['Key']
        file_url = f'https://{self._bucket}.s3.amazonaws.com/{file_key}'
        metadata = self.get_s3_file_metadata(file_key)

        return {
            'filename': file_key.split('/')[-1],
            'file_url': file_url,
            'metadata': metadata,
            'size': obj['Size'],
            'last_modified': obj['LastModified'].isoformat(),
        }

    def get_s3_file_metadata(self, file_key: str) -> Dict[str, Any]:
        logger.debug('Getting metadata for file key: %s', file_key)
        try:
            response = self._client.head_object(Bucket=self._bucket, Key=file_key)
            metadata = response.get('Metadata', {})
            logger.debug('Metadata for file key %s: %s', file_key, metadata)
            return metadata
        except Exception as e:
            logger.error('Error retrieving metadata for file key %s: %s', file_key, e)
            return {'error': str(e)}

    def find_file_object_by_document_id(self, document_id: str) -> Dict[str, Any]:
        logger.debug('Searching for document with id: %s', document_id)
        prefix = f'documents/{document_id}'
        try:
            object_content = self._client.get_object(Bucket=self._bucket, Key=prefix)
            logger.info(
                'List objects response for document id %s: %s',
                document_id,
                object_content,
            )
        except Exception as e:
            logger.error('Error listing objects for document id %s: %s', document_id, e)
            raise Exception(f'Error listing objects for document id {document_id}') from e
        return object_content

    def update_document_category(self, document_key: str, category: str):
        document_key = f'documents/{document_key}'
        try:
            head_response = self._client.head_object(Bucket=self._bucket, Key=document_key)
            current_metadata = head_response.get('Metadata', {})
        except Exception as e:
            logger.error(f'Error retrieving metadata for {self._bucket}/{document_key}: {e}')
            return
        current_metadata['category'] = category

        try:
            self._client.copy_object(
                Bucket=self._bucket,
                Key=document_key,
                CopySource={'Bucket': self._bucket, 'Key': document_key},
                Metadata=current_metadata,
                MetadataDirective='REPLACE',
            )
            logger.info(f'Metadata for {self._bucket}/{document_key} updated successfully!')
        except Exception as e:
            logger.error(f'Error updating metadata for {self._bucket}/{document_key}: {e}')

    def remove_file_object_by_document_id(self, document_id: str) -> Dict[str, Any]:
        logger.debug('Attempting to remove file object for document id: %s', document_id)
        object_key = f'documents/{document_id}'
        try:
            response = self._client.delete_object(Bucket=self._bucket, Key=object_key)
            logger.info(
                'Successfully removed file object for document id %s: %s',
                document_id,
                response,
            )
        except Exception as e:
            logger.error('Error removing file object for document id %s: %s', document_id, e)
            return False
        return True
