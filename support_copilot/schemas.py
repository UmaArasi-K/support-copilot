from pydantic import BaseModel, Field
from typing import Literal


Category = Literal["billing", "account_access", "feature_request", "bug",
                   "other"]
Urgency = Literal["low", "medium", "high"]


class Ticket(BaseModel):
    category: Category
    urgency: Urgency
    summary: str = Field(min_length=5, max_length=200)
