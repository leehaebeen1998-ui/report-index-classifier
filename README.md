# 보고서 인덱스 분류 모듈

광고 보고서 업로드 시 매체별 컬럼명과 구조가 달라도 카테고리를 자동 분류하기 위한 독립 재사용 모듈입니다.

이 저장소의 1차 목표는 완성형 응용 프로그램이 아니라, 다른 프로그램에서 호출할 수 있는 공통 파츠인 `index_classifier`를 제공하는 것입니다.

핵심 원칙은 다음과 같습니다.

- 계정 ID와 브랜드 ID는 분류 기준이 아니라 인덱스 검색 범위 제한에만 사용합니다.
- 강제 URL 매핑은 모든 규칙보다 먼저 적용합니다.
- 공통 로직, 브랜드별 예외 규칙, AI 보정을 조합합니다.
- 사용자가 수정한 분류 결과는 다음 업로드부터 재사용할 수 있게 인덱스에 누적합니다.

## 1차 모듈 범위

- 보고서 컬럼 자동 인식
- 강제 URL 매핑
- 캠페인 유형 분류
- 그룹명 분류
- 키워드명 분류
- 캠페인명 분류
- 일반 URL 분류
- 규칙 실패 시 AI 분석 어댑터 호출
- 사용자가 수정한 결과를 인덱스에 저장

## 2차 응용 프로그램 범위

다음 기능은 이 모듈을 호출하는 별도 응용 프로그램에서 담당합니다.

- 보고서 파일 업로드
- 분류 결과 확인 화면
- 사용자 수정 UI
- 최종 보고서 다운로드
- 스케줄러/자동화 연결

## 사용 예시

```python
from index_classifier import classify_row, load_index

index = load_index("examples/category-index.example.json")
row = {
    "매체": "Naver SA",
    "광고그룹": "형사_구속",
    "랜딩URL": "https://example.com/criminal",
}

result = classify_row(row, index)
print(result.to_dict())
```

여러 인덱스 중 브랜드/계정 범위로 후보를 고를 수는 있지만, 이 값은 분류 기준으로 사용하지 않습니다.

```python
from index_classifier import filter_indexes_by_scope

candidate_indexes = filter_indexes_by_scope(
    indexes,
    brand_id="brand_law_001",
    account_id="naver_001",
)
```

문서:

- [인덱스 분류 설계](docs/index-classification-design.md)
- [보고서 로우 정제 모듈](docs/report-row-cleaning-module.md)
- [인덱스 JSON 스키마](schemas/category-index.schema.json)
- [인덱스 예시](examples/category-index.example.json)
