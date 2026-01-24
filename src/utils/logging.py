from __future__ import annotations

import logging, os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: str = "logs", log_file: str = "ai.log", level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logfile_path = os.path.join(log_dir, log_file)
    root = logging.getLogger()
    root.setLevel(lvl)

    if root.handlers:
        return

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    sh = logging.StreamHandler()
    sh.setLevel(lvl)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    fh = RotatingFileHandler(logfile_path, maxBytes= 5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setLevel(lvl)
    fh.setFormatter(fmt)
    root.addHandler(fh)

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True

def  attack_request_id_filter() -> None:
    root = logging.getLogger()
    root.addFilter(RequestIDFilter())
