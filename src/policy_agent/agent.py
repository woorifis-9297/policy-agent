"""
Policy Agent
------------
사내 포탈 업무 도우미를 위한 LangGraph ReAct 에이전트입니다.

이 모듈은 LangGraph의 prebuilt create_agent 함수를 사용하여
사내 포탈 도구를 갖춘 ReAct 스타일 에이전트를 생성합니다.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from policy_agent.tools import PORTAL_TOOLS
from policy_agent.prompts import SYSTEM_PROMPT

# .env 파일에서 환경 변수 로드
load_dotenv(override=True)


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
    checkpointer: Optional[InMemorySaver] = None
):
    """
    도구를 갖춘 사내 포탈 업무 도우미 에이전트를 생성합니다.

    Args:
        model: LLM용 모델 식별자 문자열 (선택).
        checkpointer: 대화 유지를 위한 메모리 체크포인터 (선택).

    Returns:
        바로 호출 가능한 컴파일된 LangGraph 에이전트.
    """
    llm = get_llm(model)

    agent = create_agent(
        model=llm,
        tools=PORTAL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

    return agent


# LangGraph 서버용 기본 그래프 인스턴스 생성
# langgraph.json에서 entry point로 참조됩니다
graph = create_policy_agent()
