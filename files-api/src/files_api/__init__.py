"""Files API root module."""

from .monitoring.logger import configure_logger
from .monitoring.tracer import configure_tracing

configure_logger()
configure_tracing()
