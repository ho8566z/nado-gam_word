# 나도 감 (nado-gam) 문서

> **"나도 갈래!"** — 지구본으로 비행 경로를 보고 항공편·투어·호텔·크루즈를 한 흐름으로 예약하는 여행사 웹 서비스, **나도 감**의 문서 저장소입니다.
> 코드는 [`nado-gam`](https://github.com/ho8566z/nado-gam) 레포에 있고, 이 레포에는 기능정의서·DB 설계서·엑셀 명세서·발표 자료를 둡니다.

## 저장소 구성

| 폴더 | 내용 |
|---|---|
| [`design/`](design) | 기능정의서(`01`) · DB설계서(`02`) · 더미데이터설계서(`03`), ERD 이미지, 더미 데이터·명세서 생성 파이썬 스크립트 |
| [`excel_output/`](excel_output) | 엑셀 명세서(요구·기능·화면·API·테이블)와 시트별 요약본(프로젝트 개요·WBS·트러블슈팅 포함) |
| [`ppt_output/`](ppt_output) | 발표 PPT(`나도감_발표.pptx` / `.pdf`), 슬라이드 이미지(`나도감_발표/`), 구성안 |

## 명세 규모

| 요구사항 | 기능 | 화면 | API | 테이블 |
|:---:|:---:|:---:|:---:|:---:|
| 88건 | 48개 | 115행 | 56개 | 25개 |

문서 원본은 `design/`의 마크다운과 파이썬 스크립트이며, 엑셀은 스크립트(`gen_spec_xlsx.py`)로 다시 만들 수 있습니다.

## 발표 자료

[PPTX](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C.pptx) · [PDF](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C.pdf) — 32장, PART 1 기획 · PART 2 시연 및 설계 · PART 3 구현 및 평가

### PART 1. 기획

| | |
|---|---|
| ![표지](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C1.PNG) | ![목차](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C2.PNG) |
| 표지 | 목차 |
| ![프로젝트 소개](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C4.PNG) | ![주제 선정 배경](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C5.PNG) |
| 프로젝트 소개 (규모 숫자) | 주제 선정 배경과 필요성 |
| ![목표](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C6.PNG) | ![벤치마킹](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C7.PNG) |
| 목표 4가지 | 유사 서비스 벤치마킹 (하나투어·트립닷컴·놀유니버스) |
| ![차별점](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C8.PNG) | ![활용 방안·기대 효과](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C9.PNG) |
| 유사 서비스와의 차별점 | 활용 방안 · 기대 효과 · 확장성 |

### PART 2. 시연 및 설계

| | |
|---|---|
| ![핵심 사용자 시나리오](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C11.PNG) | ![시연 흐름](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C12.PNG) |
| 핵심 사용자 시나리오 | 시연 흐름 |
| ![시연 ①](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C13.PNG) | ![시연 ②](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C14.PNG) |
| 시연 ① 메인 · 해외 여행 | 시연 ② 투어 · 장바구니 · 결제 |
| ![시연 ③](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C15.PNG) | ![서비스 구성도](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C16.PNG) |
| 시연 ③ 예약 · QR · 관리자 · 모바일 | 서비스 구성도 |
| ![메뉴·화면 구성](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C17.PNG) | ![ERD](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C18.PNG) |
| 메뉴 · 화면 구성 | ERD (테이블 25개) |
| ![명세서 요약](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C19.PNG) | ![API 개요](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C20.PNG) |
| 명세서 요약 | API 개요 |
| ![WBS](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C21.PNG) | ![유스케이스](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C22.PNG) |
| 수행 절차 · 일정 (WBS) | 유스케이스 |
| ![단위업무 워크플로우](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C23.PNG) | ![패키지 구조](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C24.PNG) |
| 단위업무 워크플로우 | 패키지 구조 |

### PART 3. 구현 및 평가

| | |
|---|---|
| ![개발 환경](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C26.PNG) | ![Git 전략](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C27.PNG) |
| 개발 환경 | Git 브랜치 전략과 커밋 규칙 |
| ![핵심 구현 3가지](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C28.PNG) | ![테스트·검증](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C29.PNG) |
| 핵심 구현 3가지 | 테스트 · 검증 결과 (169개 통과) |
| ![트러블슈팅](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C30.PNG) | ![성과·목표 달성도](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C31.PNG) |
| 트러블슈팅 | 성과 · 목표 달성도 |
| ![한계·개선·향후 확장](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C32.PNG) | |
| 한계 · 개선 계획 · 향후 확장 | |

## 기술 스택 (구현)

Java 17 · Spring Boot 4.1.2 · Spring Security · Spring Data JPA / JdbcClient · Thymeleaf · globe.gl · H2 / MySQL 8 · Gradle · JUnit 5

## 관련 저장소

- [`nado-gam`](https://github.com/ho8566z/nado-gam) — 구현 코드, 실행 방법
