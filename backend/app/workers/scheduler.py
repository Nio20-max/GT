from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.services.event_bus import EVENT_BUS
from app.services.runtime_state import RUNTIME_STATE
from app.services.scheduler_state import SCHEDULER_STATE

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _job_key_utc(job_name: str, now_utc: datetime, hhmm: str) -> str:
    return f"utc:{job_name}:{now_utc.date().isoformat()}:{hhmm}"


def _job_key_london(job_name: str, now_utc: datetime, hhmm: str) -> str:
    local = now_utc.astimezone(ZoneInfo("Europe/London"))
    return f"europe-london:{job_name}:{local.date().isoformat()}:{hhmm}"


def _should_run_utc(now_utc: datetime, hh: int, mm: int) -> bool:
    return (now_utc.hour, now_utc.minute) >= (hh, mm)


def _should_run_london(now_utc: datetime, hh: int, mm: int) -> bool:
    local = now_utc.astimezone(ZoneInfo("Europe/London"))
    return (local.hour, local.minute) >= (hh, mm)


def run_due_jobs(now_utc: datetime | None = None) -> dict:
    now = now_utc or datetime.now(timezone.utc)
    executions: list[dict] = []

    def execute_if_due(job_name: str, key: str, due: bool, fn) -> None:
        if not due or SCHEDULER_STATE.was_executed(key):
            return
        result = fn()
        SCHEDULER_STATE.mark_executed(key, result)
        execution = {"job": job_name, "key": key, "result": result}
        executions.append(execution)
        EVENT_BUS.publish("scheduler.window.executed", execution)

    execute_if_due(
        "training_tick",
        _job_key_utc("training_tick", now, "00:00"),
        _should_run_utc(now, 0, 0),
        lambda: RUNTIME_STATE.run_training_tick(),
    )
    execute_if_due(
        "precompute_cup",
        _job_key_utc("precompute_cup", now, "12:00"),
        _should_run_utc(now, 12, 0),
        lambda: RUNTIME_STATE.run_precompute("cup"),
    )
    execute_if_due(
        "precompute_ucl",
        _job_key_utc("precompute_ucl", now, "12:00"),
        _should_run_utc(now, 12, 0),
        lambda: RUNTIME_STATE.run_precompute("ucl"),
    )
    execute_if_due(
        "publish_cup",
        _job_key_utc("publish_cup", now, "13:00"),
        _should_run_utc(now, 13, 0),
        lambda: RUNTIME_STATE.run_publish("cup"),
    )
    execute_if_due(
        "publish_ucl",
        _job_key_utc("publish_ucl", now, "13:00"),
        _should_run_utc(now, 13, 0),
        lambda: RUNTIME_STATE.run_publish("ucl"),
    )
    execute_if_due(
        "precompute_league",
        _job_key_utc("precompute_league", now, "17:00"),
        _should_run_utc(now, 17, 0),
        lambda: RUNTIME_STATE.run_precompute("league"),
    )
    execute_if_due(
        "publish_league",
        _job_key_utc("publish_league", now, "18:00"),
        _should_run_utc(now, 18, 0),
        lambda: RUNTIME_STATE.run_publish("league"),
    )
    execute_if_due(
        "report_dispatch",
        _job_key_london("report_dispatch", now, "08:00"),
        _should_run_london(now, 8, 0),
        lambda: {"delivered": True, "atUtc": datetime.now(timezone.utc).isoformat()},
    )

    return {
        "nowUtc": now.isoformat(),
        "executions": executions,
        "schedulerState": SCHEDULER_STATE.summary(),
    }


def run_once() -> None:
    summary = run_due_jobs()
    logging.info("scheduler cycle: %s", summary)


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
