from __future__ import annotations

import argparse

from index_classifier import ReportRowCleaner, load_index, load_simple_rules_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and classify downloaded report rows.")
    parser.add_argument("report", help="원본 보고서 파일 경로")
    parser.add_argument("rules", help="쉬운 규칙표 CSV/XLSX 또는 JSON 인덱스 파일 경로")
    parser.add_argument("--cleaned", help="정제 보고서 저장 경로")
    parser.add_argument("--failed", help="매칭 실패 로우 저장 경로")
    parser.add_argument("--log", help="적용 인덱스 로그 저장 경로")
    parser.add_argument("--brand-id", default="default", help="인덱스 범위 제한용 브랜드 ID")
    parser.add_argument("--account-id", action="append", default=[], help="인덱스 범위 제한용 계정 ID")
    args = parser.parse_args()

    if args.rules.lower().endswith(".json"):
        index = load_index(args.rules)
    else:
        index = load_simple_rules_index(
            args.rules,
            brand_id=args.brand_id,
            account_ids=args.account_id,
        )

    result = ReportRowCleaner(index).clean_file(
        args.report,
        cleaned_path=args.cleaned,
        failed_path=args.failed,
        log_path=args.log,
    )

    print(f"정제 보고서: {result.cleaned_report_path}")
    print(f"실패 로우: {result.failed_rows_path}")
    print(f"인덱스 로그: {result.index_log_path}")


if __name__ == "__main__":
    main()
