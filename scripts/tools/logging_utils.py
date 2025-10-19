from __future__ import annotations
import logging, os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

def get_logger(name: str, run_id: str = "default") -> logging.Logger:
    logdir = Path("data/logs"); logdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = logdir / f"tests_{run_id}_{ts}.log"

    logger = logging.getLogger(name)
    if logger.handlers:  # idempotent
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh = RotatingFileHandler(logfile, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt); fh.setLevel(logging.INFO)
    sh = logging.StreamHandler(); sh.setFormatter(fmt); sh.setLevel(logging.INFO)
    logger.addHandler(fh); logger.addHandler(sh)
    logger.propagate = False
    logger.info("Logger initialized -> %s", logfile)
    return logger
