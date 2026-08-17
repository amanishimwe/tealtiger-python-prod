"""Context management for TealTiger SDK v1.1.x Enterprise Adoption Features.

This module provides ExecutionContext and ContextManager for request tracing
and context propagation.

Part of P0.3: Correlation IDs and Traceability
"""

from .context_manager import (
    ContextManager,
    generate_correlation_id,
    generate_span_id,
    generate_trace_id,
    generate_uuid_v4,
)
from .execution_context import (
    CONTEXT_HEADERS,
    ExecutionContext,
    ExecutionContextOptions,
    is_valid_correlation_id,
    is_valid_uuid_v4,
    validate_execution_context,
)

__all__ = [
    "ExecutionContext",
    "ExecutionContextOptions",
    "CONTEXT_HEADERS",
    "is_valid_uuid_v4",
    "is_valid_correlation_id",
    "validate_execution_context",
    "ContextManager",
    "generate_uuid_v4",
    "generate_correlation_id",
    "generate_span_id",
    "generate_trace_id",
]
