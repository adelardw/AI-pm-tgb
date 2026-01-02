from typing import TypedDict, Literal
from graphs.structured_outputs import NewsStructuredOutputs

from datetime import datetime

class NewsGraphState(TypedDict):
    input: str
    search_query: str
    original_news: list[str]
    batch_results: list[NewsStructuredOutputs]
    output: str

class DefaultAssistant(TypedDict):
    user_message: str
    local_context: list[str]
    global_context: list[str]
    image_url: list[str]
    generation: str 
    recalled_images: list
    
    user_id: str
    thread_id: str
    make_history_summary: bool
    previous_thread_id: str
    search_query: str
    web_query: str

    time: datetime
    web_context: str
    need_recall: bool
    need_web_search: bool