import io

from docx import Document

from app.processors.document_processor import DocumentProcessor


class DOCXFileProcessor(DocumentProcessor):
    def extract_text(self, file_content) -> str:
        doc = Document(io.BytesIO(file_content))
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
