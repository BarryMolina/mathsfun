# adopted from https://github.com/ArjanCodes/examples/blob/main/2024/tuesday_tips/jinja2/chat.py
from typing import Callable

from openai import OpenAI

# Models
GPT3_TURBO = "gpt-3.5-turbo"
GPT4_TURBO = "gpt-4-turbo-preview"
GROK_3_MINI = "grok-3-mini"
XAI_URL = "https://api.x.ai/v1"
OPENAI_URL = "https://api.openai.com/v1"

type ChatFn = Callable[[str], str]


def chatter(api_key: str, model: str = GROK_3_MINI, url: str = XAI_URL) -> ChatFn:
    ai_client = OpenAI(base_url=url, api_key=api_key)

    def send_chat_request(query: str) -> str:
        response = ai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": query},
            ],
        )
        chat_result = response.choices[0].message.content
        if not chat_result:
            raise ValueError("No response from the chat model.")
        return chat_result

    return send_chat_request
