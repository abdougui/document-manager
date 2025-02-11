import io

from PyPDF2 import PdfReader

from app.processors.document_processor import DocumentProcessor


class PDFFileProcessor(DocumentProcessor):
    def extract_text(self, file_content) -> str:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
