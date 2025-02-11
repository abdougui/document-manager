from abc import ABC, abstractmethod


class DocumentProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_content) -> str:
        pass
