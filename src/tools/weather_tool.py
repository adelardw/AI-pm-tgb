import requests
from langchain.tools import tool
from beautylogger.bl import logger

@tool
def weather_tool(city_name: str = "Moscow"):
    '''
    По названию города показывает погоду на утро/день/вечер/ночь
    '''
    url = f"https://wttr.in/{city_name}?format=j1"

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'DNT': '1',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Sec-Fetch-User': '?1'})
        return response.json()
    except Exception:
        logger.info("Упс! Что-то пошло не так. Попробуйте позже.")

WEATHER_TOOL = [weather_tool]