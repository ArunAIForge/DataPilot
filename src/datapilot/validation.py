"""Validate uploaded CSVs before they reach the agents."""
from __future__ import annotations

import io
from dataclasses import dataclass

import pandas as pd

MAX_BYTES = 25 * 1024 * 1024
MAX_ROWS = 500_000


@dataclass
class CsvCheck:
    ok: bool
    message: str = ""
    rows: int = 0
    columns: tuple = ()


def validate_csv(data: bytes) -> CsvCheck:
    if not data:
        return CsvCheck(False, "The file is empty.")
    if len(data) > MAX_BYTES:
        return CsvCheck(False, f"File is larger than {MAX_BYTES // 1024 // 1024} MB.")
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception as exc:
        return CsvCheck(False, f"Could not read this as a CSV ({type(exc).__name__}).")
    if df.empty or df.shape[1] < 2:
        return CsvCheck(False, "The CSV needs at least 2 columns and 1 row.")
    if len(df) > MAX_ROWS:
        return CsvCheck(False, f"Too many rows ({len(df):,}); the limit is {MAX_ROWS:,}.")
    if not df.select_dtypes("number").shape[1]:
        return CsvCheck(False, "No numeric column found; nothing to analyse.")
    return CsvCheck(True, "ok", len(df), tuple(df.columns))
