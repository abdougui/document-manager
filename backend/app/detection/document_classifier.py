import logging
import os
from typing import Dict, List, Optional

import tiktoken
from openai import OpenAI, RateLimitError

from app.detection.openai_chat_service import OpenAIChatService
from app.detection.openai_config import OpenAIConfig
from app.factories.processor_factory import DocumentProcessorFactory

logger = logging.getLogger(__name__)


class DocumentClassifier:
    # Mapping of model names to their maximum token limits
    MODEL_MAX_TOKENS = {
        'gpt-4o-mini': 4096,
    }
    # Reserve some tokens for the API's response and overhead.
    DEFAULT_RESERVED_RESPONSE_TOKENS = 70

    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-4o-mini') -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                'OpenAI API key must be provided either as an argument or via the OPENAI_API_KEY environment variable.'
            )

        self._client = OpenAI(api_key=self.api_key)
        self.model = model

        # Set up the tokenizer for the specified model.
        try:
            self.token_encoder = tiktoken.encoding_for_model(self.model)
        except Exception as e:
            logger.error('Failed to load tokenizer for model %s: %s', self.model, e)
            raise

        self.max_tokens_for_model = self.MODEL_MAX_TOKENS.get(self.model, 4096)

    def _truncate_text_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate the text so that it does not exceed max_tokens."""
        tokens = self.token_encoder.encode(text)
        truncated_tokens = tokens[:max_tokens]
        return self.token_encoder.decode(truncated_tokens)

    def _build_prompt_messages(self, file_content: str) -> List[Dict[str, str]]:
        system_message = 'You are a helpful assistant.'
        user_message_prefix = (
            'Categorize the following document into one of these categories: '
            'invoice, contract, report, etc. (in English). '
            'Reply with the category name only.\n\n'
            'Document:\n'
        )

        # Calculate token counts for the fixed parts of the prompt.
        system_tokens = len(self.token_encoder.encode(system_message))
        prefix_tokens = len(self.token_encoder.encode(user_message_prefix))

        # Determine the available tokens for the document text.
        available_document_tokens = self.max_tokens_for_model - (
            system_tokens + prefix_tokens + self.DEFAULT_RESERVED_RESPONSE_TOKENS
        )
        if available_document_tokens <= 0:
            raise ValueError("The fixed prompt components exceed the model's maximum token limit.")

        # Truncate the document content to fit within the available tokens.
        truncated_content = self._truncate_text_to_tokens(file_content, available_document_tokens)
        user_message = f'{user_message_prefix}{truncated_content}\n\nCategory:'

        return [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message},
        ]

    def detect_category(self, file_name: str, content: str) -> str:
        # Determine the appropriate processor based on file extension.
        file_extension = file_name.split('.')[-1].lower()
        processor = DocumentProcessorFactory.get_processor(file_extension)
        file_content = processor.extract_text(content)

        # Build prompt messages with dynamically calculated token limits.
        messages = self._build_prompt_messages(file_content)
        prompt = messages[1].get('content')
        try:
            logger.info('Uploading document to OpenAI API.')
            logger.info('Detecting document category using OpenAI API.')
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=10,
                temperature=0.5,
            )

            # Extract and clean the result.
            category = completion.choices[0].message.content.strip()
            if not category:
                raise Exception('OpenAI API returned an empty category.')

        except RateLimitError:
            logger.error('Failed to detect document category using openai module : LIMIT REACHED')
            category = self.detect_via_chat_service(prompt=prompt)

        except Exception as e:
            logger.error('Failed to detect document category: %s', e)
        logger.info('Document: {%s} category detected: %s', file_name, category)
        return category

    # This function perfom a simmilar request in openai playground
    def detect_via_chat_service(self, prompt: str):
        logger.error('Trying to retreive category using openai playground')
        config = OpenAIConfig(
            api_key='PLAYGROUND API REQUEST',
            organization='PLAYGROUND API REQUEST',
            project='PLAYGROUND API REQUEST',
        )

        chat_service = OpenAIChatService(config)
        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt,
                        },
                    ],
                },
            ],
            'temperature': 0.5,
            'max_completion_tokens': 10,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'model': 'gpt-4o-mini',
            'response_format': {'type': 'text'},
            'stream': True,
            'stream_options': {'include_usage': True},
        }

        try:
            category = ''
            for content in chat_service.stream_chat_completion_content(payload):
                category += content
            return category
        except Exception as e:
            logger.error('Failed to detect document category', e)
