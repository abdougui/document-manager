from typing import Dict


class OpenAIConfig:
    def __init__(
        self, api_key: str, organization: str, project: str, base_url: str = 'https://api.openai.com/v1'
    ) -> None:
        self.api_key = api_key
        self.organization = organization
        self.project = project
        self.base_url = base_url

    def get_headers(self) -> Dict[str, str]:
        """
        Returns the HTTP headers for the API call.
        """
        return {
            'accept': 'text/event-stream',
            'accept-language': 'en,ar;q=0.9,fr;q=0.8',
            'authorization': f'Bearer {self.api_key}',
            'content-type': 'application/json',
            'dnt': '1',
            'openai-organization': self.organization,
            'openai-project': self.project,
            'origin': 'https://platform.openai.com',
            'priority': 'u=1, i',
            'referer': 'https://platform.openai.com/',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/133.0.0.0 Safari/537.36'
            ),
        }
