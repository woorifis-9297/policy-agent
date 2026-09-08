"""
Policy Agent - Web Chat Proxy (API 호출 방식)
--------------------------------------------
slack_bot.py와 같은 패턴이다: 이 서버는 그래프를 전혀 갖지 않는다.
떠 있는 langgraph dev API 서버(기본 http://127.0.0.1:2024)에 HTTP로만
요청을 보내고, 그 결과를 웹페이지 챗봇이 쓰기 쉬운 형태(JSON / SSE)로
중계한다.

역할 분리:
    웹페이지(프론트)
      --(fetch: POST /chat 또는 /chat/stream)-->
    이 프록시(FastAPI, 기본 :8000)
      --(langgraph_sdk)-->
    langgraph dev API 서버(:2024) --> 실제 그래프 실행

이렇게 나누는 이유:
    - 프론트가 langgraph 서버에 직접 붙으면 CORS/인증/API 키 노출 문제가 생긴다.
    - 이 프록시가 사내 인증, 로깅, 요청 검증 등을 얹을 수 있는 지점이 된다.
    - 대화 기록은 langgraph dev 서버가 thread_id 기준으로 들고 있으므로,
      이 프록시를 재시작해도 대화가 끊기지 않는다.

사전 조건: langgraph dev 서버가 떠 있어야 한다.
    uv run langgraph dev --no-browser

실행:
    uv run uvicorn policy_agent.web_api:app --app-dir src --reload --port 8000

필요한 .env 값 (선택, 기본값 있음):
    LANGGRAPH_API_URL=http://127.0.0.1:2024
    WEB_CHAT_ALLOWED_ORIGINS=http://localhost:5500,https://portal.example.com
"""

import json
import logging
import os
import uuid
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langgraph_sdk import get_client
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("policy_agent.web_api")

LANGGRAPH_API_URL = os.environ.get("LANGGRAPH_API_URL", "http://127.0.0.1:2024")
ASSISTANT_ID = "policy_agent"  # langgraph.json에 등록된 graph_id

_allowed_origins = [
    origin.strip()
    for origin in os.environ.get("WEB_CHAT_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if not _allowed_origins:
    # 데모/로컬 개발용 기본값. 운영 배포 시에는 반드시
    # WEB_CHAT_ALLOWED_ORIGINS에 실제 웹페이지 origin을 지정할 것.
    _allowed_origins = ["http://localhost:5500", "http://127.0.0.1:5500"]

client = get_client(url=LANGGRAPH_API_URL)

app = FastAPI(title="Policy Agent Web Chat Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/demo", StaticFiles(directory=_static_dir, html=True), name="demo")


class ChatRequest(BaseModel):
    session_id: str  # 웹페이지가 브라우저(localStorage 등)에 저장해두는 대화 식별자
    message: str


def _thread_id_for(session_id: str) -> str:
    """langgraph API의 thread_id는 UUID 형식만 허용한다.
    같은 session_id는 항상 같은 UUID로 변환되므로, 프론트가 저장해둔
    session_id만 계속 보내면 서버 재시작과 무관하게 대화가 이어진다."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"web-{session_id}"))


def _extract_text(content) -> str:
    """Gemini 등 일부 모델은 content가 [{'type': 'text', 'text': ...}] 형태일 수 있음."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


@app.get("/health")
async def health():
    return {"status": "ok", "langgraph_api_url": LANGGRAPH_API_URL}


@app.get("/history")
async def history(session_id: str):
    """새로고침 후 화면을 채우기 위한 이전 대화 조회.

    새로고침해도 서버(langgraph dev)의 체크포인터에는 대화가 남아있지만,
    데모 페이지는 이걸 화면에 다시 그려주지 않으면 매번 빈 화면으로 보인다.
    thread가 아직 없는 새 세션이면 빈 목록을 돌려준다.
    """
    thread_id = _thread_id_for(session_id)
    try:
        state = await client.threads.get_state(thread_id)
    except Exception:
        return {"messages": [], "thread_id": thread_id}

    messages = state.get("values", {}).get("messages", [])
    result = []
    for msg in messages:
        msg_type = msg.get("type")
        role = "user" if msg_type == "human" else "bot" if msg_type == "ai" else None
        if role is None:
            continue
        text = _extract_text(msg.get("content"))
        if text:
            result.append({"role": role, "text": text})
    return {"messages": result, "thread_id": thread_id}


@app.post("/chat")
async def chat(req: ChatRequest):
    """스트리밍이 필요 없는 단순 요청-응답 방식."""
    thread_id = _thread_id_for(req.session_id)
    try:
        result = await client.runs.wait(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            input={"messages": [{"role": "human", "content": req.message}]},
            if_not_exists="create",
        )
    except Exception:
        logger.exception("langgraph API 호출 실패 - 서버(uv run langgraph dev)가 떠 있는지 확인하세요")
        raise HTTPException(status_code=502, detail="에이전트 서버에 연결할 수 없습니다.")

    answer = _extract_text(result["messages"][-1]["content"])
    return {"answer": answer, "thread_id": thread_id}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """웹페이지 챗봇용 SSE 스트리밍 엔드포인트.

    프론트는 fetch로 이 엔드포인트를 호출한 뒤 응답 본문을
    text/event-stream으로 읽으면 된다 (EventSource는 GET만 지원하므로
    POST 바디가 필요한 여기서는 쓸 수 없다 - src/policy_agent/static/index.html 참고).

    이벤트 종류:
        token: {"text": "..."}  - 지금까지 생성된 답변 전체 텍스트(누적값).
                                   LangGraph API가 매번 "누적된 메시지"를 보내주므로
                                   프론트는 append가 아니라 replace로 렌더링해야 한다.
        done:  {"thread_id": "..."} - 정상 종료
        error: {"message": "..."} - 에러 발생
    """
    thread_id = _thread_id_for(req.session_id)

    async def event_generator() -> AsyncIterator[dict]:
        try:
            async for part in client.runs.stream(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID,
                input={"messages": [{"role": "human", "content": req.message}]},
                stream_mode="messages",
                if_not_exists="create",
            ):
                if part.event not in ("messages/partial", "messages/complete"):
                    continue
                data = part.data
                message = data[0] if isinstance(data, list) and data else None
                if not isinstance(message, dict) or message.get("type") != "ai":
                    continue
                text = _extract_text(message.get("content"))
                if text:
                    yield {"event": "token", "data": json.dumps({"text": text})}
            yield {"event": "done", "data": json.dumps({"thread_id": thread_id})}
        except Exception:
            logger.exception("스트리밍 중 오류 [thread=%s]", thread_id)
            yield {
                "event": "error",
                "data": json.dumps({"message": "에이전트 서버 오류가 발생했습니다."}),
            }

    return EventSourceResponse(event_generator())
