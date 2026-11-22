# 나도 감 (nado-gam) 문서

![나도 감 표지](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C1.PNG)

[nado-gam](https://github.com/ho8566z/nado-gam) 프로젝트의 명세서와 발표 자료를 모아 둔 문서 저장소입니다. (2차 개인 프로젝트, 2026.11.19 ~ 11.22)

코드는 [nado-gam](https://github.com/ho8566z/nado-gam) 저장소에 있고, 이 저장소에는 기능정의서·DB 설계서·엑셀 명세서·발표 자료를 둡니다.

## 프로젝트 요약

**"나도 갈래!"** — 가고 싶은 여행지를 고르면 항공편·투어·호텔·크루즈를 보여 주고, 비행 경로를 3D 지구본으로 보여 주는 여행사 웹 서비스입니다. 모든 항공사·편명·호텔·투어 브랜드·가격은 가상 데이터입니다.

![주제 선정 배경](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C/%EC%8A%AC%EB%9D%BC%EC%9D%B4%EB%93%9C5.PNG)

- **해결하려는 문제**: 항공권·현지 투어·숙소를 각각 다른 화면에서 찾고 비교해야 하고, 노선이 글자와 표로만 나와 어느 도시에서 어느 도시로 가는지 감이 안 오며, 고른 뒤가 끊긴다.
- **핵심 기능**: 지구본 경로 보기, 여행지 먼저 고르는 예약 흐름, 장바구니 → 모의 결제 → 좌석 차감 → QR 예약 확인, 관리자 운영 기능
- **기술 스택**: Java 17, Spring Boot 4.1.2, Spring Security, JPA(쓰기)·JdbcClient(읽기), Thymeleaf, globe.gl, H2 / MySQL 8
- **규모**: 요구사항 88 · 기능 48 · 화면 115행 · API 56 · 테이블 25 · 자동 테스트 169개 통과
- **목적**: 취업용 포트폴리오

## 폴더 구성

```
design/
  01_기능정의서.md · 02_DB설계서.md · 03_더미데이터설계서.md   설계 문서
  erd.png, *.py                                               ERD 이미지, 더미 데이터·명세서 생성 스크립트
excel_output/
  나도감_명세서.xlsx                   명세서 전체(시트 13개)
  나도감_명세서 요약*.xlsx             시트별 요약본(개요·요구·기능·화면·API·테이블·WBS·트러블슈팅)
ppt_output/
  나도감_발표.pptx · nado-gam.pdf   발표 자료(32장)
  나도감_발표/                         슬라이드 이미지(슬라이드1~32.PNG)
  00_PPT_구성안.md                     PPT 구성안
```

문서 원본은 `design/`의 마크다운과 파이썬 스크립트이며, 엑셀은 스크립트(`gen_spec_xlsx.py`)로 다시 만들 수 있습니다.

## 명세서 (excel_output/나도감_명세서.xlsx)

| 시트 | 내용 |
| --- | --- |
| 프로젝트 개요 | 서비스 목표, 구성, 기술 스택, 규모, 확정·미정 항목 |
| WBS | 11/19~11/25 일정과 작업별 상태 |
| 요구 명세서 | 구분별 요구사항(ID, 권한, 세부 기능 요구사항) |
| 기능 목록 | 기능 ID, 설명, 관련 요구사항, 액터, 우선순위 |
| 화면 기능 명세서 | 화면별 영역·요소·사용자 동작·처리 규칙 |
| API 명세서 | 구분, Method, URI, 권한 |
| 기능 명세서(사용자) | 사용자 핵심 기능의 사전 조건, 입력, 처리 순서, 업무 규칙, 예외 |
| 기능 명세서(관리자) | 관리자 핵심 기능의 처리 순서, 업무 규칙, 예외 |
| 테이블 명세서 | 테이블과 컬럼(관리자 영역·사용자 영역·운영 마스터) |
| 설정·규약 | 포트, 환경변수, 구현 순서 등 개발 공통 기준 |
| 트러블슈팅 | 점검에서 찾은 문제, 원인, 해결 |
| ERD | 테이블 25개와 외래키 관계 |
| 와이어프레임 | 주요 화면 배치 |

## 발표 자료

[PPTX](ppt_output/%EB%82%98%EB%8F%84%EA%B0%90_%EB%B0%9C%ED%91%9C.pptx) · [PDF](ppt_output/nado-gam.pdf) — 32장, PART 1 기획 · PART 2 시연 및 설계 · PART 3 구현 및 평가

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

## 주요 결정

- 한 앱에서 경로로 분리(`/admin/**`)하고, 관리자 계정과 사용자 계정 테이블도 나눔
- 여행지를 먼저 고르면 그 여행지로 가는 항공편이 있는 출발지만 표시
- 결제는 장바구니 + 모의 결제(실제 결제 서비스·카드 정보 수집 없음), 가격은 서버가 DB 값으로 다시 계산
- 좌석 차감은 `seats_left >= 인원` 조건부 UPDATE, 하나라도 부족하면 결제 전체 거절
- 화면용 조회는 JdbcClient, 쓰기는 JPA로 역할 분리
- 모바일은 별도 `/m` 없이 반응형 + 하단 탭 바
- 항공사·호텔·투어 브랜드·가격은 모두 가상 데이터, 웹 조사는 참고만

## 관련 저장소

- [nado-gam](https://github.com/ho8566z/nado-gam) — 구현 코드, 실행 방법

## 작성자

이윤호 (개인 프로젝트)
