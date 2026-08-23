"""
사내 포탈 데이터베이스
---------------------------------
사내 규정, 조직, IT 환경, 인사, 복리후생, 근태 등
사내 포탈 도우미가 사용하는 가상의 업무 데이터입니다.

이 가상 데이터베이스는 LangGraph 도구를 통해 조회되도록 설계되었으며,
추후 Agent의 비즈니스 로직 변경 없이 RAG 기반 조회로 대체할 수 있습니다.
"""

from typing import TypedDict, List


# ============================================================
# 데이터 스키마
# ============================================================

class InternalJob(TypedDict):
    """사내 업무 정보 스키마."""

    job_id: str
    name: str
    description: str
    category: str
    department: str
    target: str
    required_documents: List[str]
    procedure: str
    keywords: List[str]


class Policy(TypedDict):
    """사내 규정 정보 스키마."""

    policy_id: str
    title: str
    category: str
    summary: str
    details: str
    target: str
    keywords: List[str]


class Organization(TypedDict):
    """조직 정보 스키마."""

    department: str
    parent_department: str
    description: str
    responsibilities: List[str]
    contact: str


class ITGuide(TypedDict):
    """IT 환경설정 가이드 스키마."""

    title: str
    category: str
    description: str
    procedure: List[str]
    contact: str
    keywords: List[str]


# ============================================================
# 사내 업무 데이터베이스
# ============================================================

INTERNAL_JOB_DB: dict[str, List[InternalJob]] = {

    # --------------------------------------------------------
    # 조직 / 인사
    # --------------------------------------------------------
    "조직/인사": [

        {
            "job_id": "HR-001",
            "name": "인사발령 조회",
            "description": "본인의 인사발령 내역 및 발령일자를 조회합니다.",
            "category": "조직/인사",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 인사 > 인사발령 조회",
            "keywords": ["인사발령", "부서이동", "전보", "승진", "발령"]
        },

        {
            "job_id": "HR-002",
            "name": "조직도 조회",
            "description": "회사 전체 조직 및 부서별 구성원을 조회합니다.",
            "category": "조직/인사",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 조직도",
            "keywords": ["조직도", "부서", "팀", "구성원", "담당자"]
        },

        {
            "job_id": "HR-003",
            "name": "인사정보 변경",
            "description": "주소, 연락처 등 개인 인사정보를 변경합니다.",
            "category": "조직/인사",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": ["변경 증빙자료"],
            "procedure": "포탈 > 인사 > 개인정보 변경",
            "keywords": ["인사정보", "주소변경", "전화번호", "개인정보"]
        },

        {
            "job_id": "HR-004",
            "name": "부서 이동에 따른 업무 변경",
            "description": "부서 이동 시 신규 부서 업무 수행에 필요한 정보를 확인합니다.",
            "category": "조직/인사",
            "department": "인사팀",
            "target": "부서 이동 임직원",
            "required_documents": [],
            "procedure": "인사발령 확인 후 신규 부서 담당자에게 업무 인수인계 진행",
            "keywords": ["부서이동", "전보", "업무변경", "인수인계"]
        },
    ],


    # --------------------------------------------------------
    # 근태 / 휴가
    # --------------------------------------------------------
    "근태/휴가": [

        {
            "job_id": "ATT-001",
            "name": "연차 신청",
            "description": "연차휴가를 신청합니다.",
            "category": "근태/휴가",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 근태 > 휴가신청 > 연차 선택",
            "keywords": ["연차", "휴가", "연차신청"]
        },

        {
            "job_id": "ATT-002",
            "name": "반차/반반차 신청",
            "description": "반차 또는 반반차 휴가를 신청합니다.",
            "category": "근태/휴가",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 근태 > 휴가신청",
            "keywords": ["반차", "반반차", "휴가"]
        },

        {
            "job_id": "ATT-003",
            "name": "재택근무 신청",
            "description": "재택근무 대상자는 재택근무를 신청할 수 있습니다.",
            "category": "근태/휴가",
            "department": "인사팀",
            "target": "재택근무 대상자",
            "required_documents": [],
            "procedure": "포탈 > 근태 > 근무형태 신청 > 재택근무",
            "keywords": ["재택", "재택근무", "근무형태"]
        },

        {
            "job_id": "ATT-004",
            "name": "출장 신청",
            "description": "국내외 출장 시 출장 신청 및 결재를 진행합니다.",
            "category": "근태/휴가",
            "department": "총무팀",
            "target": "출장자",
            "required_documents": ["출장계획서"],
            "procedure": "포탈 > 출장 > 출장신청",
            "keywords": ["출장", "출장신청", "국내출장", "해외출장"]
        },
    ],


    # --------------------------------------------------------
    # 복리후생
    # --------------------------------------------------------
    "복리후생": [

        {
            "job_id": "WEL-001",
            "name": "복지포인트 사용",
            "description": "연간 지급된 복지포인트의 잔액 및 사용내역을 조회합니다.",
            "category": "복리후생",
            "department": "총무팀",
            "target": "복지포인트 지급 대상자",
            "required_documents": [],
            "procedure": "포탈 > 복리후생 > 복지포인트",
            "keywords": ["복지포인트", "복지", "포인트"]
        },

        {
            "job_id": "WEL-002",
            "name": "건강검진 신청",
            "description": "임직원 건강검진을 신청합니다.",
            "category": "복리후생",
            "department": "총무팀",
            "target": "건강검진 대상자",
            "required_documents": [],
            "procedure": "포탈 > 복리후생 > 건강검진",
            "keywords": ["건강검진", "검진", "병원"]
        },

        {
            "job_id": "WEL-003",
            "name": "경조금 신청",
            "description": "결혼, 출산, 조의 등 경조사 발생 시 경조금을 신청합니다.",
            "category": "복리후생",
            "department": "총무팀",
            "target": "경조사 발생 임직원",
            "required_documents": ["경조사 증빙서류"],
            "procedure": "포탈 > 복리후생 > 경조금 신청",
            "keywords": ["경조금", "결혼", "출산", "조의", "경조사"]
        },

        {
            "job_id": "WEL-004",
            "name": "경조휴가 신청",
            "description": "결혼, 출산, 가족 경조사 등에 따른 휴가를 신청합니다.",
            "category": "복리후생",
            "department": "인사팀",
            "target": "경조휴가 대상자",
            "required_documents": ["경조사 증빙서류"],
            "procedure": "포탈 > 근태 > 경조휴가 신청",
            "keywords": ["경조휴가", "결혼휴가", "출산휴가", "조의"]
        },
    ],


    # --------------------------------------------------------
    # 급여 / 보상
    # --------------------------------------------------------
    "급여/보상": [

        {
            "job_id": "PAY-001",
            "name": "급여명세서 조회",
            "description": "월별 급여명세서를 조회합니다.",
            "category": "급여/보상",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 급여 > 급여명세서",
            "keywords": ["급여", "급여명세서", "월급", "급여조회"]
        },

        {
            "job_id": "PAY-002",
            "name": "연말정산 자료 조회",
            "description": "연말정산 관련 자료 및 제출 일정을 확인합니다.",
            "category": "급여/보상",
            "department": "인사팀",
            "target": "전 임직원",
            "required_documents": ["연말정산 증빙자료"],
            "procedure": "포탈 > 급여 > 연말정산",
            "keywords": ["연말정산", "소득공제", "세액공제"]
        },
    ],


    # --------------------------------------------------------
    # PC / IT 환경
    # --------------------------------------------------------
    "PC/IT환경": [

        {
            "job_id": "IT-001",
            "name": "PC 초기 설정",
            "description": "신규 PC 지급 후 회사 표준 환경을 설정합니다.",
            "category": "PC/IT환경",
            "department": "IT지원팀",
            "target": "신규 PC 지급자",
            "required_documents": [],
            "procedure": "PC 로그인 > 표준 프로그램 설치 > 보안 프로그램 확인",
            "keywords": ["PC", "컴퓨터", "초기설정", "신규PC"]
        },

        {
            "job_id": "IT-002",
            "name": "VPN 접속 신청",
            "description": "외부에서 사내 시스템에 접속하기 위한 VPN 사용을 신청합니다.",
            "category": "PC/IT환경",
            "department": "IT지원팀",
            "target": "VPN 사용 대상자",
            "required_documents": ["VPN 사용 신청서"],
            "procedure": "포탈 > IT서비스 > VPN 신청",
            "keywords": ["VPN", "외부접속", "원격접속"]
        },

        {
            "job_id": "IT-003",
            "name": "업무용 프로그램 설치",
            "description": "업무 수행에 필요한 표준 프로그램을 설치합니다.",
            "category": "PC/IT환경",
            "department": "IT지원팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "사내 소프트웨어 센터에서 프로그램 선택 후 설치",
            "keywords": ["프로그램", "소프트웨어", "설치", "Office"]
        },

        {
            "job_id": "IT-004",
            "name": "PC 장애 접수",
            "description": "PC 및 주변기기 장애를 IT지원팀에 접수합니다.",
            "category": "PC/IT환경",
            "department": "IT지원팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > IT서비스 > 장애접수",
            "keywords": ["PC장애", "컴퓨터오류", "프린터", "장애"]
        },
    ],


    # --------------------------------------------------------
    # 업무시스템 / 권한
    # --------------------------------------------------------
    "업무시스템": [

        {
            "job_id": "SYS-001",
            "name": "업무시스템 권한 신청",
            "description": "업무 수행에 필요한 시스템 접근권한을 신청합니다.",
            "category": "업무시스템",
            "department": "IT지원팀",
            "target": "업무시스템 사용 대상자",
            "required_documents": [],
            "procedure": "포탈 > IT서비스 > 시스템 권한 신청",
            "keywords": ["권한", "시스템권한", "접근권한", "업무시스템"]
        },

        {
            "job_id": "SYS-002",
            "name": "그룹웨어 권한 신청",
            "description": "전자결재 및 그룹웨어 기능에 필요한 권한을 신청합니다.",
            "category": "업무시스템",
            "department": "IT지원팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > IT서비스 > 그룹웨어 권한",
            "keywords": ["그룹웨어", "전자결재", "결재권한"]
        },

        {
            "job_id": "SYS-003",
            "name": "공유폴더 접근권한 신청",
            "description": "부서 및 업무별 공유폴더 접근권한을 신청합니다.",
            "category": "업무시스템",
            "department": "IT지원팀",
            "target": "공유폴더 사용 대상자",
            "required_documents": [],
            "procedure": "포탈 > IT서비스 > 공유폴더 권한",
            "keywords": ["공유폴더", "폴더권한", "파일서버", "접근권한"]
        },
    ],


    # --------------------------------------------------------
    # 보안 / 정보보호
    # --------------------------------------------------------
    "보안/정보보호": [

        {
            "job_id": "SEC-001",
            "name": "비밀번호 변경",
            "description": "사내 계정 비밀번호를 변경합니다.",
            "category": "보안/정보보호",
            "department": "정보보안팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 보안 > 비밀번호 변경",
            "keywords": ["비밀번호", "패스워드", "계정"]
        },

        {
            "job_id": "SEC-002",
            "name": "보안사고 신고",
            "description": "악성메일, 정보유출, 분실 등 보안사고를 신고합니다.",
            "category": "보안/정보보호",
            "department": "정보보안팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 보안 > 보안사고 신고",
            "keywords": ["보안사고", "정보유출", "악성메일", "피싱", "분실"]
        },

        {
            "job_id": "SEC-003",
            "name": "외부 저장매체 사용 신청",
            "description": "업무상 필요한 경우 USB 등 외부 저장매체 사용을 신청합니다.",
            "category": "보안/정보보호",
            "department": "정보보안팀",
            "target": "업무상 사용 필요자",
            "required_documents": ["사용 사유"],
            "procedure": "포탈 > 보안 > 저장매체 사용 신청",
            "keywords": ["USB", "외장하드", "저장매체", "보안"]
        },
    ],


    # --------------------------------------------------------
    # 교육 / 역량개발
    # --------------------------------------------------------
    "교육/역량개발": [

        {
            "job_id": "EDU-001",
            "name": "필수교육 수강",
            "description": "법정 및 사내 필수교육을 조회하고 수강합니다.",
            "category": "교육/역량개발",
            "department": "인재개발팀",
            "target": "교육 대상 임직원",
            "required_documents": [],
            "procedure": "포탈 > 교육 > 필수교육",
            "keywords": ["교육", "필수교육", "법정교육"]
        },

        {
            "job_id": "EDU-002",
            "name": "직무교육 신청",
            "description": "직무 역량 향상을 위한 교육을 신청합니다.",
            "category": "교육/역량개발",
            "department": "인재개발팀",
            "target": "전 임직원",
            "required_documents": [],
            "procedure": "포탈 > 교육 > 직무교육 신청",
            "keywords": ["직무교육", "교육신청", "역량개발"]
        },
    ],


    # --------------------------------------------------------
    # 출장 / 업무지원
    # --------------------------------------------------------
    "출장/업무지원": [

        {
            "job_id": "TRV-001",
            "name": "법인카드 사용내역 조회",
            "description": "업무용 법인카드의 사용내역을 조회합니다.",
            "category": "출장/업무지원",
            "department": "재무팀",
            "target": "법인카드 사용자",
            "required_documents": [],
            "procedure": "포탈 > 경비 > 법인카드 사용내역",
            "keywords": ["법인카드", "카드사용", "사용내역"]
        },

        {
            "job_id": "TRV-002",
            "name": "출장비 정산",
            "description": "출장 종료 후 출장비를 정산합니다.",
            "category": "출장/업무지원",
            "department": "재무팀",
            "target": "출장자",
            "required_documents": ["영수증", "출장 증빙"],
            "procedure": "포탈 > 경비 > 출장비 정산",
            "keywords": ["출장비", "정산", "영수증", "경비"]
        },
    ],
}


# ============================================================
# 사내 규정 데이터베이스
# ============================================================

POLICY_DB: List[Policy] = [

    {
        "policy_id": "POL-001",
        "title": "연차휴가 운영규정",
        "category": "근태/휴가",
        "summary": "임직원의 연차휴가 사용 및 신청에 관한 규정입니다.",
        "details": "연차휴가는 사내 근태 시스템을 통해 사전에 신청하는 것을 원칙으로 합니다.",
        "target": "전 임직원",
        "keywords": ["연차", "휴가", "연차휴가"]
    },

    {
        "policy_id": "POL-002",
        "title": "재택근무 운영규정",
        "category": "근태/휴가",
        "summary": "재택근무 대상 및 신청 절차에 관한 규정입니다.",
        "details": "재택근무 대상자는 사전에 재택근무를 신청하고 승인받아야 합니다.",
        "target": "재택근무 대상자",
        "keywords": ["재택", "재택근무"]
    },

    {
        "policy_id": "POL-003",
        "title": "정보보안 기본규정",
        "category": "보안/정보보호",
        "summary": "회사 정보자산 및 개인정보 보호를 위한 기본 규정입니다.",
        "details": "회사 정보자산은 승인된 업무 목적으로만 사용해야 하며 중요정보를 외부로 무단 반출해서는 안 됩니다.",
        "target": "전 임직원",
        "keywords": ["보안", "정보보안", "정보자산", "개인정보"]
    },

    {
        "policy_id": "POL-004",
        "title": "경조사 지원규정",
        "category": "복리후생",
        "summary": "결혼, 출산, 조의 등 경조사에 대한 지원 기준을 규정합니다.",
        "details": "경조사 발생 시 회사가 정한 기준에 따라 경조금 및 경조휴가를 신청할 수 있습니다.",
        "target": "전 임직원",
        "keywords": ["경조사", "결혼", "출산", "조의", "경조금"]
    },

    {
        "policy_id": "POL-005",
        "title": "PC 및 정보자산 이용규정",
        "category": "PC/IT환경",
        "summary": "회사에서 지급하는 PC 및 정보자산의 이용 기준을 규정합니다.",
        "details": "회사에서 지급한 PC에는 승인된 소프트웨어만 설치하고 보안 프로그램을 임의로 삭제해서는 안 됩니다.",
        "target": "전 임직원",
        "keywords": ["PC", "컴퓨터", "정보자산", "소프트웨어"]
    },
]


# ============================================================
# 조직 데이터베이스
# ============================================================

ORGANIZATION_DB: List[Organization] = [

    {
        "department": "경영지원본부",
        "parent_department": "대표이사",
        "description": "인사, 총무, 재무 등 회사 운영을 지원합니다.",
        "responsibilities": [
            "인사관리",
            "복리후생",
            "총무",
            "재무"
        ],
        "contact": "경영지원본부 내 담당 부서 문의"
    },

    {
        "department": "인사팀",
        "parent_department": "경영지원본부",
        "description": "채용, 인사발령, 근태, 급여 및 인사제도를 담당합니다.",
        "responsibilities": [
            "채용",
            "인사발령",
            "근태관리",
            "급여",
            "복리후생"
        ],
        "contact": "내선 1001"
    },

    {
        "department": "IT지원팀",
        "parent_department": "IT본부",
        "description": "임직원의 PC, 네트워크 및 업무시스템 이용을 지원합니다.",
        "responsibilities": [
            "PC지원",
            "계정관리",
            "VPN",
            "업무시스템",
            "IT장애"
        ],
        "contact": "내선 2001"
    },

    {
        "department": "정보보안팀",
        "parent_department": "IT본부",
        "description": "회사 정보보안 정책 및 보안사고 대응을 담당합니다.",
        "responsibilities": [
            "정보보안",
            "개인정보보호",
            "보안사고 대응",
            "접근통제"
        ],
        "contact": "내선 2002"
    },

    {
        "department": "인재개발팀",
        "parent_department": "경영지원본부",
        "description": "임직원 교육 및 역량개발을 담당합니다.",
        "responsibilities": [
            "필수교육",
            "직무교육",
            "역량개발"
        ],
        "contact": "내선 1003"
    },
]


# ============================================================
# IT 환경설정 가이드 데이터베이스
# ============================================================

IT_GUIDE_DB: List[ITGuide] = [

    {
        "title": "신규 PC 초기 설정",
        "category": "PC/IT환경",
        "description": "신규 지급 PC의 기본 환경을 설정합니다.",
        "procedure": [
            "사내 계정으로 Windows 로그인",
            "백신 및 보안 프로그램 설치 확인",
            "업무용 표준 프로그램 설치",
            "VPN 설치 및 접속 테스트",
            "필요한 업무시스템 권한 신청"
        ],
        "contact": "IT지원팀",
        "keywords": ["신규PC", "PC설정", "입사", "PC"]
    },

    {
        "title": "VPN 사용 안내",
        "category": "PC/IT환경",
        "description": "외부에서 사내 시스템에 접속하기 위한 VPN 사용 방법입니다.",
        "procedure": [
            "VPN 사용 신청",
            "VPN 프로그램 설치",
            "사내 계정으로 로그인",
            "접속 테스트"
        ],
        "contact": "IT지원팀",
        "keywords": ["VPN", "원격", "외부접속", "재택"]
    },

    {
        "title": "비밀번호 보안 안내",
        "category": "보안/정보보호",
        "description": "사내 계정 비밀번호 관리 기준입니다.",
        "procedure": [
            "주기적인 비밀번호 변경",
            "타인과 계정 공유 금지",
            "동일 비밀번호의 외부 서비스 재사용 금지",
            "의심스러운 로그인 발생 시 보안팀 신고"
        ],
        "contact": "정보보안팀",
        "keywords": ["비밀번호", "계정", "보안"]
    },
]


# ============================================================
# 카테고리
# ============================================================

CATEGORIES = list(INTERNAL_JOB_DB.keys())