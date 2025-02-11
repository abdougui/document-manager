import pytest

from app.config import Config


class TestConfig:
    @pytest.fixture(autouse=True)
    def set_env_vars(self, monkeypatch):
        monkeypatch.setenv('MY_AWS_SECRET_ACCESS_KEY', 'test_secret')
        monkeypatch.setenv('MY_AWS_ACCESS_KEY_ID', 'test_access')
        monkeypatch.setenv('MY_AWS_DEFAULT_REGION', 'test-region')
        monkeypatch.setenv('MY_AWS_STORAGE_BUCKET_NAME', 'test_bucket')

    def test_config_initialization(self):
        config = Config()
        assert config._aws_secret_access_key == 'test_secret'
        assert config._aws_access_key == 'test_access'
        assert config._aws_region == 'test-region'
        assert config._s3_bucket == 'test_bucket'
