import logging
import os
from typing import Optional

from openai import OpenAI

from app.factories.processor_factory import DocumentProcessorFactory

logger = logging.getLogger(__name__)


class DocumentClassifier:
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-4o-mini') -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self._client = OpenAI(api_key=self.api_key)
        if not self.api_key:
            raise ValueError(
                'OpenAI API key must be provided either as an argument or via the OPENAI_API_KEY environment variable.'
            )
        self.model = model

    def detect_category(self, file_name: str, content: str) -> str:
        file_extension = file_name.split('.')[-1].lower()
        processor = DocumentProcessorFactory.get_processor(file_extension)
        file_content = processor.extract_text(content)

        # Upload the file content to OpenAI
        try:
            logger.info('Uploading document to OpenAI API.')
            prompt = (
                'Categorize the following document into one of these categories: '
                'invoice, contract, report, or other.\n\nDocument:\n'
                f'{file_content}\n\nCategory:'
            )
            logger.info('Detecting document category using OpenAI API.')
            completion = self._client.chat.completions.create(
                model=self.model,  # or another GPT model
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                max_tokens=10,
                temperature=0,
            )

            category = completion.choices[0].message.content
            if not category:
                raise Exception('OpenAI API returned an empty category.')
            logger.info('Document category detected: %s', category)
            return category

        except Exception as e:
            logger.error('Failed to detect document category: %s', e, exc_info=True)
            raise
