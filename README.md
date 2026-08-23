# LangGraph Agent Tutorial

LangGraph V1.0을 사용하여 AI 에이전트를 구축하는 방법을 배우는 교육용 프로젝트입니다.

## 학습 목표

이 튜토리얼을 통해 다음을 학습할 수 있습니다:

- **에이전트 생성**: `create_react_agent`를 사용한 ReAct 스타일 에이전트 구축
- **도구(Tool) 정의**: `@tool` 데코레이터를 활용한 외부 시스템 연동
- **컨텍스트 관리**: `ToolRuntime`과 `context_schema`로 실행 환경 정보 전달
- **구조화된 응답**: Pydantic 모델을 사용한 일관된 출력 형식
- **메모리 관리**: `InMemorySaver`와 `thread_id`로 대화 히스토리 유지
- **미들웨어**: Human-in-the-Loop 승인 워크플로우 구현

## 실습 도메인

전자상거래 고객 서비스 챗봇을 구현하며, 다음 기능을 포함합니다:
- 상품 검색 및 추천
- 주문 배송 상태 조회
- 고객 프로필 기반 개인화 서비스

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
  - Azure OpenAI API Key (필수)
  - LangSmith API Key (선택사항, 추적 기능용)
  - Tavily API Key (선택사항, 검색 도구용)

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
# 필수: Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview

# 선택사항: LangSmith (디버깅 및 추적 기능)
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=LangGraph-Tutorial

# 선택사항: Tavily (검색 도구)
TAVILY_API_KEY=your-tavily-api-key
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
│   ├── shopping_agent/                # 배포 가능한 쇼핑 에이전트
│   │   ├── agent.py                   # 에이전트 그래프 정의
│   │   ├── tools.py                   # 도구 함수 정의
│   │   ├── data.py                    # 상품/주문 데이터베이스
│   │   └── prompts.py                 # 시스템 프롬프트
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

개발 서버가 시작되면 쇼핑 에이전트가 로컬에서 실행됩니다.

### 3. Agent Chat으로 테스트하기

1. LangGraph 개발 서버를 실행합니다
2. [https://agentchat.vercel.app](https://agentchat.vercel.app) 에 접속합니다
3. 로컬 서버 URL을 입력하여 에이전트와 대화를 시작합니다

---

## 주요 학습 내용

### 모델 초기화
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("azure_openai:gpt-4.1", temperature=0)
```

### 도구 정의
```python
from langchain_core.tools import tool
from typing import Literal

@tool
def search_products(category: Literal["전자기기", "의류", "생활용품"]) -> str:
    """특정 카테고리의 제품을 검색합니다."""
    ...
```

### 에이전트 생성
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[search_products, check_order_status],
    prompt=SYSTEM_PROMPT
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

**Copyright Notice**

본 자료는 교육 목적으로 제작되었습니다. **무단 배포를 금합니다.**
