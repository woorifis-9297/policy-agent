"""
Shopping Agent Database
-----------------------
Product and order data for the e-commerce shopping assistant.
"""

from typing import TypedDict, List


class Product(TypedDict):
    """Product information schema."""
    name: str
    price: int
    rating: float


class Order(TypedDict):
    """Order information schema."""
    status: str
    item: str
    delivery_date: str


# Product database organized by category
PRODUCT_DB: dict[str, List[Product]] = {
    "전자기기": [
        {"name": "아이폰 17 Pro", "price": 1990000, "rating": 4.5},
        {"name": "애플워치 Ultra", "price": 599000, "rating": 4.8},
        {"name": "맥북 프로 16인치 M4", "price": 3490000, "rating": 4.9},
        {"name": "아이패드 프로 12.9", "price": 1590000, "rating": 4.7},
        {"name": "에어팟 맥스", "price": 769000, "rating": 4.6},
        {"name": "삼성 갤럭시 S25 Ultra", "price": 1650000, "rating": 4.7},
        {"name": "소니 WH-1000XM5 헤드폰", "price": 429000, "rating": 4.8},
        {"name": "LG 그램 17인치", "price": 2190000, "rating": 4.5},
        {"name": "닌텐도 스위치 OLED", "price": 415000, "rating": 4.6},
        {"name": "소니 플레이스테이션 5", "price": 628000, "rating": 4.7},
    ],
    "의류": [
        {"name": "노스페이스 눕시 패딩", "price": 359000, "rating": 4.8},
        {"name": "리바이스 501 청바지", "price": 129000, "rating": 4.5},
        {"name": "나이키 에어맥스 운동화", "price": 179000, "rating": 4.7},
        {"name": "유니클로 울트라라이트다운", "price": 99000, "rating": 4.4},
        {"name": "아디다스 트랙수트", "price": 139000, "rating": 4.3},
        {"name": "폴로 랄프로렌 셔츠", "price": 189000, "rating": 4.6},
        {"name": "캘빈클라인 언더웨어 세트", "price": 79000, "rating": 4.5},
        {"name": "무신사 스탠다드 맨투맨", "price": 39000, "rating": 4.2},
        {"name": "뉴발란스 993 러닝화", "price": 259000, "rating": 4.8},
        {"name": "파타고니아 플리스 자켓", "price": 219000, "rating": 4.7},
    ],
    "생활용품": [
        {"name": "다이슨 V15 무선청소기", "price": 1190000, "rating": 4.8},
        {"name": "삼성 비스포크 공기청정기", "price": 549000, "rating": 4.6},
        {"name": "쿠쿠 IH압력밥솥", "price": 389000, "rating": 4.7},
        {"name": "LG 스타일러", "price": 1890000, "rating": 4.5},
        {"name": "발뮤다 토스터", "price": 329000, "rating": 4.4},
        {"name": "필립스 에어프라이어 XXL", "price": 299000, "rating": 4.6},
        {"name": "드롱기 커피머신", "price": 789000, "rating": 4.7},
        {"name": "다이슨 에어랩", "price": 699000, "rating": 4.8},
        {"name": "브리타 정수기", "price": 45000, "rating": 4.3},
        {"name": "로봇청소기 로보락 S8", "price": 1290000, "rating": 4.7},
    ],
    "식품": [
        {"name": "정관장 홍삼정 에브리타임", "price": 89000, "rating": 4.7},
        {"name": "곰곰 무항생제 계란 30구", "price": 12900, "rating": 4.5},
        {"name": "마켓컬리 유기농 샐러드", "price": 8900, "rating": 4.3},
        {"name": "스타벅스 원두 1kg", "price": 32000, "rating": 4.6},
        {"name": "농심 신라면 멀티팩", "price": 4500, "rating": 4.8},
        {"name": "오뚜기 진라면 40개입", "price": 28000, "rating": 4.5},
        {"name": "동원 참치 선물세트", "price": 45000, "rating": 4.4},
        {"name": "한우 1++ 등심 500g", "price": 89000, "rating": 4.9},
        {"name": "제주 감귤 5kg", "price": 29000, "rating": 4.6},
        {"name": "프로틴 파우더 2kg", "price": 59000, "rating": 4.5},
    ],
    "뷰티": [
        {"name": "설화수 윤조에센스", "price": 130000, "rating": 4.8},
        {"name": "SK-II 피테라 에센스", "price": 289000, "rating": 4.7},
        {"name": "에스티로더 갈색병 세럼", "price": 145000, "rating": 4.6},
        {"name": "라네즈 립슬리핑마스크", "price": 22000, "rating": 4.5},
        {"name": "이니스프리 그린티 세럼", "price": 32000, "rating": 4.4},
        {"name": "아이오페 레티놀 크림", "price": 65000, "rating": 4.5},
        {"name": "닥터자르트 시카페어 크림", "price": 48000, "rating": 4.6},
        {"name": "헤라 블랙쿠션", "price": 55000, "rating": 4.7},
        {"name": "MAC 루비우 립스틱", "price": 38000, "rating": 4.5},
        {"name": "조말론 향수 100ml", "price": 195000, "rating": 4.8},
    ],
    "스포츠": [
        {"name": "나이키 에어줌 러닝화", "price": 169000, "rating": 4.7},
        {"name": "요가매트 프리미엄 8mm", "price": 49000, "rating": 4.5},
        {"name": "덤벨 세트 20kg", "price": 89000, "rating": 4.6},
        {"name": "가민 포러너 265 스마트워치", "price": 549000, "rating": 4.8},
        {"name": "룰루레몬 레깅스", "price": 138000, "rating": 4.7},
        {"name": "테니스 라켓 윌슨 프로", "price": 289000, "rating": 4.5},
        {"name": "골프 드라이버 테일러메이드", "price": 650000, "rating": 4.6},
        {"name": "캠핑 텐트 4인용", "price": 320000, "rating": 4.4},
        {"name": "등산 배낭 45L", "price": 159000, "rating": 4.5},
        {"name": "자전거 헬멧", "price": 89000, "rating": 4.6},
    ],
    "가구": [
        {"name": "이케아 MALM 침대 프레임", "price": 299000, "rating": 4.4},
        {"name": "시디즈 T50 사무용 의자", "price": 489000, "rating": 4.7},
        {"name": "한샘 책상 1400", "price": 359000, "rating": 4.5},
        {"name": "에이스침대 매트리스 퀸", "price": 890000, "rating": 4.8},
        {"name": "무인양품 선반 유닛", "price": 189000, "rating": 4.3},
        {"name": "리바트 소파 3인용", "price": 1290000, "rating": 4.6},
        {"name": "스탠딩 데스크 전동", "price": 450000, "rating": 4.5},
        {"name": "LED 스탠드 조명", "price": 79000, "rating": 4.4},
        {"name": "행거 옷장 시스템", "price": 259000, "rating": 4.3},
        {"name": "거실장 TV 스탠드", "price": 389000, "rating": 4.5},
    ],
}

# Order database with order IDs as keys
ORDER_DB: dict[str, Order] = {
    # 배송완료 주문
    "ORD-2024-001": {
        "status": "배송완료",
        "item": "아이폰 17 Pro",
        "delivery_date": "2024-12-20"
    },
    "ORD-2024-002": {
        "status": "배송완료",
        "item": "애플워치 Ultra",
        "delivery_date": "2024-12-18"
    },
    "ORD-2024-003": {
        "status": "배송완료",
        "item": "노스페이스 눕시 패딩",
        "delivery_date": "2024-12-15"
    },
    # 배송중 주문
    "ORD-2024-004": {
        "status": "배송중",
        "item": "다이슨 V15 무선청소기",
        "delivery_date": "2025-01-05"
    },
    "ORD-2024-005": {
        "status": "배송중",
        "item": "맥북 프로 16인치 M4",
        "delivery_date": "2025-01-06"
    },
    "ORD-2024-006": {
        "status": "배송중",
        "item": "설화수 윤조에센스",
        "delivery_date": "2025-01-04"
    },
    # 준비중 주문
    "ORD-2025-001": {
        "status": "준비중",
        "item": "에이스침대 매트리스 퀸",
        "delivery_date": "2025-01-10"
    },
    "ORD-2025-002": {
        "status": "준비중",
        "item": "시디즈 T50 사무용 의자",
        "delivery_date": "2025-01-08"
    },
    "ORD-2025-003": {
        "status": "준비중",
        "item": "가민 포러너 265 스마트워치",
        "delivery_date": "2025-01-09"
    },
    # 결제대기 주문
    "ORD-2025-004": {
        "status": "결제대기",
        "item": "LG 스타일러",
        "delivery_date": "미정"
    },
    "ORD-2025-005": {
        "status": "결제대기",
        "item": "골프 드라이버 테일러메이드",
        "delivery_date": "미정"
    },
    # 취소 주문
    "ORD-2024-010": {
        "status": "주문취소",
        "item": "소니 플레이스테이션 5",
        "delivery_date": "취소됨"
    },
    # 교환/반품 주문
    "ORD-2024-011": {
        "status": "반품진행중",
        "item": "리바이스 501 청바지",
        "delivery_date": "2025-01-07"
    },
    "ORD-2024-012": {
        "status": "교환진행중",
        "item": "나이키 에어맥스 운동화",
        "delivery_date": "2025-01-08"
    },
}

# Available product categories
CATEGORIES = list(PRODUCT_DB.keys())
