"""DNS-over-TLS Server implementation."""

import logging
import socket
import sys
from typing import Optional

from .resolvers import (
    resolve_with_curl,
    resolve_with_doh,
    resolve_with_kdig,
    resolve_with_ssock,
)
import validators


class DNSToTLSServer:
    """DNS to DNS-over-TLS proxy server."""

    def __init__(
        self,
        port: int = 1053,
        max_connections: int = 1,
        stub_resolver: str = "doh",
        host: str = "0.0.0.0",
    ):
        """Initialize the DNS-over-TLS server.
        
        Args:
            port: Port to listen on
            max_connections: Maximum concurrent connections
            stub_resolver: Resolver to use ('doh', 'curl', 'kdig', 'ssock')
            host: Host to bind to
        """
        self.port = port
        self.max_connections = max_connections
        self.stub_resolver = stub_resolver
        self.host = host
        self.socket: Optional[socket.socket] = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            level=logging.INFO,
        )

    def _get_resolver(self):
        """Get the appropriate resolver function based on stub_resolver setting."""
        resolvers = {
            "doh": resolve_with_doh,
            "curl": resolve_with_curl,
            "kdig": resolve_with_kdig,
            "ssock": resolve_with_ssock,
        }
        
        if self.stub_resolver not in resolvers:
            raise ValueError(f"Invalid stub resolver: {self.stub_resolver}")
        
        return resolvers[self.stub_resolver]

    def _handle_connection(self, connection: socket.socket, client_address: tuple) -> None:
        """Handle a single client connection.
        
        Args:
            connection: Client socket connection
            client_address: Client address tuple
        """
        resolver = self._get_resolver()
        
        try:
            while True:
                # Receive query from the user
                data = connection.recv(16)
                if not data:
                    logging.warning("No data from %s", client_address)
                    break

                try:
                    query = data.strip().decode("utf-8")
                except UnicodeDecodeError:
                    logging.warning("Non-unicode byte detected (keyboard interrupt perhaps?)")
                    break

                logging.info("Query received for %s", query)
                
                if not validators.domain(query):
                    logging.warning("Invalid URL %s from %s", query, client_address)
                    break

                # Resolve the query
                try:
                    result = resolver(query)
                    logging.info("Resolution result: %s", result)
                except Exception as e:
                    logging.error("Resolution failed for %s: %s", query, e)
                    break

                # Send response back to client
                if isinstance(result, str):
                    result = result.encode("utf-8")
                connection.sendall(result)
                logging.info("Response for query %s sent to %s: %s", query, client_address, result)

        except Exception as e:
            logging.error("Error handling connection from %s: %s", client_address, e)
        finally:
            connection.close()

    def start(self) -> None:
        """Start the DNS-over-TLS server."""
        # Create a TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind to port
        server_address = (self.host, self.port)
        logging.info(
            "Starting up %s on %s {port: %s, maxconns: %s, resolver: %s}",
            sys.argv[0],
            server_address,
            self.port,
            self.max_connections,
            self.stub_resolver,
        )
        
        self.socket.bind(server_address)
        self.socket.listen(self.max_connections)

        try:
            while True:
                # Wait for a connection
                connection, client_address = self.socket.accept()
                self._handle_connection(connection, client_address)
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        finally:
            if self.socket:
                self.socket.close()

    def stop(self) -> None:
        """Stop the DNS-over-TLS server."""
        if self.socket:
            self.socket.close()
            self.socket = None


def dnstotls(port: int, maxconn: int, stub: str) -> None:
    """Legacy function for backward compatibility.
    
    Args:
        port: Port to listen on
        maxconn: Maximum concurrent connections
        stub: Stub resolver to use
    """
    server = DNSToTLSServer(port=port, max_connections=maxconn, stub_resolver=stub)
    server.start() 