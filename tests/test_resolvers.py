"""Unit tests for DNS resolvers."""

import subprocess
import pytest
from unittest.mock import Mock, patch

from dns_over_tls_server.resolvers import (
    resolve_with_doh,
    resolve_with_curl,
    resolve_with_kdig,
    resolve_with_ssock,
    run_stub_command,
)


class TestResolvers:
    """Test cases for DNS resolver functions."""

    @patch("dns_over_tls_server.resolvers.run_stub_command")
    def test_resolve_with_doh(self, mock_run_command):
        """Test doh resolver."""
        mock_run_command.return_value = "doh_result"
        
        result = resolve_with_doh("example.com")
        
        mock_run_command.assert_called_once_with("doh example.com")
        assert result == "doh_result"

    @patch("dns_over_tls_server.resolvers.run_stub_command")
    def test_resolve_with_curl(self, mock_run_command):
        """Test curl resolver."""
        mock_run_command.return_value = "curl_result"
        
        result = resolve_with_curl("example.com")
        
        expected_command = (
            'curl --silent -H "accept: application/dns-json" '
            '"https://cloudflare-dns.com/dns-query?name=example.com"'
        )
        mock_run_command.assert_called_once_with(expected_command)
        assert result == "curl_result"

    @patch("dns_over_tls_server.resolvers.run_stub_command")
    def test_resolve_with_kdig(self, mock_run_command):
        """Test kdig resolver."""
        mock_run_command.return_value = "kdig_result"
        
        result = resolve_with_kdig("example.com")
        
        expected_command = "kdig -d @1.1.1.1 +tls-ca +tls-host=cloudflare-dns.com example.com"
        mock_run_command.assert_called_once_with(expected_command)
        assert result == "kdig_result"

    @patch("dns_over_tls_server.resolvers.ssock")
    def test_resolve_with_ssock(self, mock_ssock):
        """Test ssock resolver."""
        mock_ssock.connectsend.return_value = b"ssock_result"
        
        result = resolve_with_ssock("example.com")
        
        mock_ssock.connectsend.assert_called_once_with("example.com")
        assert result == b"ssock_result"

    @patch("dns_over_tls_server.resolvers.subprocess")
    def test_run_stub_command_success(self, mock_subprocess):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.stdout = "command_output"
        mock_subprocess.run.return_value = mock_result
        
        result = run_stub_command("test_command")
        
        mock_subprocess.run.assert_called_once_with(
            "test_command",
            shell=True,
            stdout=mock_subprocess.PIPE,
            stderr=mock_subprocess.PIPE,
            text=True,
            check=True,
        )
        assert result == "command_output"

    @patch("dns_over_tls_server.resolvers.subprocess")
    def test_run_stub_command_failure(self, mock_subprocess):
        """Test command execution failure."""
        mock_subprocess.run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="test_command", stderr="error"
        )
        
        with pytest.raises(subprocess.CalledProcessError):
            run_stub_command("test_command") 