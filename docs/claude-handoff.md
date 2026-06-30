# Claude Handoff: Report Index Classifier

## Current State

This repository contains the first working foundation for a report-row index classification module.

The current implementation is not the final integrated downloader app yet. It is a reusable classifier/cleaner layer that can be called after a raw report CSV is downloaded.

Main pieces:

- `index_classifier/`: reusable classification package
- `clean_report.py`: CLI entry point for cleaning one raw report
- `rule_editor_gui.py`: Tkinter GUI for editing simple CSV rules
- `examples/simple-index-rules.example.csv`: sample rule table
- `tests/test_classifier.py`: unit tests for classifier, simple rules, CSV reading, and cleaner output

## Final Goal

The user's final goal is to combine this classifier with the row downloader.

Expected flow:

1. Row downloader downloads a raw media report CSV.
2. Downloader passes the downloaded CSV path to the classifier.
3. Classifier loads the selected rule table CSV.
4. Classifier writes:
   - cleaned report CSV
   - failed/unresolved rows CSV
   - index log JSON
5. User reviews failed rows and adds more rules.
6. Next downloads use the improved rule table.

Preferred integration inside downloader Python code:

```python
from index_classifier import ReportRowCleaner, load_simple_rules_index

index = load_simple_rules_index("path/to/simple-index-rules.csv")
result = ReportRowCleaner(index).clean_file("path/to/downloaded-raw-report.csv")

print(result.cleaned_report_path)
print(result.failed_rows_path)
print(result.index_log_path)
```

Simple CLI integration:

```powershell
python clean_report.py "path\to\downloaded-raw-report.csv" "path\to\simple-index-rules.csv"
```

## Important Implementation Notes

### Naver CSV Title Row

Naver raw CSV files may start with a report title line, with the real header on the second line.

Example:

```text
"형사_키워드_주간 보고서(2026.06.29.~2026.06.29.),1826631"
일별,캠페인유형,URL,PC/모바일 매체,캠페인,광고그룹,키워드,...
```

`index_classifier.report_io._read_delimited()` now detects and skips that title row automatically by looking for known header names.

### Windows / OneDrive File Writing

The user's workspace is under a Korean OneDrive path. Python file writes sometimes failed with:

- `[Errno 9] Bad file descriptor`
- `UnauthorizedAccessException`
- file-not-found errors when creating output paths

To make writing more reliable:

- `index_classifier.simple_rule_table.write_simple_rule_rows()` has fallback write behavior.
- `index_classifier.report_io.write_text()` and `write_csv_rows()` use a PowerShell/.NET fallback when normal Python writing fails.
- `rule_editor_gui.py` no longer writes to CSV immediately when a rule is added. It updates the in-memory table first, then writes only when the user clicks `파일 저장`.
- If direct save fails, the GUI offers `다른 이름으로 저장`.

This was necessary because Excel, the row program, or OneDrive may hold the CSV file lock.

## Rule Table Status

The current sample rule table includes these user-requested rules:

- `https://taehaschool.com` -> `학폭`
- `taehaschool.com` URL contains -> `학폭`
- Sex-crime keywords -> `성범죄`
  - `강간`
  - `성범죄`
  - `추행`
  - `희롱`
  - `성폭`
  - `미성년자약취`
  - `성매매`
  - `아청`
  - `카촬`
  - `음란`
  - `성전문`
- Campaign/group contains `교통` or `음주` -> `교통/음주`
- Campaign/group contains `재산` or `경제` -> `재산범죄`

The user also saved a working rule table here:

```text
C:\Users\User\OneDrive\바탕 화면\이해빈\클로드 자동화\simple-index-rules.example.20260630-194948.csv
```

## Validation Performed

Tests:

```powershell
python -m unittest discover -s tests
```

Current result:

```text
Ran 13 tests
OK
```

Actual user row files tested:

```text
C:\Users\User\OneDrive\바탕 화면\이해빈\클로드 자동화\법무법인_태하\Naver\20260630\일별 로우\naver_thlaw_01_raw_20260629_20260629.csv
```

```text
C:\Users\User\OneDrive\바탕 화면\이해빈\클로드 자동화\법무법인_태하_-_데일리\Naver\20260630\일별 로우\naver_thlaw_01_raw_20260629_20260629.csv
```

Validation outputs were written to:

```text
C:\Users\User\AppData\Local\Temp\index_validation\
```

Summary for `법무법인_태하\Naver\20260630\일별 로우`:

```text
total rows: 6544
형사: 1872
재산범죄: 1448
교통/음주: 1428
성범죄: 987
학폭: 81
unresolved: 728
```

Summary for `법무법인_태하_-_데일리\Naver\20260630\일별 로우`:

```text
total rows: 5654
성범죄: 419
형사: 15
unresolved: 5220
```

The second file is mostly keyword-only, so classification coverage is low until more keyword rules are added.

## Next Work For Downloader Integration

1. Locate the row downloader's "download complete" point.
2. Capture the final raw CSV path.
3. Add a setting for the active rule table CSV path.
4. Call:

```python
index = load_simple_rules_index(rule_table_path)
result = ReportRowCleaner(index).clean_file(downloaded_csv_path)
```

5. Show or log:

```text
result.cleaned_report_path
result.failed_rows_path
result.index_log_path
```

6. For repeated daily automation, use `failed_rows_path` as the review queue for new rules.

## Recommended Next Rule Additions

From failed row samples, add keyword rules for items such as:

- `12대중과실`, `교통사고`, `속도위반` -> likely `교통/음주`
- `투자사기`, `NPL사기`, `가상계좌사기`, `SNS사기` -> likely `재산범죄`
- brand/person-name rows under `C_자사명`, `브랜드(...)`, `법무법인태하...` may need a `브랜드` or `자사명` category decision from the user.

Do not assume final category names for unresolved rows without user confirmation.
