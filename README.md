# 사내 포탈 업무 도우미 Agent Tutorial

LangGraph V1.0을 사용하여 **사내 포탈 업무 도우미(Internal Portal Assistant)** 를 구축하는 방법을 배우는 교육용 프로젝트입니다.

## 학습 목표

이 튜토리얼을 통해 다음을 학습할 수 있습니다:

- **에이전트 생성**: `create_agent`를 사용한 ReAct 스타일 에이전트 구축
- **도구(Tool) 정의**: `@tool` 데코레이터를 활용한 사내 업무/규정 데이터 조회
- **컨텍스트 관리**: `ToolRuntime`과 `context_schema`로 임직원 정보 전달
- **구조화된 응답**: Pydantic 모델을 사용한 업무 처리 가이드 형식화
- **메모리 관리**: `InMemorySaver`와 `thread_id`로 대화 히스토리 유지
- **멀티에이전트**: Supervisor 패턴으로 역할을 분리한 서브 에이전트 라우팅
- **외부 연동**: Slack Socket Mode 봇으로 사내 메신저에서 바로 질의응답

## 실습 도메인

임직원의 사내 업무 문의에 답하고, 상황에 맞는 후속 업무까지 능동적으로 추천하는
**사내 포탈 업무 도우미** 챗봇을 구현하며, 다음 기능을 포함합니다:

- **업무 안내**: 조직/인사, 근태/휴가, 복리후생, PC/IT환경, 업무시스템, 보안/정보보호 등
  카테고리별 사내 업무 검색 및 신청 절차 안내
- **사내 규정 조회**: 연차, 재택근무, 정보보안, 경조사 지원 등 규정 검색
- **조직도 조회**: 부서별 담당업무 및 연락처 확인
- **IT 환경설정 가이드**: PC 초기설정, VPN, 비밀번호 관리 절차 안내
- **상황 기반 추천**: "부서 이동했어요", "아이가 태어났어요" 같은 상황을 분석해
  함께 확인해야 할 관련 업무를 먼저 제안

---

## 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd langgraph-agent-tutorial
```

### 2. 환경 설정

아래 [환경 설정](#%EF%B8%8F-환경-설정) 섹션을 참고하여 개발 환경을 구성합니다.

### 3. Jupyter Lab 실행

```bash
# 가상 환경 활성화
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Jupyter Lab 실행
jupyter lab
```

브라우저가 자동으로 열리며 튜토리얼 노트북을 선택하여 실행할 수 있습니다.

---

## ⚙️ 환경 설정

### 필수 요구사항

- **Python 3.11 이상**
- **UV 패키지 매니저** (빠르고 효율적인 Python 패키지 관리자)
- **API Keys**:
  - Google AI Studio API Key (필수 — 기본 LLM인 Gemini Flash-Lite 사용)
  - Azure OpenAI / OpenAI API Key (선택사항, 다른 모델 사용 시)
  - LangSmith API Key (선택사항, 추적 기능용)
  - Slack Bot/App Token (선택사항, Slack 봇 사용 시)

### 1단계: UV 설치

UV는 빠르고 효율적인 Python 패키지 관리자입니다.

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**설치 확인:**
```bash
uv --version
```

### 2단계: 가상 환경 생성 및 의존성 설치

```bash
# 1. 가상 환경 생성
uv venv

# 2. 가상 환경 활성화
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 3. 의존성 설치 (uv.lock 기반)
uv sync

# 4. Jupyter 커널 등록
uv run python -m ipykernel install --user --name=langgraph-v1 --display-name="Python (langgraph-v1)"
```

> **💡 참고**: `uv sync` 명령어는 `uv.lock` 파일을 기반으로 모든 의존성을 정확한 버전으로 설치합니다. 팀원 간 동일한 개발 환경을 보장합니다.
>
> **💡 커널 등록**: Jupyter 노트북에서 이 프로젝트의 가상환경을 사용하려면 커널 등록이 필요합니다. 등록 후 노트북에서 `Python (langgraph-v1)` 커널을 선택할 수 있습니다.

### 3단계: 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 API 키를 설정합니다:

**macOS/Linux:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

`.env` 파일을 열어 아래 내용을 설정하세요:

```env
# 필수: Google AI Studio (기본 LLM - Gemini Flash-Lite)
GOOGLE_API_KEY=your-google-api-key

# 선택사항: Azure OpenAI / OpenAI (다른 모델을 사용하고 싶을 때)
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview
OPENAI_API_KEY=your-openai-api-key

# 선택사항: LangSmith (디버깅 및 추적 기능)
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=LangGraph-Tutorial

# 선택사항: Slack 봇 (사내 포탈 에이전트를 Slack에서 사용하고 싶을 때)
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

### 4단계: 설치 검증

가상 환경에서 Python과 주요 패키지가 제대로 설치되었는지 확인:

```bash
# Python 버전 확인 (3.11 이상이어야 함)
python --version

# 주요 패키지 설치 확인
python -c "import langchain, langgraph; print('✅ 설치 완료!')"
```

---

## 프로젝트 구조

```
langgraph-agent-tutorial/
├── src/
│   ├── notebook/
│   │   └── 01-langgraph-agent.ipynb  # 메인 학습 노트북
│   ├── policy_agent/                  # 배포 가능한 사내 포탈 에이전트
│   │   ├── agent.py                   # 에이전트 그래프 정의 (create_agent 기반)
│   │   ├── agent_lowlevel.py          # 동일 로직을 StateGraph로 직접 구현한 버전
│   │   ├── agent_multiagent.py        # Supervisor 패턴 멀티에이전트 버전
│   │   ├── tools.py                   # 도구 함수 정의
│   │   ├── data.py                    # 사내 업무/규정/조직/IT가이드 데이터베이스
│   │   ├── prompts.py                 # 시스템 프롬프트
│   │   └── slack_bot.py               # Slack Socket Mode 봇 (langgraph dev API 호출)
│   └── utils/                         # 유틸리티 함수
│       ├── graphs.py                  # 그래프 시각화
│       ├── messages.py                # 스트리밍 헬퍼
│       └── logging.py                 # LangSmith 설정
├── langgraph.json                     # LangGraph 서버 설정
├── pyproject.toml                     # 프로젝트 의존성
├── uv.lock                            # 의존성 버전 잠금
└── .env.example                       # 환경 변수 템플릿
```

---

## 사용 방법

### 1. Jupyter 노트북으로 학습하기

```bash
# uv run 사용 (가상환경 활성화 없이)
uv run jupyter lab

# 또는 가상환경 활성화 후
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
jupyter lab
```

`src/notebook/01-langgraph-agent.ipynb` 노트북을 열어 단계별로 학습을 진행합니다.

### 2. LangGraph 개발 서버 실행하기

```bash
uv run langgraph dev
```

개발 서버가 시작되면 사내 포탈 에이전트가 로컬에서 실행됩니다.

### 3. Agent Chat으로 테스트하기

1. LangGraph 개발 서버를 실행합니다
2. [https://agentchat.vercel.app](https://agentchat.vercel.app) 에 접속합니다
3. 로컬 서버 URL을 입력하여 에이전트와 대화를 시작합니다

### 4. Slack에서 사용하기

`.env`에 `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`을 설정한 뒤, LangGraph 개발 서버를 먼저 띄우고
Slack 봇을 별도 프로세스로 실행합니다 (봇은 그래프를 직접 실행하지 않고 `langgraph dev` API에 요청만 보냅니다):

```bash
# 1) LangGraph 개발 서버 실행 (그대로 켜둔 상태 유지)
uv run langgraph dev --no-browser

# 2) 다른 터미널에서 Slack 봇 실행
uv run python -m policy_agent.slack_bot
```

Slack 채널에서 봇을 멘션하거나 DM을 보내면 `policy_agent` 그래프가 응답합니다.

---

## 주요 학습 내용

### 모델 초기화
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("google_genai:gemini-flash-lite-latest", temperature=0)
```

### 도구 정의
```python
from langchain_core.tools import tool

@tool
def search_job(category: str) -> str:
    """특정 카테고리의 사내 업무를 조회합니다."""
    ...
```

### 에이전트 생성
```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[search_job, search_policy],
    system_prompt=SYSTEM_PROMPT
)
```

---

## 문제 해결

### UV 명령어를 찾을 수 없는 경우

터미널을 재시작하거나 PATH를 다시 로드하세요:

```bash
# macOS/Linux
source ~/.bashrc  # 또는 ~/.zshrc

# Windows: 터미널 재시작
```

### 가상환경 활성화 오류 (Windows)

PowerShell 실행 정책을 변경해야 할 수 있습니다:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---
