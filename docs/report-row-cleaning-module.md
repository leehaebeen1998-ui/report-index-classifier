# 보고서 로우 정제 모듈

## 목적

3차 모듈은 2차 모듈에서 다운로드된 원본 보고서 파일을 입력받아 공통 정제 포맷으로 변환한다.

이 모듈은 로그인이나 다운로드를 수행하지 않는다. 원본 보고서 파일이 이미 존재한다는 전제에서 동작한다.

## 입력

- 원본 보고서 파일: `.csv`, `.tsv`, `.xlsx`
- 인덱스 파일: `category-index` JSON
- 선택 입력: AI analyzer, 출력 필드 설정, XLSX 시트명

## 출력

- 원본 보고서 파일: 입력 파일은 변경하지 않는다.
- 정제 보고서 파일: 기본값 `{원본파일명}.cleaned.csv`
- 매칭 실패 로우 파일: 기본값 `{원본파일명}.failed.csv`
- 적용된 인덱스 로그: 기본값 `{원본파일명}.index-log.json`

## 처리 순서

```text
1. 원본 보고서 파일 읽기
2. 컬럼명 자동 인식
3. 인덱스 기반 분류 엔진 호출
4. 0순위 강제 URL 매핑 확인
5. 캠페인 유형, 그룹명, 키워드명, 캠페인명, 일반 URL 순서로 분류
6. 규칙 매칭이 없을 때만 AI 분석
7. 필요한 컬럼만 남겨 공통 포맷 생성
8. 정제 보고서 저장
9. 미분류 또는 검토 필요 로우 저장
10. 적용된 인덱스와 매칭 근거 로그 저장
```

## 공통 정제 포맷

기본 출력 컬럼은 다음과 같다.

```text
account_id
brand_id
campaign_type
campaign_name
group_name
keyword_name
url
creative_name
ad_text
category
classification_confidence
classification_priority
classification_rule_id
classification_source
classification_needs_review
```

계정 ID와 브랜드 ID는 출력 및 인덱스 선택 범위 제한에 사용할 수 있지만, 카테고리 분류 기준으로 사용하지 않는다.

## 사용 예시

```python
from index_classifier import clean_report_file

result = clean_report_file(
    input_path="downloads/raw_report.xlsx",
    index_path="examples/category-index.example.json",
)

print(result.cleaned_report_path)
print(result.failed_rows_path)
print(result.index_log_path)
```

필요한 컬럼만 따로 지정할 수도 있다.

```python
from index_classifier import CleaningConfig, ReportRowCleaner, load_index

index = load_index("examples/category-index.example.json")
cleaner = ReportRowCleaner(
    index=index,
    config=CleaningConfig(
        output_fields=(
            "campaign_type",
            "campaign_name",
            "group_name",
            "keyword_name",
            "url",
            "category",
            "classification_confidence",
            "classification_source",
        )
    ),
)

cleaner.clean_file("downloads/raw_report.csv")
```
