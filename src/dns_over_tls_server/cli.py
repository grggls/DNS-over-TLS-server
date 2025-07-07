"""Command-line interface for DNS-over-TLS server."""

import argparse
import logging
import sys

from .server import DNSToTLSServer


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DNS to DNS-over-TLS proxy server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        type=int,
        default=1053,
        help="listening port for incoming DNS queries",
    )
    parser.add_argument(
        "-c",
        "--connections",
        action="store",
        type=int,
        default=1,
        help="maximum concurrent connections to the service",
    )
    parser.add_argument(
        "-s",
        "--stub",
        action="store",
        type=str,
        default="doh",
        choices=["doh", "curl", "kdig", "ssock"],
        help="choose which stub resolver to use",
    )
    parser.add_argument(
        "--host",
        action="store",
        type=str,
        default="0.0.0.0",
        help="host to bind to",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose logging",
    )

    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=log_level,
    )

    try:
        server = DNSToTLSServer(
            port=args.port,
            max_connections=args.connections,
            stub_resolver=args.stub,
            host=args.host,
        )
        server.start()
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error("Server failed to start: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main() 