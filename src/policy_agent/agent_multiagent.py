"""
Policy Agent - Multi-Agent Workflow (Supervisor 패턴)
---------------------------------------------------------
지금까지의 agent.py / agent_lowlevel.py는 "하나의 에이전트"가 모든 툴을
다 들고 있는 구조였다. 이 파일은 반대로, 역할을 나눈 두 개의 전문 에이전트
(job_agent, policy_agent)를 supervisor가 라우팅하는 멀티에이전트 워크플로우다.

핵심 포인트: 에이전트끼리는 API로 통신하지 않는다. 하나의 그래프 안에서
같은 State(messages)를 공유하며 노드를 옮겨 다닐 뿐이다.

구조:
    START -> supervisor -> (job_agent | policy_agent | finalize)
    job_agent    -> supervisor   (다시 판단받으러 돌아옴)
    policy_agent -> supervisor
    finalize -> END              (모든 조회가 끝난 뒤 최종 답변을 한 번에 합성)

    supervisor는 최대 3번까지만 라우팅하고, 그 이상이면 강제로 finalize로 보낸다
    (LLM 라우팅 판단이 계속 애매하게 나올 경우 무한루프 방지용 안전장치).

    참고: 서브 에이전트마다 즉시 "정리 답변"을 생성하게 했더니, Gemini가 (특히
    여러 요청이 섞인 질문에서) 존재하지 않는 툴을 스스로 호출하려다 빈 텍스트만
    반환하는 버그성 동작을 보였다. 그래서 서브 에이전트는 툴 실행 결과(raw)만
    쌓아두고, 최종 답변 합성은 finalize 노드에서 한 번만 수행하도록 바꿨다.

실행:
    uv run python -m policy_agent.agent_multiagent "부서 이동을 했는데 뭘 확인해야 하고, 재택근무 규정도 알려줘"
"""

import logging
import sys
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from policy_agent.agent import get_llm
from policy_agent.prompts import SYSTEM_PROMPT
from policy_agent.tools import (
    get_all_job,
    search_it_guide,
    search_job,
    search_organization,
    search_policy,
    search_portal_by_keyword,
)

load_dotenv(override=True)

logger = logging.getLogger("policy_agent.multiagent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [MULTI] %(message)s"))
    logger.addHandler(_handler)

JOB_TOOLS = [get_all_job, search_job, search_portal_by_keyword]
POLICY_TOOLS = [search_policy, search_organization, search_it_guide]

MAX_ROUTING_STEPS = 3

SUPERVISOR_PROMPT = """당신은 두 전문 에이전트를 지휘하는 라우터입니다.
지금까지의 대화를 보고, 아래 세 단어 중 정확히 하나로만 답하세요. 다른 설명은 절대 붙이지 마세요.

- job_agent    : 아직 답변되지 않은 사내 업무(신청/조회 절차, 담당부서) 관련 요청이 남아있을 때
- policy_agent : 아직 답변되지 않은 사내 규정/정책, 조직정보, IT 가이드 관련 요청이 남아있을 때
- finish       : 사용자의 모든 요청이 이미 답변되었을 때
"""


# ---- 상태(State) ------------------------------------------------------------------
class SupervisorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str
    steps: int


# ---- Supervisor 노드 ----------------------------------------------------------
def supervisor(state: SupervisorState) -> dict:
    steps = state.get("steps", 0) + 1

    if steps > MAX_ROUTING_STEPS:
        logger.info("supervisor: 최대 라우팅 횟수(%d) 도달 -> 강제로 finalize", MAX_ROUTING_STEPS)
        return {"next": "finish", "steps": steps}

    llm = get_llm()
    # Gemini는 메시지 목록이 model(AI) 턴으로 끝나는 요청을 거부하므로,
    # (예: product_agent가 방금 답변한 직후) 라우팅용 사람 메시지를 항상 맨 끝에 붙인다.
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        *state["messages"],
        HumanMessage(content="다음 행동을 product_agent / order_agent / finish 중 하나로만 답하세요."),
    ]
    decision = llm.invoke(messages).content
    decision_text = decision if isinstance(decision, str) else str(decision)
    decision_text = decision_text.strip().lower()

    if "job" in decision_text:
        route = "job_agent"
    elif "policy" in decision_text:
        route = "policy_agent"
    else:
        route = "finish"

    logger.info("supervisor 판단 (%d/%d): %s", steps, MAX_ROUTING_STEPS, route)
    return {"next": route, "steps": steps}


# ---- 전문 에이전트 노드 (각자 자기 툴만 들고 조회만 수행, 답변 합성은 finalize가 담당) ----
def _run_subagent(state: SupervisorState, tools, name: str) -> dict:
    llm = get_llm().bind_tools(tools)
    response = llm.invoke(state["messages"])
    new_messages: list = [response]

    if getattr(response, "tool_calls", None):
        tools_by_name = {t.name: t for t in tools}
        for call in response.tool_calls:
            logger.info("[%s] tool 실행: %s(%s)", name, call["name"], call["args"])
            output = tools_by_name[call["name"]].invoke(call["args"])
            new_messages.append(
                ToolMessage(content=str(output), tool_call_id=call["id"], name=call["name"])
            )

    return {"messages": new_messages}


def job_agent(state: SupervisorState) -> dict:
    logger.info("job_agent 진입")
    return _run_subagent(state, JOB_TOOLS, "job_agent")


def policy_agent(state: SupervisorState) -> dict:
    logger.info("policy_agent 진입")
    return _run_subagent(state, POLICY_TOOLS, "policy_agent")


# ---- 최종 답변 합성 (모든 서브 에이전트 조회가 끝난 뒤 한 번만 실행) ----------------------
def finalize(state: SupervisorState) -> dict:
    logger.info("finalize: 최종 답변 생성")
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
        HumanMessage(content="지금까지 조회한 결과를 바탕으로 사용자에게 최종 답변을 작성해줘."),
    ]
    response = llm.invoke(messages)
    return {"messages": [response]}


# ---- 라우팅 ---------------------------------------------------------------------
def route_from_supervisor(state: SupervisorState) -> str:
    return state["next"]


# ---- 그래프 조립 ---------------------------------------------------------------
builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor)
builder.add_node("job_agent", job_agent)
builder.add_node("policy_agent", policy_agent)
builder.add_node("finalize", finalize)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {"job_agent": "job_agent", "policy_agent": "policy_agent", "finish": "finalize"},
)
builder.add_edge("job_agent", "supervisor")  # 서브 에이전트 작업 후 다시 supervisor에게
builder.add_edge("policy_agent", "supervisor")
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "부서 이동을 했는데 뭘 확인해야 하고, 재택근무 규정도 알려줘"
    logger.info("사용자 질문: %s", question)

    result = graph.invoke({"messages": [HumanMessage(content=question)], "steps": 0})

    print()
    print("=== 대화 흐름 ===")
    for m in result["messages"]:
        role = type(m).__name__
        content = m.content if isinstance(m.content, str) else str(m.content)
        print(f"[{role}] {content[:200]}")
