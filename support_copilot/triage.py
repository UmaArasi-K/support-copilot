import logging
from pydantic import ValidationError
from .schemas import Ticket
from .provider import LLMProvider

log = logging.getLogger(__name__)
SYSTEM_PROMPT = """You are a support-ticket triage assistant for a
    finance-oriented company. Classify the ticket below.

    Urgency levels:
    - high: the customer loses access completely, loses money, or faces
    a deadline today. Any billing, payment or charge problem counts as
    high, including a suspected or unclear error.
    - medium: something is broken or wrong, but there is a workaround,
    so it is not highly urgent.
    - low: a question or a cosmetic problem, with no impact and no
    deadline.

    Rules for tickets with more than one issue:
    - Rate urgency by the most severe issue (high > medium > low).
    - Choose the category of that same most severe issue."""


class TriageError(Exception):
    """LLM reply could not be validated into a Ticket."""


def classify(text: str, provider: LLMProvider) -> Ticket:
    raw_text = provider.complete_json(SYSTEM_PROMPT, f"Ticket: {text}",
                                      Ticket.model_json_schema())
    try:
        return Ticket.model_validate_json(raw_text)
    except ValidationError as e:
        log.error("The model %s has thrown error for the text %s",
                  provider.model, raw_text)
        raise TriageError(f"Invalid output from {provider.model}") from e


if __name__ == "__main__":
    from dotenv import load_dotenv
    from .provider import AzureOpenAICompatProvider

    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    provider = AzureOpenAICompatProvider()
    tickets = [
        "I was charged twice for my subscription this month and my card "
        "is now overdrawn. Please refund one charge today.",
        "The login page keeps showing a 404 error. "
        "I can't access my account at all.",
        "I'd like to request a feature for bulk "
        "export of reports in CSV format.",
        "app is slow and also billing looks wrong",
    ]

    for i, text in enumerate(tickets, 1):
        try:
            t = classify(text, provider)
            print(f"{i}. {t.category:<16} {t.urgency:<7} {t.summary}")
        except TriageError as e:
            print(f"{i}. INVALID OUTPUT: {e}")
        except Exception as e:
            print(f"{i}. {type(e).__name__}: {e}")
