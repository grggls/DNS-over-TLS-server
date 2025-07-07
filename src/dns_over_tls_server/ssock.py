"""SSL socket implementation for DNS-over-TLS."""

import binascii
import logging
import socket
import ssl
from typing import Union

import dns.message


class SSLSocket:
    """SSL socket wrapper for DNS-over-TLS connections."""

    def __init__(self, hostname: str = "1.1.1.1", port: int = 853):
        """Initialize SSL socket.
        
        Args:
            hostname: DNS server hostname
            port: DNS server port
        """
        self.hostname = hostname
        self.port = port
        self.context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with secure defaults.
        
        Returns:
            Configured SSL context
        """
        context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("/etc/ssl/cert.pem")
        return context

    def connectsend(self, query: str) -> Union[str, bytes]:
        """Connect to DNS server and send query.
        
        Args:
            query: Domain name to query
            
        Returns:
            DNS response as bytes or string
        """
        # Create a socket and wrap it
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        try:
            wrsock = self.context.wrap_socket(sock, server_hostname=self.hostname)
            wrsock.connect((self.hostname, self.port))
            cfcert = wrsock.getpeercert()

            # Pad and encode and send and receive
            encoded_query = self._padencode(query)
            wrsock.send(encoded_query)
            data = wrsock.recv(4096)
            
            logging.debug("Received data: %s", data)
            return data
            
        finally:
            sock.close()

    def _padencode(self, domain: str) -> bytes:
        """Format query with two-byte length prefix per RFC1035.
        
        Args:
            domain: Domain name to encode
            
        Returns:
            Encoded DNS query as bytes
        """
        msg = dns.message.make_query(domain, "A")
        return binascii.hexlify(msg.to_text().encode())


# Global instance for backward compatibility
_ssl_socket = SSLSocket()


def connectsend(query: str) -> Union[str, bytes]:
    """Legacy function for backward compatibility.
    
    Args:
        query: Domain name to query
        
    Returns:
        DNS response as bytes or string
    """
    return _ssl_socket.connectsend(query) 