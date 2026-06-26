# 쉬운 인덱스 규칙표

일반 사용자는 JSON 파일을 직접 수정하지 않는다.

권장 방식은 `start_rule_editor.bat`를 실행해서 탭 화면에서 규칙을 입력하는 것이다.

```cmd
start_rule_editor.bat
```

또는 직접 실행한다.

```cmd
python rule_editor_gui.py examples/simple-index-rules.example.csv
```

프로그램 탭:

```text
0 강제 지정 URL
1 캠페인 유형
2 그룹명
3 키워드명
4 캠페인명
5 일반 URL
```

프로그램은 입력값을 아래 CSV 규칙표에 저장한다.

```text
examples\simple-index-rules.example.csv
```

CSV 또는 엑셀에서 직접 수정할 수도 있지만, 일반 사용자는 프로그램 입력 방식을 우선 사용한다.

규칙표 예시:

```text
순위,규칙,매칭값,카테고리,신뢰도,사용,메모
0,강제 지정 URL,https://example.com/drug,마약,1,O,이 URL은 무조건 마약
2,그룹명,형사,형사,0.9,O,광고그룹명에 형사 포함
3,키워드명,마약,마약,0.9,O,키워드명에 마약 포함
4,캠페인명,브랜드,브랜드,0.85,O,캠페인명에 브랜드 포함
5,일반 URL,/criminal,형사,0.65,O,URL 보조 규칙
```

## 컬럼 설명

| 컬럼 | 설명 |
| --- | --- |
| `순위` | 분류 우선순위 |
| `규칙` | 어떤 필드를 볼지 적는다 |
| `매칭값` | 해당 값이 포함되면 매칭된다 |
| `카테고리` | 최종 분류명 |
| `신뢰도` | 0~1 사이 숫자 |
| `사용` | `O`면 사용, `X`면 미사용 |
| `메모` | 사람이 보는 설명 |

## 순위별 작성법

### 0순위: 강제 지정 URL

특정 URL은 무조건 특정 카테고리로 보내야 할 때 사용한다.

```text
0,강제 지정 URL,https://example.com/drug,마약,1,O,무조건 마약
```

### 1순위: 캠페인 유형

매체나 캠페인 유형을 먼저 구분할 때 사용한다.

```text
1,캠페인 유형,Naver SA,검색광고,0.8,O,네이버 검색광고
```

### 2순위: 그룹명

가장 많이 쓰는 규칙이다. 광고그룹명에 카테고리 단어가 들어가는 경우 사용한다.

```text
2,그룹명,형사,형사,0.9,O,형사 그룹
2,그룹명,이혼,이혼,0.9,O,이혼 그룹
```

### 3순위: 키워드명

검색광고처럼 키워드가 있는 보고서에서 사용한다.

```text
3,키워드명,마약,마약,0.9,O,마약 키워드
```

키워드명이 없는 Meta, GFA, P-MAX 같은 매체는 자동으로 이 단계가 건너뛰어진다.

### 4순위: 캠페인명

그룹명이나 키워드가 비어 있거나 불명확할 때 보조로 사용한다.

```text
4,캠페인명,브랜드,브랜드,0.85,O,브랜드 캠페인
```

### 5순위: 일반 URL

URL 일부로 추정할 때 사용한다. 강제 URL보다 약한 규칙이다.

```text
5,일반 URL,/criminal,형사,0.65,O,형사 URL
```

### 6순위: AI 분석

규칙표에는 직접 쓰지 않는다. 0~5순위 규칙이 모두 실패했을 때 프로그램이 마지막으로 AI 분석을 호출한다.

## 사용 예시

```python
from index_classifier import ReportRowCleaner, load_simple_rules_index

index = load_simple_rules_index("examples/simple-index-rules.example.csv")

cleaner = ReportRowCleaner(index)
cleaner.clean_file("examples/raw-report.example.csv")
```

CMD에서는 한 줄로 실행한다.

```cmd
python -c "from index_classifier import ReportRowCleaner, load_simple_rules_index; index=load_simple_rules_index('examples/simple-index-rules.example.csv'); r=ReportRowCleaner(index).clean_file('examples/raw-report.example.csv'); print(r.cleaned_report_path)"
```

더 쉬운 실행 명령은 다음과 같다.

```cmd
python clean_report.py examples/raw-report.example.csv examples/simple-index-rules.example.csv
```

이 명령은 아래 3개 파일을 만든다.

```text
examples\raw-report.example.cleaned.csv
examples\raw-report.example.failed.csv
examples\raw-report.example.index-log.json
```
