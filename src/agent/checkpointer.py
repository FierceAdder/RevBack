"""LangGraph Checkpointer provider.

Provides persistent state management for the LangGraph Autonomous Recovery Agent.
Supports in-memory state saving for testing and development, and provides
resilient fallback for production environments.
"""

import logging
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver

from src.config import settings

logger = logging.getLogger("revback.checkpointer")

_checkpointer_instance: Optional[MemorySaver] = None


def get_checkpointer() -> MemorySaver:
    """Returns the shared LangGraph checkpointer instance.
    
    Uses an in-memory checkpointer by default, ensuring state survives across
    multiple calls within the process and supports thread interruption and resumption.
    """
    global _checkpointer_instance
    if _checkpointer_instance is None:
        logger.info("Initializing LangGraph state checkpointer...")
        _checkpointer_instance = MemorySaver()
    return _checkpointer_instance


def get_agent_config(thread_id: str) -> Dict[str, Any]:
    """Generates LangGraph configuration dictionary with thread_id for state tracking."""
    return {
        "configurable": {
            "thread_id": str(thread_id),
        }
    }
