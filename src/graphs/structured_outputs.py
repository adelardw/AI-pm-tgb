from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class NewsStructuredOutputs(BaseModel):
    ners: list[str] = Field([], description='Python список из всевозможных именованных сущностей, которые могут содержаться в тексте')
    summary: str = Field(..., description='Суммаризация текста из новости')

class SearchStructuredOutputs(BaseModel):
    search_query: str = Field(..., description='Поисковый запрос из запроса пользователя')


class Elemetns(BaseModel):
    id: int = Field(..., description='Индекс элемента')
    description: int = Field(..., description='Индекс элемента')

class ActualJSElementsStructuredOutputs(BaseModel):
    actual_elements: list[int] = Field(..., description = """Список из id веб елементов, в которых действия
                                                            для данного запроса пользователя подходят наилучшим образом.""")

class WebStructuredOutputs(BaseModel):
    action: Literal['click', 'type', 'scroll', 'done', 'submit','back'] = Field(..., description="""Тип действия.
                                                                         'click' - нажатие,
                                                                         'type' - ввод текста,
                                                                         'submit' - отправка формы (нажатие Enter),
                                                                         'scroll' - прокрутка на сайте. Можно скроллить либо снизу-вверх (up) , либо сверху - вниз (down).
                                                                         'back' - возвращение к другим поисковым результатам.
                                                                         'done' - задача выполнена.""")

    direction: Optional[Literal['up','down']] = Field(None, description='Если action=scroll, иначе - None')
    element_id: Optional[int] = Field(None, description='Id элемента, с которым нужно как - то провзаимодейстовать (нажать, или найти информацию - аттрибут text)')
    text: Optional[str] = Field(None, description='Указывается если action=type - это поле с тектом у элемента с номером element_id')
    reason: Optional[str] = Field(None, description='Указывается если action=done - причина по которой action=done. Во всех остальных случаях - None')

    @field_validator('direction', mode='before')
    @classmethod
    def clean_direction(cls, v):
        """Преобразует строковый 'null' от LLM в настоящий None."""
        if v == 'null':
            return None
        return v
