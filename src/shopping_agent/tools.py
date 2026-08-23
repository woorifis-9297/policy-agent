"""
Shopping Agent Tools
--------------------
Data-driven tool definitions for the e-commerce shopping assistant.

This module implements a true ReAct pattern where tools provide raw data
and the LLM reasons about the data to make recommendations.
"""

import logging
from typing import Literal
from langchain_core.tools import tool

from shopping_agent.data import PRODUCT_DB, ORDER_DB, CATEGORIES

logger = logging.getLogger("shopping_agent.tools")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [TOOL] %(message)s"))
    logger.addHandler(_handler)


@tool
def get_all_products() -> str:
    """전체 상품 카탈로그를 조회합니다.

    모든 카테고리의 전체 제품 목록을 반환합니다.
    LLM이 전체 상품을 파악하고 고객 요구사항에 맞는 제품을 직접 선택할 수 있습니다.

    Returns:
        전체 카테고리별 제품 목록 (이름, 가격, 평점 포함)
    """
    logger.info("[TOOL EXECUTED] get_all_products()")
    result = "=== 전체 상품 카탈로그 ===\n\n"

    for category, products in PRODUCT_DB.items():
        result += f"【{category}】\n"
        for p in products:
            result += f"  - {p['name']}: {p['price']:,}원 (평점: {p['rating']})\n"
        result += "\n"

    result += f"총 {sum(len(products) for products in PRODUCT_DB.values())}개 상품"
    return result


@tool
def search_products(
    category: Literal["전자기기", "의류", "생활용품", "식품", "뷰티", "스포츠", "가구"]
) -> str:
    """특정 카테고리의 제품을 검색합니다.

    지정된 카테고리의 모든 제품 정보를 반환합니다.
    LLM이 카테고리 내 제품들을 분석하여 고객에게 적합한 제품을 추천할 수 있습니다.

    Args:
        category: 검색할 제품 카테고리 (전자기기, 의류, 생활용품, 식품, 뷰티, 스포츠, 가구)

    Returns:
        해당 카테고리의 제품 목록 (이름, 가격, 평점 포함)
    """
    logger.info("[TOOL EXECUTED] search_products(category=%s)", category)
    products = PRODUCT_DB.get(category, [])

    if not products:
        return f"{category} 카테고리에 제품이 없습니다."

    result = f"【{category}】 카테고리 제품 목록:\n\n"
    for p in products:
        result += f"- {p['name']}\n"
        result += f"  가격: {p['price']:,}원\n"
        result += f"  평점: {p['rating']}/5.0\n\n"

    # Add summary statistics for LLM reasoning
    prices = [p['price'] for p in products]
    ratings = [p['rating'] for p in products]
    result += f"--- 카테고리 통계 ---\n"
    result += f"상품 수: {len(products)}개\n"
    result += f"가격 범위: {min(prices):,}원 ~ {max(prices):,}원\n"
    result += f"평균 평점: {sum(ratings)/len(ratings):.1f}\n"

    return result


@tool
def search_products_by_keyword(keyword: str) -> str:
    """키워드로 전체 카테고리에서 상품을 검색합니다.

    입력된 키워드가 상품명에 포함된 모든 제품을 검색합니다.
    LLM이 검색 결과를 분석하여 고객 요구에 맞는 제품을 선택할 수 있습니다.

    Args:
        keyword: 검색할 키워드 (예: "운동", "헤드폰", "청소기")

    Returns:
        키워드가 포함된 제품 목록 (카테고리, 이름, 가격, 평점 포함)
    """
    logger.info("[TOOL EXECUTED] search_products_by_keyword(keyword=%s)", keyword)
    results = []

    for category, products in PRODUCT_DB.items():
        for p in products:
            if keyword.lower() in p['name'].lower():
                results.append({
                    'category': category,
                    'name': p['name'],
                    'price': p['price'],
                    'rating': p['rating']
                })

    if not results:
        return f"'{keyword}' 키워드로 검색된 상품이 없습니다."

    result = f"'{keyword}' 검색 결과:\n\n"
    for item in results:
        result += f"- {item['name']} [{item['category']}]\n"
        result += f"  가격: {item['price']:,}원\n"
        result += f"  평점: {item['rating']}/5.0\n\n"

    result += f"총 {len(results)}개 상품 검색됨"
    return result


@tool
def check_order_status(order_id: str) -> str:
    """주문 번호로 배송 상태를 조회합니다.

    Args:
        order_id: 주문 번호 (예: ORD-2024-001)

    Returns:
        주문의 현재 배송 상태
    """
    logger.info("테스트입니다!!")
    logger.info("[TOOL EXECUTED] check_order_status(order_id=%s)", order_id)
    order = ORDER_DB.get(order_id)

    if not order:
        return f"주문번호 {order_id}를 찾을 수 없습니다."

    return (
        f"주문번호: {order_id}\n"
        f"제품: {order['item']}\n"
        f"상태: {order['status']}\n"
        f"배송예정일: {order['delivery_date']}"
    )


# Export all tools as a list for easy import
SHOPPING_TOOLS = [
    get_all_products,
    search_products,
    search_products_by_keyword,
    check_order_status,
]
