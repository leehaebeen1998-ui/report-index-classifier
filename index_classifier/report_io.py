from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def read_report_rows(path: str | Path, *, sheet_name: str | None = None) -> list[dict[str, Any]]:
    report_path = Path(path)
    suffix = report_path.suffix.casefold()

    if suffix == ".csv":
        return _read_delimited(report_path, delimiter=",")
    if suffix == ".tsv":
        return _read_delimited(report_path, delimiter="\t")
    if suffix == ".xlsx":
        return _read_xlsx(report_path, sheet_name=sheet_name)

    raise ValueError(f"Unsupported report file type: {report_path.suffix}")


def write_csv_rows(
    path: str | Path,
    rows: list[dict[str, Any]],
    *,
    fieldnames: list[str],
    encoding: str = "utf-8-sig",
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding=encoding, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _read_delimited(path: Path, *, delimiter: str) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        return [dict(row) for row in reader]


def _read_xlsx(path: Path, *, sheet_name: str | None) -> list[dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("openpyxl is required to read .xlsx report files.") from exc

    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook[sheet_name] if sheet_name else workbook.active
    rows = worksheet.iter_rows(values_only=True)

    try:
        header_row = next(rows)
    except StopIteration:
        return []

    headers = ["" if value is None else str(value) for value in header_row]
    results: list[dict[str, Any]] = []
    for row in rows:
        item = {
            headers[index]: value
            for index, value in enumerate(row)
            if index < len(headers) and headers[index]
        }
        if any(value not in (None, "") for value in item.values()):
            results.append(item)
    return results
