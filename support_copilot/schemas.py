from pydantic import BaseModel, Field
from typing import Literal


Topic = Literal["billing", "account_access", "order_delivery", "bug",
                "not_support", "other"]
Urgency = Literal["low", "medium", "high"]


class Ticket(BaseModel):
    topic: Topic
    urgency: Urgency
    summary: str = Field(min_length=5, max_length=200,
                         description="One short sentence, "
                         "under 200 characters.")


def strict_schema(model: type[BaseModel]) -> dict:
    schema = model.model_json_schema()
    schema["additionalProperties"] = False
    schema["required"] = list(schema["properties"])
    for field in schema["properties"].values():
        field.pop("minLength", None)
        field.pop("maxLength", None)
    return schema
