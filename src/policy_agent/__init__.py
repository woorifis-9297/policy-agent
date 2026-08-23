"""
사내 포탈 에이전트 패키지
------------------------------
LangGraph 기반 사내 포탈 업무 도우미 에이전트입니다.

이 패키지는 다음을 처리하는 ReAct 스타일 에이전트를 제공합니다:
- 카테고리/키워드 기반 사내 업무·절차 조회
- 사내 규정 조회
- 조직 정보 조회
- IT 환경설정 가이드 조회

사용법:
    from policy_agent import graph

    # 에이전트 호출
    response = graph.invoke({
        "messages": [{"role": "user", "content": "연차 신청 방법 알려줘"}]
    })

    # 대화 메모리 사용 (thread_id)
    response = graph.invoke(
        {"messages": [{"role": "user", "content": "재택근무 규정도 알려줘"}]},
        config={"configurable": {"thread_id": "session_001"}}
    )
"""

from .agent import graph, create_policy_agent, get_llm
from .tools import (
    get_all_job,
    search_job,
    search_portal_by_keyword,
    search_policy,
    search_organization,
    search_it_guide,
    PORTAL_TOOLS
)
from .data import INTERNAL_JOB_DB, POLICY_DB, ORGANIZATION_DB, IT_GUIDE_DB, CATEGORIES
from .prompts import SYSTEM_PROMPT

__all__ = [
    # 메인 그래프 export (langgraph.json 참조용)
    "graph",
    # 에이전트 팩토리 함수
    "create_policy_agent",
    "get_llm",
    # 도구 (ReAct 데이터 기반 패턴)
    "get_all_job",
    "search_job",
    "search_portal_by_keyword",
    "search_policy",
    "search_organization",
    "search_it_guide",
    "PORTAL_TOOLS",
    # 데이터
    "INTERNAL_JOB_DB",
    "POLICY_DB",
    "ORGANIZATION_DB",
    "IT_GUIDE_DB",
    "CATEGORIES",
    # 프롬프트
    "SYSTEM_PROMPT",
]
