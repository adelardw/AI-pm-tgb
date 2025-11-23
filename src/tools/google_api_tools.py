import base64
from bs4 import BeautifulSoup
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger
import os
from langchain.tools import tool
from tools.utils import mask_personal_data
from src.config import TOKEN_PATH, SCOPES, CRED_SECRET_PATH


def get_google_creds():
    """
    Получения учетных данных Google API.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CRED_SECRET_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds


def create_calendar_event(data: dict):
    """
    Создает событие в Google Calendar, используя готовый объект service.
    """
    logger.info(f'[DEBUG] {data}')
    summary = data.get("summary")
    start_time_str = data.get("start")
    end_time_str = data.get("end")
    description = data.get("description")
    location = data.get("location")
    timezone = data.get("timezone", "Europe/Moscow")
    reminders_format = data.get("remind_format",'minutes')
    reminders_num = data.get("remind_num",'minutes')
    creds = get_google_creds()

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time_str,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time_str,
                "timeZone": timezone,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", reminders_format: reminders_num},
                    {"method": "popup", reminders_format: reminders_num},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        template = f"Событие '{event['summary']}' успешно создано: {event.get('htmlLink')}"
        logger.info(template)
        return template

    except Exception as error:
        template = f'Ошибка при создании события в календаре: {error}'
        logger.error(template)
        return template




@tool
def get_last_emails():
    """
    Получает k последних писем из почтового ящика пользователя.

    Список словарей, где каждый словарь представляет одно письмо,
    или пустой список, если писем нет или произошла ошибка.
    """
    creds = get_google_creds()
    service = build("gmail", "v1", credentials=creds)
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            logger.info("Писем не найдено.")
            return []

        email_list = []
        for message_info in messages:
            msg = service.users().messages().get(userId='me', id=message_info['id'], format='full').execute()

            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            email_data = {"id": msg.get('id')}

            for header in headers:
                name = header.get('name')
                if name.lower() == 'from':
                    email_data['from'] = header.get('value')
                if name.lower() == 'subject':
                    email_data['subject'] = header.get('value')
                if name.lower() == 'date':
                    email_data['date'] = header.get('value')

            plain_text_body = ""
            html_body = ""

            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get("mimeType") == "text/plain" and "data" in part.get("body"):
                        data = part['body']['data']
                        plain_text_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                    elif part.get("mimeType") == "text/html" and "data" in part.get("body"):
                        data = part['body']['data']
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'body' in payload and 'data' in payload['body']:
                 html_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')


            if plain_text_body:
                email_data['body'] = mask_personal_data(plain_text_body)
            elif html_body:

                soup = BeautifulSoup(html_body, "html.parser")
                email_data['body'] = mask_personal_data(soup.get_text(separator='\n', strip=True))
            else:
                email_data['body'] = "Тело письма не найдено."

            email_list.append(email_data)

        return email_list

    except Exception as error:
        logger.error(f"Произошла ошибка API: {error}")
        return []

CALENDAR_TOOLS = [create_calendar_event]
EMAIL_TOOLS = [get_last_emails]
