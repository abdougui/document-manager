from abc import ABC, abstractmethod
from typing import Any, Dict


class IDocumentStorage(ABC):
    @abstractmethod
    def upload_file(self, file, file_name: str) -> bool:
        pass

    @abstractmethod
    def retrieve_s3_objects(self, prefix: str) -> Dict[str, Any]:
        pass
