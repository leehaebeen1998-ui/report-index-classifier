from __future__ import annotations

import argparse
from pathlib import Path

from index_classifier.simple_rule_table import (
    DEFAULT_CONFIDENCE_BY_PRIORITY,
    RULE_LABELS,
    append_simple_rule,
    delete_simple_rule,
    read_simple_rule_rows,
    write_simple_rule_rows,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="인덱스 규칙을 프로그램에서 입력/수정합니다.")
    parser.add_argument(
        "rules",
        nargs="?",
        default="examples/simple-index-rules.example.csv",
        help="규칙표 CSV 파일 경로",
    )
    args = parser.parse_args()

    rules_path = Path(args.rules)
    if not rules_path.exists():
        write_simple_rule_rows(rules_path, [])

    while True:
        print()
        print("=== 인덱스 규칙 입력 프로그램 ===")
        print(f"규칙표: {rules_path}")
        print("1. 규칙 추가")
        print("2. 규칙 목록 보기")
        print("3. 규칙 삭제")
        print("4. 종료")
        choice = input("선택: ").strip()

        if choice == "1":
            add_rule(rules_path)
        elif choice == "2":
            show_rules(rules_path)
        elif choice == "3":
            remove_rule(rules_path)
        elif choice == "4":
            print("종료합니다.")
            return
        else:
            print("1~4 중에서 선택해 주세요.")


def add_rule(rules_path: Path) -> None:
    print()
    print("추가할 규칙 종류를 선택하세요.")
    for priority, label in RULE_LABELS.items():
        print(f"{priority}. {label}")

    priority = ask_priority()
    match_value = ask_required("매칭값")
    category = ask_required("카테고리")
    default_confidence = DEFAULT_CONFIDENCE_BY_PRIORITY[priority]
    confidence = input(f"신뢰도 [{default_confidence}]: ").strip() or default_confidence
    memo = input("메모 [빈칸 가능]: ").strip()

    row = append_simple_rule(
        rules_path,
        priority=priority,
        match_value=match_value,
        category=category,
        confidence=confidence,
        memo=memo,
    )

    print()
    print("규칙이 저장되었습니다.")
    print(format_rule(len(read_simple_rule_rows(rules_path)), row))


def show_rules(rules_path: Path) -> None:
    rows = read_simple_rule_rows(rules_path)
    print()
    if not rows:
        print("저장된 규칙이 없습니다.")
        return

    print("저장된 규칙")
    for index, row in enumerate(rows, start=1):
        print(format_rule(index, row))


def remove_rule(rules_path: Path) -> None:
    show_rules(rules_path)
    rows = read_simple_rule_rows(rules_path)
    if not rows:
        return

    number_text = input("삭제할 번호: ").strip()
    if not number_text:
        print("삭제를 취소했습니다.")
        return

    try:
        removed = delete_simple_rule(rules_path, one_based_index=int(number_text))
    except (ValueError, IndexError) as exc:
        print(f"삭제 실패: {exc}")
        return

    print("삭제되었습니다.")
    print(format_rule(int(number_text), removed))


def ask_priority() -> int:
    while True:
        value = input("순위 번호: ").strip()
        try:
            priority = int(value)
        except ValueError:
            print("숫자로 입력해 주세요.")
            continue
        if priority in RULE_LABELS:
            return priority
        print("0~5 중에서 선택해 주세요.")


def ask_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label}은 비워둘 수 없습니다.")


def format_rule(index: int, row: dict[str, object]) -> str:
    return (
        f"{index}. [{row.get('순위')}] {row.get('규칙')} | "
        f"{row.get('매칭값')} => {row.get('카테고리')} | "
        f"신뢰도 {row.get('신뢰도')} | 사용 {row.get('사용')}"
    )


if __name__ == "__main__":
    main()
