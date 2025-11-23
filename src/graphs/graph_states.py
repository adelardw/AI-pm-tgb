from typing import TypedDict, Literal
from graphs.structured_outputs import NewsStructuredOutputs
from graphs.utils import WebChromeSearch

class NewsGraphState(TypedDict):
    input: str
    search_query: str
    original_news: list[str]
    batch_results: list[NewsStructuredOutputs]
    output: str


class WebSurfer(TypedDict):
    query: str
    elements: list[dict[str, str | int]]
    reason: list
    action: list
    assistant_answer: str