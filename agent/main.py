"""
Agent entrypoint.

Usage:
    python -m agent                      # run with ./agent/agent_config.yaml (or AGENT_CONFIG)
    python -m agent --config <path>     # run with a specific config file
    python -m agent --once              # send burst + heartbeat once, then exit (useful for tests)
    python -m agent --version
"""

import argparse
import signal
import sys
import threading

from agent import __version__
from agent.config import load_config
from agent.logging_setup import get_logger, setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="soc-agent", description="SOC Endpoint Detection Agent")
    parser.add_argument("--config", help="path to the agent config YAML file")
    parser.add_argument("--once", action="store_true", help="collect once, send, then exit")
    parser.add_argument("--version", action="version", version=f"soc-agent {__version__}")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config_manager = load_config(args.config)
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    setup_logging(
        level=config_manager.log_level,
        log_dir=config_manager.get("log_dir"),
        log_max_bytes=int(config_manager.get("log_max_bytes", 5_000_000)),
        log_backups=int(config_manager.get("log_backups", 3)),
        quiet=args.once,
    )
    logger = get_logger()
    logger.info("Agent command line: %s", " ".join(sys.argv))

    from agent.core import AgentCore

    core = AgentCore(config_manager, config_source=args.config or "default")
    try:
        core.initialize()
    except Exception as exc:
        logger.error("Initialization failed: %s", exc)
        return 1

    if args.once:
        # Collect a single tick from each monitor, then flush synchronously.
        for monitor in core._monitors:
            try:
                for event in monitor._collect():
                    core.emit(event)
            except Exception as exc:
                logger.error("%s monitor collection failed: %s", monitor.name, exc)
        core.stop()
        logger.info("Once-mode run complete; queued events flushed.")
        return 0

    core.start()

    stop_event = threading.Event()

    def _handle(signum, _frame):
        logger.info("Received signal %s; shutting down...", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)

    # Watchdog in a daemon thread; main thread waits for a stop signal.
    watchdog = threading.Thread(
        target=core.run_watchdog,
        kwargs={"stop_event": stop_event},
        name="watchdog",
        daemon=True,
    )
    watchdog.start()

    try:
        while not stop_event.wait(1.0):
            pass
    finally:
        core.stop()
        print("Agent stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())