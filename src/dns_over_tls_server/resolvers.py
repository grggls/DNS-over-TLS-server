"""DNS resolver implementations."""

import subprocess
from typing import Union

from . import ssock


def resolve_with_doh(query: str) -> str:
    """Resolve DNS query using doh (DNS over HTTPS) tool.
    
    Args:
        query: Domain name to resolve
        
    Returns:
        DNS resolution result as string
    """
    command = f"doh {query}"
    return run_stub_command(command)


def resolve_with_curl(query: str) -> str:
    """Resolve DNS query using curl with Cloudflare DNS over HTTPS.
    
    Args:
        query: Domain name to resolve
        
    Returns:
        DNS resolution result as string
    """
    url = f"https://cloudflare-dns.com/dns-query?name={query}"
    command = f'curl --silent -H "accept: application/dns-json" "{url}"'
    return run_stub_command(command)


def resolve_with_kdig(query: str) -> str:
    """Resolve DNS query using kdig with TLS.
    
    Args:
        query: Domain name to resolve
        
    Returns:
        DNS resolution result as string
    """
    command = f"kdig -d @1.1.1.1 +tls-ca +tls-host=cloudflare-dns.com {query}"
    return run_stub_command(command)


def resolve_with_ssock(query: str) -> Union[str, bytes]:
    """Resolve DNS query using custom SSL socket implementation.
    
    Args:
        query: Domain name to resolve
        
    Returns:
        DNS resolution result as bytes or string
    """
    return ssock.connectsend(query)


def run_stub_command(command: str) -> str:
    """Run a shell command and return the output.
    
    Args:
        command: Shell command to execute
        
    Returns:
        Command output as string
        
    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout 