import datetime
import logging
import unicodedata
from typing import Dict

ALLOWED_EXTENSIONS = {'xls', 'xlxs', 'pdf', 'docx', 'doc', 'txt'}

logger = logging.getLogger(__name__)
MAX_FILE_SIZE_MB = 2
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def allowed_file(file_name: str) -> bool:
    logger.info('checking if the file ext is allowed')
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in file_name


def extract_metadata(file_multipart, file_name: str, document_id: str, category: str = 'none') -> dict:
    logger.info('Extracting metadata')
    upload_time = datetime.datetime.utcnow().isoformat()
    unormilized_metadata = {
        'original_name': file_name,
        'filesize': str(retreive_file_size(file_multipart=file_multipart, file_name=file_name)),
        'upload_time': upload_time,
        'key': document_id,
        'category': category,
    }
    return normalize_metadata(unormilized_metadata)


def retreive_file_size(file_multipart, file_name) -> int:
    logger.info('retreive file size')
    file_multipart.seek(0, 2)
    file_size = file_multipart.tell()
    file_multipart.seek(0)
    logger.info(f'{file_name} size is {file_size}')
    return file_size


def is_file_size_exceeded(file_multipart, file_name: str) -> bool:
    file_size = retreive_file_size(file_multipart, file_name)
    return file_size > MAX_FILE_SIZE_BYTES


def normalize_metadata(metadata: Dict[str, str]) -> Dict[str, str]:
    normalized = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            normalized[key] = normalize_text(value)
        else:
            normalized[key] = value
    return normalized


def normalize_text(text: str) -> str:
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
