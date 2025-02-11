from typing import Optional

from app.processors.docx_processor import DOCXFileProcessor
from app.processors.pdf_processor import PDFFileProcessor
from app.processors.text_processor import TextFileProcessor
from app.processors.xlsx_processor import XLSXFileProcessor


class DocumentProcessorFactory:
    @staticmethod
    def get_processor(file_extension: str) -> Optional[type]:
        if file_extension == 'txt':
            return TextFileProcessor()
        elif file_extension == 'pdf':
            return PDFFileProcessor()
        elif file_extension == 'docx':
            return DOCXFileProcessor()
        elif file_extension == 'xlsx':
            return XLSXFileProcessor()
        else:
            raise ValueError(f'Unsupported file extension: {file_extension}')
