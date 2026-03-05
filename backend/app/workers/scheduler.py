from __future__ import annotations

import argparse
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run_once() -> None:
    logging.info("scheduler cycle: lock/precompute/publish placeholders executed")


def run_daemon(interval_seconds: int = 60) -> None:
    while True:
        run_once()
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="GT scheduler worker")
    parser.add_argument("--once", action="store_true", help="Run one scheduler cycle")
    parser.add_argument("--interval", type=int, default=60, help="Daemon loop interval in seconds")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_daemon(args.interval)


if __name__ == "__main__":
    main()
