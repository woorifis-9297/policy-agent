"""
Shopping Agent Package
----------------------
LangGraph-based e-commerce shopping assistant agent.

This package provides a ReAct-style agent for handling:
- Product search by category
- Order status tracking
- Personalized product recommendations

Usage:
    from shopping_agent import graph

    # Invoke the agent
    response = graph.invoke({
        "messages": [{"role": "user", "content": "Show me electronics"}]
    })

    # With conversation memory (thread_id)
    response = graph.invoke(
        {"messages": [{"role": "user", "content": "What about clothing?"}]},
        config={"configurable": {"thread_id": "session_001"}}
    )
"""

from .agent import graph, create_shopping_agent, get_llm
from .tools import (
    get_all_products,
    search_products,
    search_products_by_keyword,
    check_order_status,
    SHOPPING_TOOLS
)
from .data import PRODUCT_DB, ORDER_DB, CATEGORIES
from .prompts import SYSTEM_PROMPT

__all__ = [
    # Main graph export (for langgraph.json)
    "graph",
    # Agent factory function
    "create_shopping_agent",
    "get_llm",
    # Tools (ReAct data-driven pattern)
    "get_all_products",
    "search_products",
    "search_products_by_keyword",
    "check_order_status",
    "SHOPPING_TOOLS",
    # Data
    "PRODUCT_DB",
    "ORDER_DB",
    "CATEGORIES",
    # Prompts
    "SYSTEM_PROMPT",
]
