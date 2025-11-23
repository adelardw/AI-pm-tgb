import os
import json
from langchain.tools import tool
from pydantic import BaseModel, Field, ValidationError

class WriteFileInput(BaseModel):
    file_name: str
    message: str
    append: bool = False
    save_dir: str = "agent_files"

class ReadFileInput(BaseModel):
    file_name: str
    save_dir: str = "agent_files"


@tool
def write_file(json_args: str) -> str:
    """
    Записывает или дописывает текст в файл.
    Принимает ОДИН АРГУМЕНТ: строку в формате JSON с ключами 'file_name', 'message', и опционально 'append', 'save_dir'.
    Пример: '{"file_name": "plan.txt", "message": "Это мой план.", "append": false}'
    """
    try:
        data = json.loads(json_args)
        args = WriteFileInput.model_validate(data)

    except json.JSONDecodeError:
        return f"Ошибка: полученная строка не является корректным JSON: {json_args}"
    except ValidationError as e:
        return f"Ошибка валидации аргументов: {e}. Убедитесь, что JSON содержит все необходимые поля ('file_name', 'message')."

    dir_path = os.path.join(os.path.abspath(os.curdir), args.save_dir)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, args.file_name)
    mode = 'a' if args.append else 'w'

    try:
        with open(file_path, mode, encoding='utf-8') as f:
            if args.append and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                f.write("\n")
            f.write(args.message)
        return f"Файл '{args.file_name}' успешно сохранен."
    except Exception as e:
        return f"Ошибка при записи файла '{args.file_name}': {e}"


@tool
def read_file(json_args: str) -> str:
    """
    Читает и возвращает содержимое файла.
    Принимает ОДИН АРГУМЕНТ: строку в формате JSON с ключом 'file_name' и опционально 'save_dir'.
    Пример: '{"file_name": "plan.txt"}'
    """
    try:
        data = json.loads(json_args)
        args = ReadFileInput.model_validate(data)

    except json.JSONDecodeError:
        return f"Ошибка: полученная строка не является корректным JSON: {json_args}"
    except ValidationError as e:
        return f"Ошибка валидации аргументов: {e}. Убедитесь, что JSON содержит ключ 'file_name'."

    file_path = os.path.join(os.path.abspath(os.curdir), args.save_dir, args.file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Ошибка: Файл с именем '{args.file_name}' не найден в директории '{args.save_dir}'."
    except Exception as e:
        return f"Ошибка при чтении файла '{args.file_name}': {e}"


FILE_SYSTEM_TOOL = [read_file, write_file]