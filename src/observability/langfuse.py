"""Langfuse LLM Tracing and Observability integration for RevBack.

Supports:
1. LiteLLM callback automatic tracking (tokens, latency, costs).
2. Function tracing via @observe_agent wrapper.
3. Live trace metrics fetching with graceful fallback.
"""

import os
import functools
import logging
from typing import Optional, Any, Callable
from src.config import settings

logger = logging.getLogger(__name__)

_langfuse_client: Optional[Any] = None
_langfuse_initialized = False


def get_langfuse_client():
    """Returns the singleton Langfuse client if configured, else None."""
    global _langfuse_client, _langfuse_initialized
    if _langfuse_initialized:
        return _langfuse_client

    pub_key = settings.LANGFUSE_PUBLIC_KEY or os.getenv("LANGFUSE_PUBLIC_KEY")
    sec_key = settings.LANGFUSE_SECRET_KEY or os.getenv("LANGFUSE_SECRET_KEY")
    host = settings.LANGFUSE_HOST or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if pub_key and sec_key:
        try:
            from langfuse import Langfuse
            _langfuse_client = Langfuse(
                public_key=pub_key,
                secret_key=sec_key,
                host=host,
            )
            logger.info("Langfuse observability client initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse client: {e}")
            _langfuse_client = None
    else:
        _langfuse_client = None

    _langfuse_initialized = True
    return _langfuse_client


def setup_langfuse():
    """Configures LiteLLM and environment variables for automatic Langfuse logging."""
    pub_key = settings.LANGFUSE_PUBLIC_KEY or os.getenv("LANGFUSE_PUBLIC_KEY")
    sec_key = settings.LANGFUSE_SECRET_KEY or os.getenv("LANGFUSE_SECRET_KEY")
    host = settings.LANGFUSE_HOST or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if pub_key and sec_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = pub_key
        os.environ["LANGFUSE_SECRET_KEY"] = sec_key
        os.environ["LANGFUSE_HOST"] = host

        try:
            import litellm
            if "langfuse" not in (litellm.success_callback or []):
                litellm.success_callback = list(set((litellm.success_callback or []) + ["langfuse"]))
            if "langfuse" not in (litellm.failure_callback or []):
                litellm.failure_callback = list(set((litellm.failure_callback or []) + ["langfuse"]))
            logger.info("LiteLLM callbacks wired to Langfuse.")
        except Exception as e:
            logger.warning(f"Failed to wire LiteLLM callbacks to Langfuse: {e}")


def observe_agent(name: Optional[str] = None, **observe_kwargs):
    """Decorator to trace agent execution in Langfuse if active, otherwise transparent pass-through."""
    def decorator(fn: Callable):
        pub_key = settings.LANGFUSE_PUBLIC_KEY or os.getenv("LANGFUSE_PUBLIC_KEY")
        if pub_key:
            try:
                from langfuse import observe
                wrapped = observe(name=name or fn.__name__, **observe_kwargs)(fn)
                return wrapped
            except Exception as e:
                logger.debug(f"Langfuse observe decorator fallback: {e}")

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        import inspect
        if inspect.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    return decorator
