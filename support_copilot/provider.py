import os
from typing import Protocol
from openai import AzureOpenAI


class LLMProvider(Protocol):
    model: str

    def complete_json(self, system: str, user: str, schema: dict) -> str:
        """Send a prompt and return the model's raw reply as a JSON string."""


class AzureOpenAICompatProvider:
    def __init__(self):
        self.model = os.environ["LLM_MODEL"]
        self.client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ["API_VERSION"],
            timeout=20,
            max_retries=2
        )

    def complete_json(self, system: str, user: str, schema: dict) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "ticket",
                                             "schema": schema}},
            )
        return response.choices[0].message.content
