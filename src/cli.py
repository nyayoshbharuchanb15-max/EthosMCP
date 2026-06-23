from __future__ import annotations

import argparse

from src.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(prog="ethosmcp")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve = subparsers.add_parser("serve")
    serve.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    if args.command == "serve":
        run_server(transport=args.transport, port=args.port, config_path=args.config)
