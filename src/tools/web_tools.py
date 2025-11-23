import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
from langchain.tools import tool
from ddgs import DDGS
from urllib.parse import quote

#@tool
def search(search_query: str) -> list[dict[str, str]]:
    """
    Находит ссылки на различные источники по входному запросу
    """
    search = DDGS()
    search_results = search.text(search_query, max_results = 5)
    return search_results


@tool
def open_url(url: str):
    """
    Открывает в chrome найденные ссылки из поиска
    """

    webbrowser.open_new_tab(url)

@tool
def open_top_results(search_query: str):
    """
    Выполняет поиск по DuckDuckGo и открывает топ-5 найденных ссылок
    в новых вкладках браузера Chrome.

    Используйте этот инструмент, когда пользователь просит найти что-либо
    и сразу открыть результаты в браузере.
    """

    # 1. Выполняем поиск
    results = search(search_query)

    if not results:
        return f"Поиск '{search_query}' не дал результатов."

    opened_count = 0

    # 2. Перебираем и открываем
    for item in results:
        url = item.get('href')
        if url:
            webbrowser.open_new_tab(url)
            opened_count += 1

    return f"Успешно найдено и открыто {opened_count} ссылок по запросу: '{search_query}'."

@tool
def search_chrome(search_query : str):
    """
    Открытия chrome по входному запросу
    """
    base_url = "https://www.google.com/search?q="

    encoded_query = quote(search_query)

    full_url = base_url + encoded_query

    webbrowser.open_new_tab(full_url)


WEB_SURFER_TOOLS = [open_top_results]