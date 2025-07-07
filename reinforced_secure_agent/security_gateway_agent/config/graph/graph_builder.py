from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import START, END

from config.nodes.nodes import should_continue, agent  # , web_search_tool

checkpointer = MemorySaver()

graph_builder = StateGraph(MessagesState)


def build_graph():
    graph_builder.add_node('agent', agent)
    # tool_node 노드 따로 추가하지 않음

    graph_builder.add_edge(START, 'agent')
    graph_builder.add_conditional_edges(
        'agent',
        should_continue,
        {
            'agent': 'agent',  # agent가 계속 판단 및 도구 호출 반복
            'end': END
        }
    )

    return graph_builder.compile(checkpointer=checkpointer)

