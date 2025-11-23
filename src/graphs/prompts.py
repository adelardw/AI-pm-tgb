from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from graphs.tasks import NEWS_TASK, MAKE_SEARCH_TASK, MAKE_FULL_NEWS, WEB_TASK
from graphs.utils import image_text_prompt

agent_name = "VEGA"
forbidden_agent_result = "Не удалось получить запрос от агента. Повторите Ваш запрос снова"

human_template = "Входное сообщение от пользователя: {input}\n"

make_search_query_prompt = "Ты - {agent_name}, профессионал в понимании людей и в состалвении поисковых запросов"\
"Твои задачи: {tasks}.Ответ дай строго в формате предложенной схемы.".format(agent_name=agent_name,
                                                                             tasks=MAKE_SEARCH_TASK)

news_summary_agent_prompt = "Ты - {agent_name}, профессионал в суммаризации текста и нахождении именованных сущностей из текста."\
"Твои задачи: {tasks}.Ответ дай строго в формате предложенной схемы.".format(agent_name=agent_name,tasks=NEWS_TASK)

make_full_news_prompt = "Ты - {agent_name}, профессионал в создании новостей из краткой выжимки других новостей."\
"Твои задачи: {tasks}.".format(agent_name=agent_name,tasks=MAKE_FULL_NEWS)


web_agent_pmt = "Ты — {agent_name}, AI-агент, управляющий браузером. Твоя задача — {tasks}."\
"""Интерактивные элементы на скриншоте пронумерованы. Также, в качестве контекста, тебе можнт быть известно:
какая была причина совершения прошло действия.
Проанализируй цель, изображение и список элементов, а затем верни ОДНО следующее действие в формате JSON.
ВАЖНО: После ввода текста в поле (например, в строку поиска Google), твоим следующим действием должно быть 'submit' с тем же 'element_id', чтобы имитировать нажатие клавиши Enter и запустить поиск. Не ищи кнопку "Поиск".
ВАЖНО: Если чего - то не знаешь, попробуй поисследовать страницу - поделать скроллы.
Если цель достигнута, используй 'done'.""".format(agent_name=agent_name,tasks=WEB_TASK)

focus_web_pmt = "Ты — {agent_name}, 'фокусирующий' модуль для AI-агента."\
"""Тебе дан полный список элементов со страницы (в формате JSON) и главная цель пользователя.
Твоя задача — проанализировать цель и вернуть СПИСОК (list) ID тех элементов, которые релевантны для цели.
Игнорируй мусор (футеры, пустые ссылки и т.д.).
Помимо этого, ты можешь знать ответ от другого ассистента о причине его совершения того или иного действия.

""".format(agent_name=agent_name)

make_search_query_prompt = ChatPromptTemplate.from_messages([
    ("system", make_search_query_prompt),
    ("human", human_template)]
)

news_summary_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", news_summary_agent_prompt),
    ("human", "Новость: {news}")]
)

make_full_news_prompt = ChatPromptTemplate.from_messages([
    ("system", make_full_news_prompt),
    ("human", "Суммаризация нескольких новостей: {news}")]
)

web_agent_prompt = RunnableLambda(lambda x: image_text_prompt(web_agent_pmt,  x))

focus_web_prompt = RunnableLambda(lambda x: image_text_prompt(focus_web_pmt,  x))

#focus_web_prompt = ChatPromptTemplate.from_messages([
#    ("system", focus_web_pmt),
#    ("human","Прошлые действия: {action}"
#          "Описание/причины прошлых действий: {reason}"),
#    ("human", human_template + "Найденные элементы: \n {elements} \n")]
#)