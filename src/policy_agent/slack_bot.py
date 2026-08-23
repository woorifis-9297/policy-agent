"""
Policy Agent - Slack Bot (API 호출 방식)
--------------------------------------------
이전 버전은 이 프로세스 안에서 create_policy_agent()로 그래프를 직접
컴파일해서 돌렸다. 이번 버전은 그렇게 하지 않는다 - 이 봇은 그래프를
전혀 갖고 있지 않고, langgraph dev API 서버(http://127.0.0.1:2024)에
HTTP로 요청만 보낸다.

그 결과:
    - 실제 그래프 실행은 langgraph dev 프로세스 안에서 일어난다.
    - 툴 실행 로그([TOOL EXECUTED] ...)도 langgraph dev 콘솔에 찍힌다
      (이 봇 콘솔이 아니라).
    - 대화 기록은 langgraph dev 서버가 들고 있으므로, 이 봇을 껐다 켜도
      (심지어 Studio UI에서 같은 스레드로 이어봐도) 대화가 유지된다.

사전 조건: langgraph dev 서버가 떠 있어야 한다.
    uv run langgraph dev --no-browser

필요한 .env 값:
    SLACK_BOT_TOKEN=xoxb-...
    SLACK_APP_TOKEN=xapp-...

실행:
    uv run python -m policy_agent.slack_bot
"""

import logging
import os
import uuid

from dotenv import load_dotenv
from langgraph_sdk import get_sync_client
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("policy_agent.slack")

LANGGRAPH_API_URL = os.environ.get("LANGGRAPH_API_URL", "http://127.0.0.1:2024")
ASSISTANT_ID = "policy_agent"  # langgraph.json에 등록된 graph_id

client = get_sync_client(url=LANGGRAPH_API_URL)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
_bot_user_id = app.client.auth_test()["user_id"]
logger.info("봇 연결됨 (user_id=%s), langgraph API=%s", _bot_user_id, LANGGRAPH_API_URL)

# 같은 Slack 이벤트가 app_mention/message 두 핸들러에 중복으로 잡힐 수 있어
# ts 기준으로 한 번만 처리하도록 막는다.
_processed_ts: set[str] = set()


def _thread_id_for(key: str) -> str:
    """langgraph API의 thread_id는 UUID 형식만 허용한다.
    같은 key는 항상 같은 UUID로 변환되므로, 이 봇을 재시작해도
    같은 Slack 스레드는 계속 같은 서버 측 대화(thread)로 이어진다."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def _strip_mention(text: str) -> str:
    """'<@U12345> VPN 신청 방법 알려줘' -> 'VPN 신청 방법 알려줘'"""
    return " ".join(word for word in text.split() if not word.startswith("<@")).strip()


def _extract_answer(content) -> str:
    """Gemini 응답은 content가 [{'type': 'text', 'text': ...}] 형태일 수 있음."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


def _handle_question(event, say):
    ts = event.get("ts")
    if ts in _processed_ts:
        return
    _processed_ts.add(ts)

    channel = event["channel"]
    thread_ts = event.get("thread_ts", ts)
    question = _strip_mention(event.get("text", ""))

    if not question:
        say(text="궁금하신 사내 업무나 신청번호를 함께 보내주세요!", thread_ts=thread_ts)
        return

    logger.info("요청 수신 [channel=%s thread=%s]: %s", channel, thread_ts, question)

    thread_id = _thread_id_for(f"slack-{channel}-{thread_ts}")
    try:
        result = client.runs.wait(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            input={"messages": [{"role": "human", "content": question}]},
            if_not_exists="create",
        )
    except Exception:
        logger.exception("langgraph API 호출 실패 - 서버(uv run langgraph dev)가 떠 있는지 확인하세요")
        say(text="죄송해요, 지금 답변 서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.", thread_ts=thread_ts)
        return

    answer = _extract_answer(result["messages"][-1]["content"])

    logger.info("응답 전송 [channel=%s thread=%s]: %s", channel, thread_ts, answer[:100])
    say(text=answer, thread_ts=thread_ts)


@app.event("app_mention")
def handle_mention(event, say):
    _handle_question(event, say)


@app.event("message")
def handle_message(event, say):
    # 봇 자신/다른 봇 메시지, 메시지 수정 등은 무시 (무한루프 방지)
    if event.get("bot_id") or event.get("subtype"):
        return

    text = event.get("text", "")
    is_dm = event.get("channel_type") == "im"
    is_mentioned = f"<@{_bot_user_id}>" in text

    # Slack 앱 설정에 app_mention 이벤트가 구독 안 되어 있어도,
    # 채널 멘션/DM이 'message' 이벤트로만 들어오는 경우를 대비한 보험 처리.
    if is_dm or is_mentioned:
        _handle_question(event, say)


@app.event("app_home_opened")
def handle_app_home_opened(event, logger):
    pass  # Home 탭 열람 이벤트는 처리할 필요 없음 - 404 로그 노이즈만 방지


if __name__ == "__main__":
    logger.info("Slack 봇 시작 (Socket Mode, API 모드 -> %s)", LANGGRAPH_API_URL)
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
