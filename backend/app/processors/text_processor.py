from app.processors.document_processor import DocumentProcessor


class TextFileProcessor(DocumentProcessor):
    def extract_text(self, file_content) -> str:
        return file_content
