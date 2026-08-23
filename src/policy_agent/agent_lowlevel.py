"""
Policy Agent - Low-Level LangGraph
-------------------------------------
agent.py와 동일한 ReAct 동작을 하지만, prebuilt create_agent 대신
StateGraph로 직접 구현한 버전입니다. agent.py와 함께 읽으면
prebuilt 버전이 감추고 있던 State / Node / Edge를 정확히 볼 수 있습니다.
"""

import logging
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from policy_agent.agent import get_llm
from policy_agent.prompts import SYSTEM_PROMPT
from policy_agent.tools import PORTAL_TOOLS

load_dotenv(override=True)

logger = logging.getLogger("policy_agent.lowlevel")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [NODE] %(message)s"))
    logger.addHandler(_handler)

TOOLS_BY_NAME = {t.name: t for t in PORTAL_TOOLS}


# ---- 상태(State) ----------------------------------------------------------------
# 모든 노드가 읽고 쓰는 유일한 대상. `add_messages`가 리듀서 역할을 하여
# 리스트를 덮어쓰는 대신 새 메시지를 뒤에 추가한다.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ---- 노드 ------------------------------------------------------------------
_llm = get_llm().bind_tools(PORTAL_TOOLS)


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


# ---- Edges (조건부 라우팅) -------------------------------------------
def route_after_model(state: AgentState) -> str:
    """LLM이 tool_calls를 냈으면 tools 노드로, 아니면 종료."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# ---- 그래프 조립 ---------------------------------------------------------
builder = StateGraph(AgentState)
builder.add_node("model", call_model)
builder.add_node("tools", call_tools)

builder.add_edge(START, "model")
builder.add_conditional_edges("model", route_after_model, {"tools": "tools", END: END})
builder.add_edge("tools", "model")  # ReAct 루프: 툴 실행 후 다시 LLM에게

graph = builder.compile()
