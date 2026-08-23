"""
Shopping Agent
--------------
LangGraph ReAct agent for e-commerce shopping assistance.

This module creates a ReAct-style agent using LangGraph's prebuilt
create_react_agent function with shopping tools.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from shopping_agent.tools import SHOPPING_TOOLS
from shopping_agent.prompts import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv(override=True)


def get_llm(model: Optional[str] = None):
    """
    Initialize the language model with flexible model selection.

    Args:
        model: Model identifier string. If not provided, uses LLM_MODEL
               environment variable or defaults to 'google_genai:gemini-flash-lite-latest'.

    Returns:
        Initialized chat model instance.
    """
    model_name = model or os.environ.get("LLM_MODEL", "google_genai:gemini-flash-lite-latest")
    return init_chat_model(
        model_name,
        temperature=0,
        max_tokens=2000
    )


def create_shopping_agent(
    model: Optional[str] = None,
    checkpointer: Optional[InMemorySaver] = None
):
    """
    Create a shopping assistant agent with tools.

    Args:
        model: Optional model identifier string for LLM.
        checkpointer: Optional memory checkpointer for conversation persistence.

    Returns:
        Compiled LangGraph agent ready for invocation.
    """
    llm = get_llm(model)

    agent = create_agent(
        model=llm,
        tools=SHOPPING_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

    return agent


# Create the default graph instance for LangGraph server
# This is referenced in langgraph.json as the entry point
graph = create_shopping_agent()
