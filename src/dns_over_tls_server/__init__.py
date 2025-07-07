"""DNS-over-TLS Server Package."""

__version__ = "0.1.0"

from .server import DNSToTLSServer
from .resolvers import (
    resolve_with_doh,
    resolve_with_curl,
    resolve_with_kdig,
    resolve_with_ssock,
)

__all__ = [
    "DNSToTLSServer",
    "resolve_with_doh",
    "resolve_with_curl", 
    "resolve_with_kdig",
    "resolve_with_ssock",
]

def hello() -> str:
    return "Hello from dns-over-tls-server!"
