import json
import time
from collections import deque
from langgraph.graph import START, END, StateGraph
from beautylogger import logger

from graphs.graph_states import WebSurfer
from graphs.structured_outputs import WebStructuredOutputs, ActualJSElementsStructuredOutputs, SearchStructuredOutputs
from llm import OpenRouterChat
from config import OPEN_ROUTER_API_KEY
from graphs.utils import DDGSSeleniumSearch
from graphs.prompts import web_agent_prompt, focus_web_prompt, make_search_query_prompt

llm = OpenRouterChat(OPEN_ROUTER_API_KEY,
                     model_name='google/gemini-2.5-flash-lite-preview-09-2025')

web_agent = web_agent_prompt | llm.with_structured_output(WebStructuredOutputs)
focus_agent = focus_web_prompt | llm.with_structured_output(ActualJSElementsStructuredOutputs)
search_agent = make_search_query_prompt | llm.with_structured_output(SearchStructuredOutputs)
web_instance = DDGSSeleniumSearch()

def make_user_query(state):
    user_query = state['query']
    search_query = search_agent.invoke({"input": user_query}).search_query

    web_instance.get_links(search_query)
    web_instance.open_link()

    state['query'] = user_query
    return state


def selection(state: WebSurfer):
    logger.info("--- [Node: selection] ---")
    query = state['query']

    logger.info("Пауза 2 сек. для стабилизации страницы...")
    time.sleep(2)

    web_instance.make_sreenshot()

    if not state.get('reason', None):
        state['reason'] = deque([])

    if len(state['reason']) >= 5:
            state['reason'].popleft()

    if not state.get('action', None):
        state['action'] = deque([])

    if len(state['action']) >= 5:
        state['reason'].popleft()

    elements_with_rect = web_instance.execute_invisivle_analysis()
    elements_with_rect = web_instance.filter_by_blacklist(elements_with_rect)
    elements_without_rect = web_instance.get_elements_without_rect(elements_with_rect)

    state['elements'] = elements_without_rect
    state['raw_elements'] = elements_with_rect


    web_instance.draw_highlights_on_image(elements_with_rect)
    return state

def command(state):
    logger.info("--- [Node: command] ---")
    query = state['query']
    elements = state['elements']

    if not elements:
        logger.warning("Агенту не передано элементов. Вызываю LLM без элементов.")

    elements_text, image_url = web_instance.get_llm_inputs(elements)

    reason = state['reason']
    action = state['action']

    prompt_input = {
        "reason": f'Информация о том, как завершилось прошлые действия: {", ".join(reason)}',
        "action": f'Информация о последних действиях: {", ".join(action)}',
        "user_goal": f"Моя цель: {query}",
        "elements": f"Вот интерактивные элементы на текущей странице:\n{elements_text}",
        "image_url": image_url}

    try:
        assistant_answer = web_agent.invoke(prompt_input)
        state['assistant_answer'] = assistant_answer
        state['reason'].append(assistant_answer.reason)
        state['action'].append(assistant_answer.action)
        logger.info(f"Ответ LLM: {assistant_answer}")
    except Exception as e:
        logger.error(f"Ошибка вызова LLM в 'command': {e}")
        state['assistant_answer'] = WebStructuredOutputs(action="scroll", direction="down", reason="Ошибка LLM, пробую проскроллить.")

    return state

def route(state):

    logger.info("--- [Node: route] ---")

    if 'assistant_answer' not in state or not state['assistant_answer']:
        logger.error("В 'route' не пришел 'assistant_answer'. Завершаю.")
        return END

    action_config: WebStructuredOutputs = state['assistant_answer']

    if action_config.action == 'done':
        logger.info(f"Цель достигнута! Причина: {action_config.reason}")
        return END
    else:
        try:
            logger.info(f"Выполнение действия: {action_config}")

            logger.debug("Присваиваю data-agent-id в DOM...")
            web_instance.execute_invisivle_apply_ids()
            web_instance.action(action_config)

        except Exception as e:
            logger.error(f"Произошла ошибка во время web.action: {e}.")
            time.sleep(1)

        return 'selection'


workflow = StateGraph(WebSurfer)
workflow.add_node("search", make_user_query)
workflow.add_node("selection", selection)
workflow.add_node("command", command)

workflow.add_edge(START, "search")
workflow.add_edge("search", "selection")
workflow.add_edge("selection", 'command')

workflow.add_conditional_edges(
    "command",
    route,
    {
        "selection": "selection",
        END: END
    }
)

web_ddgs_graph = workflow.compile(debug=False)

"""
if __name__ == '__main__':


    print("--- [Main] Тестирование завершено. ---")
    print("--- [Main] Вызов graph.invoke... ---")
    web_ddgs_graph.invoke({"query": "Купить билет в Армению из Москвы на 10 ноября 2025"
                     }, config = {"recursion_limit": 100})

"""