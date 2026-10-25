"""
Knowledge RAG MCP 연동
----------------------
Woori AI Hub 공용 문서 검색 MCP 서버(Knowledge RAG MCP Server)의 Tool을
LangChain Tool로 불러온다.

MCP 서버는 "찾는 일"만 한다. 검색 여부 판단, 질문 재작성, 답변 생성은
에이전트(LLM)의 몫이므로, 여기서는 search_documents Tool과 이 호출자에게
허용된 도메인 목록만 에이전트에 넘긴다.

출처 표시는 LLM에 맡기지 않고 코드로 고정한다:
    1. Tool 결과의 각 문서에 [ref:xxxxxx] 참조를 붙여 LLM에 넘기고,
       문서 라벨은 ToolMessage.artifact에 따로 담아 둔다.
    2. LLM은 답변 끝에 "사용문서: ref, ref"만 적는다.
    3. SourcesMiddleware가 그 줄과 본문의 citation 흔적을 지우고
       마지막 줄에 "출처 : 라벨, 라벨"을 붙인다.

MCP 서버는 별도 팀이 운영하는 외부 서버다. URL과 API Key는 서버 운영 측에서
발급받는다 (이 에이전트를 호출자로 등록하고 허용 도메인을 지정해 달라고 요청).

필요한 .env 값 (RAG_MCP_URL이 없으면 MCP 연동 없이 동작):
    RAG_MCP_URL=https://<MCP 서버 호스트>/mcp
    RAG_MCP_API_KEY=<운영 측에서 발급한 이 에이전트의 API Key>
"""

import logging
import os
import re
from dataclasses import dataclass, field

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger("policy_agent.mcp")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [MCP] %(message)s"))
    logger.addHandler(_handler)

SERVER_NAME = "knowledge_rag"
# list_domains는 에이전트 생성 시 한 번만 호출해 프롬프트에 넣으므로
# LLM에게는 search_documents만 노출한다 (매 질문마다 왕복 1회 절약).
EXPOSED_TOOLS = {"search_documents"}

SOURCES_MARKER = "사용문서:"
_REF_RE = re.compile(r"\[?ref:([0-9a-f]{6})\]?")
# 본문에서 지울 citation 흔적: [ref:xxxxxx], [POL-001], [제2조], [... 제2조 ...]
_INLINE_CITATION_RE = re.compile(r"\s?\[(?:ref:[0-9a-f]{6}|[A-Z]{2,5}-\d{2,4}|[^\[\]\n]*제\d+조[^\[\]\n]*)\]")
_ARTICLE_RE = re.compile(r"제\d+조(의\d+)?")


@dataclass
class RagMcp:
    tools: list[BaseTool] = field(default_factory=list)
    domains: list[dict] = field(default_factory=list)


def _build_client() -> MultiServerMCPClient | None:
    url = os.environ.get("RAG_MCP_URL")
    if not url:
        return None
    headers = {}
    api_key = os.environ.get("RAG_MCP_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return MultiServerMCPClient({
        SERVER_NAME: {
            "transport": "streamable_http",
            "url": url,
            "headers": headers,
        }
    })


def _source_label(chunk: dict) -> str:
    """출처 줄에 보일 문서 라벨.

    조문 citation("제2조")은 단독으로는 어느 규정인지 알 수 없어서
    상위 헤딩(예: "연차휴가 운영규정 (POL-001)")을 앞에 붙인다.
    """
    citation = chunk.get("citation") or ""
    if _ARTICLE_RE.fullmatch(citation):
        doc = (chunk.get("metadata") or {}).get("h2", "")
        return f"{doc} {citation}".strip()
    return citation or chunk.get("doc_id", "")


def _with_sources(mcp_tool: BaseTool, client: MultiServerMCPClient) -> BaseTool:
    """MCP search_documents를 직접 호출해 (LLM용 텍스트, 출처 목록)을 돌려주는 Tool.

    어댑터 Tool은 structuredContent(chunks의 doc_id/citation/metadata)를 넘겨주지 않아
    MCP 세션으로 직접 호출한다. 결과 블록 id(lc_...)가 LLM에 노출되지 않는 효과도 있다.
    """
    async def _run(**kwargs):
        async with client.session(SERVER_NAME) as session:
            result = await session.call_tool(mcp_tool.name, kwargs)
        text = "\n\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")
        if result.isError:
            raise ToolException(text or "문서 검색 중 오류가 발생했습니다.")

        chunks = (result.structuredContent or {}).get("chunks", [])
        if not chunks:
            return "검색 결과가 없습니다.", []
        sources = [{"ref": c["doc_id"][:6], "label": _source_label(c)} for c in chunks]
        context = "\n\n".join(f"[ref:{s['ref']}]\n{c['content']}" for s, c in zip(sources, chunks))
        return context, sources

    return StructuredTool.from_function(
        coroutine=_run,
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema=mcp_tool.args_schema,
        response_format="content_and_artifact",
        handle_tool_error=True,
    )


async def load_rag_mcp() -> RagMcp | None:
    """MCP Tool과 허용 도메인 목록을 불러온다.

    Returns:
        RAG_MCP_URL 미설정이면 None (연동 비활성).

    Raises:
        MCP 서버 연결/인증 실패 시 예외. 호출자가 재시도 여부를 정한다.
    """
    client = _build_client()
    if client is None:
        return None

    async with client.session(SERVER_NAME) as session:
        result = await session.call_tool("list_domains", {})
    domains = [
        d for d in (result.structuredContent or {}).get("domains", [])
        if d.get("status", "active") == "active"
    ]

    tools = [_with_sources(t, client) for t in await client.get_tools() if t.name in EXPOSED_TOOLS]
    logger.info(
        "MCP 연결됨: tools=%s domains=%s",
        [t.name for t in tools], [d.get("id") for d in domains],
    )
    return RagMcp(tools=tools, domains=domains)


def _content_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return str(content)


def format_sources(text: str, sources: dict[str, str]) -> str:
    """LLM 답변에서 citation 흔적을 지우고 마지막 줄에 출처를 붙인다.

    Args:
        text: LLM의 최종 답변.
        sources: 이번 턴에 검색된 문서의 {ref: 라벨}.
    """
    used_refs = [r for r in _REF_RE.findall(text) if r in sources]

    lines = [
        line for line in text.splitlines()
        if not line.strip().lstrip("*_ ").startswith((SOURCES_MARKER, "출처"))
    ]
    body = _INLINE_CITATION_RE.sub("", "\n".join(lines))
    body = _REF_RE.sub("", body).rstrip()

    labels = _group_articles(list(dict.fromkeys(sources[r] for r in used_refs)))
    if not labels:
        return body
    return f"{body}\n\n출처 : {', '.join(labels)}"


def _group_articles(labels: list[str]) -> list[str]:
    """같은 규정의 조항을 한 라벨로 묶는다.

    ["연차휴가 운영규정 (POL-001) 제2조", "연차휴가 운영규정 (POL-001) 제1조"]
    -> ["연차휴가 운영규정 (POL-001) 제1조·제2조"]
    """
    grouped: dict[str, list[str]] = {}
    for label in labels:
        m = re.match(r"^(.*\S)\s+(제(\d+)조(?:의\d+)?)$", label)
        doc, article = (m.group(1), m.group(2)) if m else (label, "")
        grouped.setdefault(doc, [])
        if article:
            grouped[doc].append(article)

    def article_no(a: str) -> int:
        return int(re.search(r"\d+", a).group())

    return [
        f"{doc} {'·'.join(sorted(set(arts), key=article_no))}" if arts else doc
        for doc, arts in grouped.items()
    ]


class SourcesMiddleware(AgentMiddleware):
    """에이전트 종료 시 최종 답변의 출처 표시를 고정 형식으로 바꾼다."""

    def after_agent(self, state, runtime):
        messages = state["messages"]
        last = messages[-1] if messages else None
        if not isinstance(last, AIMessage) or last.tool_calls:
            return None

        # 이번 턴(마지막 사용자 메시지 이후)에 검색된 문서만 출처 후보로 쓴다.
        sources: dict[str, str] = {}
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                break
            if isinstance(m, ToolMessage) and isinstance(m.artifact, list):
                for s in m.artifact:
                    sources.setdefault(s["ref"], s["label"])

        original = _content_text(last.content)
        fixed = format_sources(original, sources)
        if fixed == original:
            return None
        # 같은 id로 돌려주면 add_messages가 기존 메시지를 교체한다.
        return {"messages": [last.model_copy(update={"content": fixed})]}


def build_rag_prompt(domains: list[dict]) -> str:
    """시스템 프롬프트 뒤에 붙일 RAG 사용 안내."""
    if not domains:
        return ""
    domain_lines = "\n".join(f"- `{d['id']}`: {d.get('description', '')}" for d in domains)
    return f"""

## 사내 문서 검색 (search_documents) — 최우선 도구

사내 업무, 규정, 조직, IT 가이드에 관한 질문은 **가장 먼저 `search_documents`로 검색**합니다.
위 "탐색" 단계의 다른 도구보다 이 도구가 우선합니다. `domain`에는 아래 id 중 하나를 넣습니다.

{domain_lines}

도구 사용 순서:
1. `search_documents`로 질문의 핵심 내용을 검색합니다.
2. 검색 결과가 비어 있거나 질문에 답하기에 부족할 때만 내장 도구
   (`search_policy`, `search_job`, `search_portal_by_keyword` 등)로 보완합니다.
3. 상황 기반 추천(관련 후속 업무)이 필요할 때는 `get_all_job`이나 `search_job`을 추가로 사용할 수 있습니다.

답변 규칙:
- 검색 결과의 각 문서는 `[ref:xxxxxx]`로 시작합니다. 문서 내용을 근거로 답변합니다.
- 본문에는 ref, 문서번호, 조항 번호 같은 출처 표시를 괄호로 붙이지 않습니다. "출처" 줄도 직접 쓰지 않습니다.
- 답변의 맨 마지막 줄에 실제로 근거로 사용한 문서의 ref만 적습니다.
  형식: `{SOURCES_MARKER} ref:1a2b3c, ref:4d5e6f`
  이 줄은 시스템이 출처 표시로 자동 변환합니다. 검색 결과 중 사용하지 않은 문서는 적지 않습니다.
- 문서와 내장 도구 결과가 서로 다르면 문서(`search_documents`) 내용을 따릅니다.
- 문서를 사용하지 않은 답변에는 `{SOURCES_MARKER}` 줄을 쓰지 않습니다.
- 어느 쪽에서도 찾지 못하면 찾지 못했다고 안내하고, 추측으로 답하지 않습니다.
"""
