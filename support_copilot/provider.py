import os
from typing import Protocol
from openai import AzureOpenAI, BadRequestError


class ContentFilteredError(Exception):
    """The provider's safety filter blocked the request or the reply,
    or the reply leaked the system prompt."""


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
        try:
            response = self._create(system, user, schema)
        except BadRequestError as e:
            if getattr(e, "code", None) == "content_filter":
                raise ContentFilteredError(
                    "Request blocked by the provider's content filter") from e
            raise  # other 400s are real bugs: don't hide them

        choice = response.choices[0]
        if choice.finish_reason == "content_filter" or not choice.message.content:
            raise ContentFilteredError("Reply blocked by the content filter")
        return choice.message.content

    def _create(self, system: str, user: str, schema: dict):
        return self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ticket",
                    "strict": True,
                    "schema": schema,
                },
            },
        )
