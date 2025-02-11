import os


class Config:
    def __init__(self):
        self._aws_secret_access_key = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
        self._aws_access_key = os.environ.get('MY_AWS_ACCESS_KEY_ID')
        self._aws_region = os.environ.get('MY_AWS_DEFAULT_REGION', 'eu-north-1')
        self._s3_bucket = os.environ.get('MY_AWS_STORAGE_BUCKET_NAME')

    def __repr__(self):
        return (
            f'AWS_SECRET_ACCESS_KEY={self._aws_secret_access_key}, '
            f'access key{self._aws_access_key}, '
            f'region={self._aws_region}>',
            f'bucket={self._s3_bucket}>',
        )
