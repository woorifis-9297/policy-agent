"""
Shopping Agent - Low-Level LangGraph
-------------------------------------
Same ReAct behavior as agent.py, but built by hand with StateGraph
instead of the prebuilt create_agent. Read this alongside agent.py to see
exactly what State / Node / Edge the prebuilt version was hiding.
"""

import logging
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from shopping_agent.agent import get_llm
from shopping_agent.prompts import SYSTEM_PROMPT
from shopping_agent.tools import SHOPPING_TOOLS

load_dotenv(override=True)

logger = logging.getLogger("shopping_agent.lowlevel")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [NODE] %(message)s"))
    logger.addHandler(_handler)

TOOLS_BY_NAME = {t.name: t for t in SHOPPING_TOOLS}


# ---- State ----------------------------------------------------------------
# The only thing every node reads from / writes back into. `add_messages`
# is the reducer: instead of overwriting the list, new messages are appended.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ---- Nodes ------------------------------------------------------------------
_llm = get_llm().bind_tools(SHOPPING_TOOLS)


def call_model(state: AgentState) -> dict:
    """model 노드: 대화 이력 + 시스템 프롬프트를 LLM에 넘기고 응답을 받는다."""
    logger.info("model node 호출 (messages=%d개)", len(state["messages"]))
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = _llm.invoke(messages)
    return {"messages": [response]}


def call_tools(state: AgentState) -> dict:
    """tools 노드: 직전 AI 메시지의 tool_calls를 하나씩 직접 실행한다."""
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        logger.info("tool 실행: %s(%s)", call["name"], call["args"])
        tool = TOOLS_BY_NAME[call["name"]]
        output = tool.invoke(call["args"])
        results.append(
            ToolMessage(content=str(output), tool_call_id=call["id"], name=call["name"])
        )
    return {"messages": results}


# ---- Edges (conditional routing) -------------------------------------------
def route_after_model(state: AgentState) -> str:
    """LLM이 tool_calls를 냈으면 tools 노드로, 아니면 종료."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# ---- Graph assembly ---------------------------------------------------------
builder = StateGraph(AgentState)
builder.add_node("model", call_model)
builder.add_node("tools", call_tools)

builder.add_edge(START, "model")
builder.add_conditional_edges("model", route_after_model, {"tools": "tools", END: END})
builder.add_edge("tools", "model")  # ReAct loop: 툴 실행 후 다시 LLM에게

graph = builder.compile()
