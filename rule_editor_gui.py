from __future__ import annotations

import argparse
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from index_classifier.simple_rule_table import (
    DEFAULT_CONFIDENCE_BY_PRIORITY,
    RULE_LABELS,
    append_simple_rule,
    delete_simple_rule,
    read_simple_rule_rows,
    write_simple_rule_rows,
)


class RuleEditorApp(tk.Tk):
    def __init__(self, rules_path: Path) -> None:
        super().__init__()
        self.title("보고서 인덱스 규칙 입력")
        self.geometry("920x620")
        self.minsize(820, 520)

        self.rules_path = rules_path
        if not self.rules_path.exists():
            write_simple_rule_rows(self.rules_path, [])

        self.tab_widgets: dict[int, dict[str, tk.Widget | ttk.Treeview]] = {}

        self._build_header()
        self._build_tabs()
        self.refresh_all_tabs()

    def _build_header(self) -> None:
        frame = ttk.Frame(self, padding=(12, 10))
        frame.pack(fill="x")

        ttk.Label(frame, text="규칙표 파일").pack(side="left")
        self.path_var = tk.StringVar(value=str(self.rules_path))
        path_entry = ttk.Entry(frame, textvariable=self.path_var, state="readonly")
        path_entry.pack(side="left", fill="x", expand=True, padx=8)

        ttk.Button(frame, text="다른 규칙표 열기", command=self.choose_rules_file).pack(side="left")
        ttk.Button(frame, text="새로고침", command=self.refresh_all_tabs).pack(side="left", padx=(6, 0))

    def _build_tabs(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for priority, label in RULE_LABELS.items():
            tab = ttk.Frame(notebook, padding=12)
            notebook.add(tab, text=f"{priority} {label}")
            self._build_rule_tab(tab, priority, label)

    def _build_rule_tab(self, parent: ttk.Frame, priority: int, label: str) -> None:
        input_frame = ttk.LabelFrame(parent, text=f"{priority}순위 - {label}", padding=12)
        input_frame.pack(fill="x")
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text=self._match_label(priority)).grid(row=0, column=0, sticky="w")
        match_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=match_var).grid(row=0, column=1, sticky="ew", padx=(8, 16))

        ttk.Label(input_frame, text="카테고리").grid(row=0, column=2, sticky="w")
        category_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=category_var).grid(row=0, column=3, sticky="ew", padx=(8, 0))

        ttk.Label(input_frame, text="신뢰도").grid(row=1, column=0, sticky="w", pady=(8, 0))
        confidence_var = tk.StringVar(value=DEFAULT_CONFIDENCE_BY_PRIORITY[priority])
        ttk.Entry(input_frame, textvariable=confidence_var, width=10).grid(
            row=1,
            column=1,
            sticky="w",
            padx=(8, 16),
            pady=(8, 0),
        )

        ttk.Label(input_frame, text="메모").grid(row=1, column=2, sticky="w", pady=(8, 0))
        memo_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=memo_var).grid(
            row=1,
            column=3,
            sticky="ew",
            padx=(8, 0),
            pady=(8, 0),
        )

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=4, sticky="e", pady=(10, 0))
        ttk.Button(
            button_frame,
            text="규칙 저장",
            command=lambda: self.add_rule(priority),
        ).pack(side="left")
        ttk.Button(
            button_frame,
            text="입력 초기화",
            command=lambda: self.clear_inputs(priority),
        ).pack(side="left", padx=(6, 0))

        table_frame = ttk.LabelFrame(parent, text="저장된 규칙", padding=8)
        table_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("number", "match_value", "category", "confidence", "enabled", "memo")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        tree.heading("number", text="번호")
        tree.heading("match_value", text="매칭값")
        tree.heading("category", text="카테고리")
        tree.heading("confidence", text="신뢰도")
        tree.heading("enabled", text="사용")
        tree.heading("memo", text="메모")
        tree.column("number", width=60, anchor="center", stretch=False)
        tree.column("match_value", width=320)
        tree.column("category", width=120, anchor="center")
        tree.column("confidence", width=90, anchor="center", stretch=False)
        tree.column("enabled", width=70, anchor="center", stretch=False)
        tree.column("memo", width=220)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(
            bottom_frame,
            text="선택 규칙 삭제",
            command=lambda: self.delete_selected_rule(priority),
        ).pack(side="right")

        self.tab_widgets[priority] = {
            "match": match_var,
            "category": category_var,
            "confidence": confidence_var,
            "memo": memo_var,
            "tree": tree,
        }

    def choose_rules_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="규칙표 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not selected:
            return
        self.rules_path = Path(selected)
        if not self.rules_path.exists():
            write_simple_rule_rows(self.rules_path, [])
        self.path_var.set(str(self.rules_path))
        self.refresh_all_tabs()

    def add_rule(self, priority: int) -> None:
        widgets = self.tab_widgets[priority]
        match_value = self._var(widgets["match"]).get().strip()
        category = self._var(widgets["category"]).get().strip()
        confidence = self._var(widgets["confidence"]).get().strip()
        memo = self._var(widgets["memo"]).get().strip()

        if not match_value:
            messagebox.showwarning("입력 필요", f"{self._match_label(priority)}을 입력해 주세요.")
            return
        if not category:
            messagebox.showwarning("입력 필요", "카테고리를 입력해 주세요.")
            return
        try:
            float(confidence)
        except ValueError:
            messagebox.showwarning("입력 확인", "신뢰도는 0~1 사이 숫자로 입력해 주세요.")
            return

        append_simple_rule(
            self.rules_path,
            priority=priority,
            match_value=match_value,
            category=category,
            confidence=confidence,
            memo=memo,
        )
        self.clear_inputs(priority)
        self.refresh_all_tabs()
        messagebox.showinfo("저장 완료", "규칙이 저장되었습니다.")

    def delete_selected_rule(self, priority: int) -> None:
        tree = self._tree(self.tab_widgets[priority]["tree"])
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("선택 필요", "삭제할 규칙을 선택해 주세요.")
            return

        item = tree.item(selected[0])
        one_based_index = int(item["values"][0])
        if not messagebox.askyesno("삭제 확인", "선택한 규칙을 삭제할까요?"):
            return

        delete_simple_rule(self.rules_path, one_based_index=one_based_index)
        self.refresh_all_tabs()

    def clear_inputs(self, priority: int) -> None:
        widgets = self.tab_widgets[priority]
        self._var(widgets["match"]).set("")
        self._var(widgets["category"]).set("")
        self._var(widgets["confidence"]).set(DEFAULT_CONFIDENCE_BY_PRIORITY[priority])
        self._var(widgets["memo"]).set("")

    def refresh_all_tabs(self) -> None:
        rows = read_simple_rule_rows(self.rules_path)
        for priority, widgets in self.tab_widgets.items():
            tree = self._tree(widgets["tree"])
            for item in tree.get_children():
                tree.delete(item)

            for one_based_index, row in enumerate(rows, start=1):
                if str(row.get("순위", "")).strip() != str(priority):
                    continue
                tree.insert(
                    "",
                    "end",
                    values=(
                        one_based_index,
                        row.get("매칭값", ""),
                        row.get("카테고리", ""),
                        row.get("신뢰도", ""),
                        row.get("사용", ""),
                        row.get("메모", ""),
                    ),
                )

    def _match_label(self, priority: int) -> str:
        return {
            0: "강제 지정 URL",
            1: "캠페인 유형",
            2: "그룹명",
            3: "키워드명",
            4: "캠페인명",
            5: "일반 URL",
        }[priority]

    def _var(self, value: tk.Widget | tk.StringVar | ttk.Treeview) -> tk.StringVar:
        if not isinstance(value, tk.StringVar):
            raise TypeError("Expected StringVar")
        return value

    def _tree(self, value: tk.Widget | tk.StringVar | ttk.Treeview) -> ttk.Treeview:
        if not isinstance(value, ttk.Treeview):
            raise TypeError("Expected Treeview")
        return value


def main() -> None:
    parser = argparse.ArgumentParser(description="인덱스 규칙을 탭 화면에서 입력합니다.")
    parser.add_argument(
        "rules",
        nargs="?",
        default="examples/simple-index-rules.example.csv",
        help="규칙표 CSV 파일 경로",
    )
    args = parser.parse_args()

    app = RuleEditorApp(Path(args.rules))
    app.mainloop()


if __name__ == "__main__":
    main()
