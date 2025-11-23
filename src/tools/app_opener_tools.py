import subprocess
from langchain.tools import tool
import ast


@tool
def subprocess_tool(app_name: str):

    """
    Открытие системного приложения app_name с помощью командной строки.
    app_name - название приложения
    """
    try:
        input_app = ast.literal_eval(app_name).values()[0]
    except:
        input_app = app_name
    try:
        subprocess.run(f'open -a "{input_app}"', shell=True, check=True)
        return f"Successfully opened '{input_app}'"
    except subprocess.CalledProcessError:
        return f"No finded '{input_app}'"





APP_OPENER_TOOL = [subprocess_tool]
