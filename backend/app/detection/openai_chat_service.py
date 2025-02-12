import json
from typing import Any, Dict, Iterator, Optional

import requests

from app.detection.openai_config import OpenAIConfig


class OpenAIChatService:
    def __init__(self, config: OpenAIConfig, session: Optional[requests.Session] = None) -> None:
        self.config = config
        self.session = session or requests.Session()

    def stream_chat_completion_content(self, payload: Dict[str, Any]) -> Iterator[str]:
        url = f'{self.config.base_url}/chat/completions'
        headers = self.config.get_headers()

        with self.session.post(url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith('data: '):
                        data_str = line[len('data: ') :].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        choices = data_json.get('choices', [])
                        for choice in choices:
                            delta = choice.get('delta', {})
                            content = delta.get('content')
                            if content:
                                yield content
