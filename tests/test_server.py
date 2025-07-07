"""Unit tests for DNS-over-TLS server."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from dns_over_tls_server.server import DNSToTLSServer


class TestDNSToTLSServer:
    """Test cases for DNSToTLSServer class."""

    def test_init_defaults(self):
        """Test server initialization with default values."""
        server = DNSToTLSServer()
        assert server.port == 1053
        assert server.max_connections == 1
        assert server.stub_resolver == "doh"
        assert server.host == "0.0.0.0"
        assert server.socket is None

    def test_init_custom_values(self):
        """Test server initialization with custom values."""
        server = DNSToTLSServer(
            port=8053,
            max_connections=5,
            stub_resolver="ssock",
            host="127.0.0.1",
        )
        assert server.port == 8053
        assert server.max_connections == 5
        assert server.stub_resolver == "ssock"
        assert server.host == "127.0.0.1"

    def test_get_resolver_valid(self):
        """Test getting valid resolver functions."""
        server = DNSToTLSServer(stub_resolver="doh")
        resolver = server._get_resolver()
        assert callable(resolver)

        server.stub_resolver = "curl"
        resolver = server._get_resolver()
        assert callable(resolver)

        server.stub_resolver = "kdig"
        resolver = server._get_resolver()
        assert callable(resolver)

        server.stub_resolver = "ssock"
        resolver = server._get_resolver()
        assert callable(resolver)

    def test_get_resolver_invalid(self):
        """Test getting invalid resolver raises ValueError."""
        server = DNSToTLSServer(stub_resolver="invalid")
        with pytest.raises(ValueError, match="Invalid stub resolver: invalid"):
            server._get_resolver()

    @patch("dns_over_tls_server.server.validators")
    @patch("dns_over_tls_server.server.logging")
    def test_handle_connection_valid_query(self, mock_logging, mock_validators):
        """Test handling connection with valid query."""
        server = DNSToTLSServer()
        mock_connection = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        
        # Mock connection behavior
        mock_connection.recv.return_value = b"example.com\n"
        mock_connection.sendall.return_value = None
        mock_connection.close.return_value = None
        
        # Mock validators
        mock_validators.domain.return_value = True
        
        # Mock resolver
        mock_resolver = Mock(return_value="resolved_result")
        server._get_resolver = Mock(return_value=mock_resolver)
        
        # Mock next recv to return empty (end loop)
        mock_connection.recv.side_effect = [b"example.com\n", b""]
        
        server._handle_connection(mock_connection, mock_client_address)
        
        # Verify resolver was called
        mock_resolver.assert_called_once_with("example.com")
        
        # Verify response was sent
        mock_connection.sendall.assert_called_once_with(b"resolved_result")
        
        # Verify connection was closed
        mock_connection.close.assert_called_once()

    @patch("dns_over_tls_server.server.validators")
    @patch("dns_over_tls_server.server.logging")
    def test_handle_connection_invalid_domain(self, mock_logging, mock_validators):
        """Test handling connection with invalid domain."""
        server = DNSToTLSServer()
        mock_connection = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        
        # Mock connection behavior
        mock_connection.recv.return_value = b"invalid-domain\n"
        mock_connection.close.return_value = None
        
        # Mock validators
        mock_validators.domain.return_value = False
        
        server._handle_connection(mock_connection, mock_client_address)
        
        # Verify connection was closed
        mock_connection.close.assert_called_once()

    @patch("dns_over_tls_server.server.validators")
    @patch("dns_over_tls_server.server.logging")
    def test_handle_connection_unicode_error(self, mock_logging, mock_validators):
        """Test handling connection with unicode decode error."""
        server = DNSToTLSServer()
        mock_connection = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        
        # Mock connection behavior
        mock_connection.recv.return_value = b"\xff\xfe"  # Invalid UTF-8
        mock_connection.close.return_value = None
        
        server._handle_connection(mock_connection, mock_client_address)
        
        # Verify connection was closed
        mock_connection.close.assert_called_once()

    @patch("dns_over_tls_server.server.validators")
    @patch("dns_over_tls_server.server.logging")
    def test_handle_connection_no_data(self, mock_logging, mock_validators):
        """Test handling connection with no data."""
        server = DNSToTLSServer()
        mock_connection = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        
        # Mock connection behavior
        mock_connection.recv.return_value = b""
        mock_connection.close.return_value = None
        
        server._handle_connection(mock_connection, mock_client_address)
        
        # Verify connection was closed
        mock_connection.close.assert_called_once()

    @patch("dns_over_tls_server.server.socket")
    @patch("dns_over_tls_server.server.logging")
    def test_start_server(self, mock_logging, mock_socket):
        """Test starting the server."""
        server = DNSToTLSServer(port=8053)
        
        # Mock socket behavior
        mock_socket_instance = Mock()
        mock_socket.socket.return_value = mock_socket_instance
        
        # Mock accept to raise KeyboardInterrupt to exit the loop
        mock_connection = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_socket_instance.accept.side_effect = KeyboardInterrupt()
        
        server.start()
        
        # Verify socket was created and configured
        mock_socket.socket.assert_called_once_with(mock_socket.AF_INET, mock_socket.SOCK_STREAM)
        mock_socket_instance.bind.assert_called_once_with(("0.0.0.0", 8053))
        mock_socket_instance.listen.assert_called_once_with(1)
        mock_socket_instance.close.assert_called_once()

    def test_stop_server(self):
        """Test stopping the server."""
        server = DNSToTLSServer()
        server.socket = Mock()
        
        server.stop()
        
        # Verify socket was closed
        server.socket.close.assert_called_once()
        assert server.socket is None

    def test_stop_server_no_socket(self):
        """Test stopping server when no socket exists."""
        server = DNSToTLSServer()
        server.socket = None
        
        # Should not raise an exception
        server.stop()
        assert server.socket is None 