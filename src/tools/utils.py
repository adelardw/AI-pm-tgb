import re
from src.config import (LAST_NAME_STEM_EN, LAST_NAME_STEM_RU, FIRST_NAME_STEM_EN,
                    FIRST_NAME_STEM_RU, PATRONYMIC_STEM_EN, PATRONYMIC_STEM_RU)


def mask_personal_data(text: str) -> str:
    """
    Маскирует персональные данные в тексте, сохраняя URL-адреса нетронутыми.
    """

    urls = []

    url_pattern = r'(?:https?://[^\s<>"]+|www\.[^\s<>"]+|mailto:[^\s<>"]+)'


    def isolate_url(match):
        urls.append(match.group(0))
        return f"__URL_PLACEHOLDER_{len(urls)-1}__"

    text_without_urls = re.sub(url_pattern, isolate_url, text, flags=re.IGNORECASE)


    patterns = {
        'ПАСПОРТ': r'\b(?:\d{2}\s\d{2}|\d{4})\s\d{6}\b',
        'EMAIL': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'ФИО': r'\b[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?\b',
        'NAME': r'\b[A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b',
        'API_KEY': r'\b[a-zA-Z0-9-_.]{32,}\b',
        'ДОКУМЕНТ': r'\b(?:серия|номер|паспорта|ву|инн|снилс|№|series|number|ID)\s*[:]?\s*([a-zA-Z0-9\s-]+)\b',

        "Имя": rf'(?i)\b({FIRST_NAME_STEM_RU}|[JYI]{FIRST_NAME_STEM_EN[1:]})\w{{0,4}}\b',
        "Фамилия": rf'(?i)\b({LAST_NAME_STEM_RU}|{LAST_NAME_STEM_EN})\w{{0,4}}\b',
        "Отчество":  rf'(?i)\b({PATRONYMIC_STEM_RU}|{PATRONYMIC_STEM_EN})\w{{0,4}}\b'
    }


    ignore_case_for = ['ДАТА', 'ДОКУМЕНТ', 'EMAIL']
    masked_text = text_without_urls

    for data_type, pattern in patterns.items():
        flags = re.IGNORECASE if data_type in ignore_case_for else 0
        masked_text = re.sub(
            pattern,
            '****',
            masked_text,
            flags=flags
        )

    final_text = masked_text
    for i, url in enumerate(urls):
        final_text = final_text.replace(f"__URL_PLACEHOLDER_{i}__", url)

    return final_text

