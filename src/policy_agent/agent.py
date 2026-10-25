"""
Policy Agent
------------
사내 포탈 업무 도우미를 위한 LangGraph ReAct 에이전트입니다.

이 모듈은 LangGraph의 prebuilt create_agent 함수를 사용하여
사내 포탈 도구를 갖춘 ReAct 스타일 에이전트를 생성합니다.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from policy_agent.tools import PORTAL_TOOLS
from policy_agent.prompts import SYSTEM_PROMPT
from policy_agent.mcp_tools import RagMcp, SourcesMiddleware, build_rag_prompt, load_rag_mcp

# .env 파일에서 환경 변수 로드
load_dotenv(override=True)

logger = logging.getLogger("policy_agent.agent")


def get_llm(model: Optional[str] = None):
    """
    유연한 모델 선택을 지원하며 언어 모델을 초기화합니다.

    Args:
        model: 모델 식별자 문자열. 지정하지 않으면 LLM_MODEL
               환경 변수 또는 기본값 'google_genai:gemini-flash-lite-latest'를 사용합니다.

    Returns:
        초기화된 챗 모델 인스턴스.
    """
    model_name = model or os.environ.get("LLM_MODEL", "google_genai:gemini-flash-lite-latest")
    return init_chat_model(
        model_name,
        temperature=0,
        max_tokens=2000
    )


def create_policy_agent(
    model: Optional[str] = None,
    checkpointer: Optional[InMemorySaver] = None,
    rag: Optional[RagMcp] = None,
):
    """
    도구를 갖춘 사내 포탈 업무 도우미 에이전트를 생성합니다.

    Args:
        model: LLM용 모델 식별자 문자열 (선택).
        checkpointer: 대화 유지를 위한 메모리 체크포인터 (선택).
        rag: load_rag_mcp()로 불러온 MCP Tool/도메인 (선택). 없으면 내장 도구만 사용.

    Returns:
        바로 호출 가능한 컴파일된 LangGraph 에이전트.
    """
    llm = get_llm(model)
    tools = list(PORTAL_TOOLS)
    system_prompt = SYSTEM_PROMPT
    middleware = []
    if rag:
        tools += rag.tools
        system_prompt += build_rag_prompt(rag.domains)
        middleware.append(SourcesMiddleware())

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=middleware,
        checkpointer=checkpointer
    )

    return agent


_graph_cache = None


async def graph():
    """LangGraph 서버용 그래프 팩토리 (langgraph.json의 entry point).

    MCP Tool 로드가 async라서 모듈 import 시점이 아니라 여기서 그래프를 만든다.
    langgraph 서버는 실행(run)마다 이 함수를 호출하므로, MCP 연결에 성공한
    그래프는 캐시해 재사용한다. MCP 서버가 내려가 있으면 내장 도구만으로
    응답하고, 다음 실행에서 다시 연결을 시도한다.
    """
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache

    try:
        rag = await load_rag_mcp()
    except Exception:
        logger.exception("MCP 서버 연결 실패 - 이번 실행은 내장 도구만 사용합니다")
        return create_policy_agent()

    agent = create_policy_agent(rag=rag)
    _graph_cache = agent
    return agent
