import os
import sys

import pytest

# Insert the parent directory (project root) at the beginning of sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(autouse=True)
def set_aws_env_vars():
    os.environ['MY_AWS_SECRET_ACCESS_KEY'] = 'YOUR_AWS_SECRET_ACCESS_KEY'
    os.environ['MY_AWS_ACCESS_KEY_ID'] = 'YOUR_AWS_ACCESS_KEY_ID'
    os.environ['MY_AWS_DEFAULT_REGION'] = 'YOUR_AWS_DEFAULT_REGION'
    os.environ['MY_AWS_STORAGE_BUCKET_NAME'] = 'YOUR_AWS_STORAGE_BUCKET_NAME'
    os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY'
