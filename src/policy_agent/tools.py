"""
사내 포탈 에이전트 도구
----------------------------
사내 포탈 업무 도우미를 위한 데이터 기반 도구 정의입니다.

이 모듈은 도구가 원본 데이터만 제공하고 LLM이 해당 데이터를 추론하여
관련 업무, 규정, 조직 정보, IT 가이드를 추천하는 진짜 ReAct 패턴을 구현합니다.
"""

import logging
from typing import List
from langchain_core.tools import tool

from policy_agent.data import (
    INTERNAL_JOB_DB,
    POLICY_DB,
    ORGANIZATION_DB,
    IT_GUIDE_DB,
    CATEGORIES,
)

logger = logging.getLogger("policy_agent.tools")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [TOOL] %(message)s"))
    logger.addHandler(_handler)


@tool
def get_all_job() -> str:
    """전체 사내 업무 카탈로그를 조회합니다.

    모든 카테고리의 전체 업무 목록을 반환합니다.
    LLM이 전체 업무를 파악하고 사용자 상황에 맞는 업무를 직접 선택할 수 있습니다.

    Returns:
        전체 카테고리별 업무 목록 (업무명, 설명, 담당부서 포함)
    """
    logger.info("[TOOL EXECUTED] get_all_job()")
    result = "=== 전체 사내 업무 카탈로그 ===\n\n"

    for category, jobs in INTERNAL_JOB_DB.items():
        result += f"【{category}】\n"
        for j in jobs:
            result += f"  - {j['name']} ({j['department']}): {j['description']}\n"
        result += "\n"

    result += f"총 {sum(len(jobs) for jobs in INTERNAL_JOB_DB.values())}개 업무"
    return result


@tool
def search_job(category: str) -> str:
    """특정 카테고리의 사내 업무를 조회합니다.

    지정된 카테고리의 모든 업무 정보를 반환합니다.
    LLM이 카테고리 내 업무들을 분석하여 사용자에게 적합한 업무를 안내할 수 있습니다.

    Args:
        category: 조회할 업무 카테고리 (예: 조직/인사, 근태/휴가, 복리후생, 급여/보상,
            PC/IT환경, 업무시스템, 보안/정보보호, 교육/역량개발, 출장/업무지원)

    Returns:
        해당 카테고리의 업무 목록 (업무명, 설명, 담당부서, 대상, 필요서류, 처리절차 포함)
    """
    logger.info("[TOOL EXECUTED] search_job(category=%s)", category)
    jobs = INTERNAL_JOB_DB.get(category, [])

    if not jobs:
        return f"'{category}' 카테고리에 등록된 업무가 없습니다. 사용 가능한 카테고리: {', '.join(CATEGORIES)}"

    result = f"【{category}】 카테고리 업무 목록:\n\n"
    for j in jobs:
        result += f"- {j['name']}\n"
        result += f"  설명: {j['description']}\n"
        result += f"  담당부서: {j['department']}\n"
        result += f"  대상: {j['target']}\n"
        if j["required_documents"]:
            result += f"  필요서류: {', '.join(j['required_documents'])}\n"
        result += f"  처리절차: {j['procedure']}\n\n"

    return result


@tool
def search_portal_by_keyword(keyword: str) -> str:
    """키워드로 전체 사내 업무에서 관련 업무를 검색합니다.

    입력된 키워드가 업무명, 설명 또는 키워드 목록에 포함된 모든 업무를 검색합니다.
    LLM이 검색 결과를 분석하여 사용자 상황에 맞는 업무를 선택할 수 있습니다.

    Args:
        keyword: 검색할 키워드 (예: "연차", "출산", "VPN", "비밀번호")

    Returns:
        키워드가 포함된 업무 목록 (카테고리, 업무명, 설명, 담당부서 포함)
    """
    logger.info("[TOOL EXECUTED] search_portal_by_keyword(keyword=%s)", keyword)
    results = []
    keyword_lower = keyword.lower()

    for category, jobs in INTERNAL_JOB_DB.items():
        for j in jobs:
            haystack = [j["name"], j["description"], *j["keywords"]]
            if any(keyword_lower in text.lower() for text in haystack):
                results.append({"category": category, **j})

    if not results:
        return f"'{keyword}' 키워드로 검색된 업무가 없습니다."

    result = f"'{keyword}' 검색 결과:\n\n"
    for item in results:
        result += f"- {item['name']} [{item['category']}]\n"
        result += f"  설명: {item['description']}\n"
        result += f"  담당부서: {item['department']}\n"
        result += f"  처리절차: {item['procedure']}\n\n"

    result += f"총 {len(results)}건 검색됨"
    return result


@tool
def search_policy(keyword: str) -> str:
    """키워드로 사내 규정 및 정책을 검색합니다.

    입력된 키워드가 규정 제목, 요약 또는 키워드 목록에 포함된 규정을 검색합니다.
    휴가, 재택근무, 보안, 경조사, PC 이용 등 사내 규정 관련 질문에 사용합니다.

    Args:
        keyword: 검색할 키워드 (예: "연차", "재택근무", "보안", "경조사")

    Returns:
        키워드와 관련된 규정 목록 (제목, 카테고리, 요약, 상세내용, 적용대상 포함)
    """
    logger.info("[TOOL EXECUTED] search_policy(keyword=%s)", keyword)
    keyword_lower = keyword.lower()
    results = []

    for p in POLICY_DB:
        haystack = [p["title"], p["summary"], *p["keywords"]]
        if any(keyword_lower in text.lower() for text in haystack):
            results.append(p)

    if not results:
        return f"'{keyword}' 키워드와 관련된 사내 규정을 찾을 수 없습니다. 정확한 확인을 위해 담당 부서에 문의해 주세요."

    result = f"'{keyword}' 관련 규정 검색 결과:\n\n"
    for p in results:
        result += f"- {p['title']} [{p['category']}]\n"
        result += f"  요약: {p['summary']}\n"
        result += f"  상세: {p['details']}\n"
        result += f"  적용대상: {p['target']}\n\n"

    return result


@tool
def search_organization(keyword: str) -> str:
    """키워드로 조직 정보를 검색합니다.

    부서명, 상위부서, 담당업무 등을 기준으로 조직 정보를 검색합니다.
    특정 부서의 담당 업무나 연락처를 확인해야 할 때 사용합니다.

    Args:
        keyword: 검색할 키워드 (예: "인사팀", "IT지원팀", "채용")

    Returns:
        일치하는 부서 정보 (상위부서, 설명, 담당업무, 연락처 포함)
    """
    logger.info("[TOOL EXECUTED] search_organization(keyword=%s)", keyword)
    keyword_lower = keyword.lower()
    results: List[dict] = []

    for org in ORGANIZATION_DB:
        haystack = [org["department"], org["parent_department"], org["description"], *org["responsibilities"]]
        if any(keyword_lower in text.lower() for text in haystack):
            results.append(org)

    if not results:
        return f"'{keyword}'와 관련된 부서 정보를 찾을 수 없습니다."

    result = f"'{keyword}' 조직 검색 결과:\n\n"
    for org in results:
        result += f"- {org['department']} (상위부서: {org['parent_department']})\n"
        result += f"  설명: {org['description']}\n"
        result += f"  담당업무: {', '.join(org['responsibilities'])}\n"
        result += f"  연락처: {org['contact']}\n\n"

    return result


@tool
def search_it_guide(keyword: str) -> str:
    """키워드로 IT 환경설정 가이드를 검색합니다.

    PC 초기설정, VPN, 비밀번호 등 IT 환경설정 절차를 안내할 때 사용합니다.

    Args:
        keyword: 검색할 키워드 (예: "PC", "VPN", "비밀번호")

    Returns:
        일치하는 IT 가이드 목록 (제목, 설명, 절차, 문의처 포함)
    """
    logger.info("[TOOL EXECUTED] search_it_guide(keyword=%s)", keyword)
    keyword_lower = keyword.lower()
    results = []

    for guide in IT_GUIDE_DB:
        haystack = [guide["title"], guide["description"], *guide["keywords"]]
        if any(keyword_lower in text.lower() for text in haystack):
            results.append(guide)

    if not results:
        return f"'{keyword}'와 관련된 IT 가이드를 찾을 수 없습니다."

    result = f"'{keyword}' IT 가이드 검색 결과:\n\n"
    for guide in results:
        result += f"- {guide['title']}\n"
        result += f"  설명: {guide['description']}\n"
        result += "  절차:\n"
        for i, step in enumerate(guide["procedure"], 1):
            result += f"    {i}. {step}\n"
        result += f"  문의처: {guide['contact']}\n\n"

    return result


# import 편의를 위해 전체 도구를 리스트로 export
PORTAL_TOOLS = [
    get_all_job,
    search_job,
    search_portal_by_keyword,
    search_policy,
    search_organization,
    search_it_guide,
]
