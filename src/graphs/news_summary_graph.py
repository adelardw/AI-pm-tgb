from langgraph.graph import START, StateGraph, END
from graphs.prompts import make_full_news_prompt, make_search_query_prompt, news_summary_agent_prompt
from graphs.graph_states import NewsGraphState
from graphs.structured_outputs import NewsStructuredOutputs, SearchStructuredOutputs
from langchain_core.output_parsers import StrOutputParser
from graphs.utils import search

from llm import OpenRouterChat
from config import OPEN_ROUTER_API_KEY

llm = OpenRouterChat(api_key=OPEN_ROUTER_API_KEY)

search_agent = make_search_query_prompt | llm.with_structured_output(SearchStructuredOutputs)
news_summary_agent = news_summary_agent_prompt | llm.with_structured_output(NewsStructuredOutputs)
final_news_agent = make_full_news_prompt | llm | StrOutputParser()


def search_node(state):
    search_query = search_agent.invoke({"input": state['input']}).search_query
    search_results = search(search_query)

    state['search_query'] = search_query
    state['original_news'] = search_results

    return state


def summary_node(state):
    answer = []
    if state['original_news']:
        for news in state['original_news']:
            answer.append(news_summary_agent.invoke({"news": news}))

        state['batch_results'] = answer
    else:
        state['batch_results'] = []

    return state

def make_news_node(state):
    if state['batch_results']:
        make_news_input = "Краткая выжимка новостей" + ",".join([ content.summary for content in state['batch_results']])
        state['output'] = final_news_agent.invoke({"news": make_news_input})
    else:
        state['output'] = "Новости не найдены, видимо, сетевая проблема"
    return state


workflow = StateGraph(NewsGraphState)

workflow.add_node('Search', search_node)
workflow.add_node('Summarization', summary_node)
workflow.add_node('MakeNews', make_news_node)

workflow.add_edge(START, "Search")
workflow.add_edge("Search","Summarization")
workflow.add_edge("Summarization", "MakeNews")
workflow.add_edge('MakeNews', END)

graph = workflow.compile(debug=False)

#if __name__ =='__main__':
#    print(graph.invoke({'input': "Расскажи о последних новостях экономики в РФ"}))