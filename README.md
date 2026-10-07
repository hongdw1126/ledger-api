# Ledger API — FastAPI + Supabase

> GitHub: https://github.com/hongdw1126/ledger-api · Render: https://ledger-api-rj2q.onrender.com

클라우드컴퓨팅실습 4주차 제출용 가계부 API입니다. FastAPI와 SQLAlchemy로 계좌, 카테고리, 거래를 관리하며 Supabase PostgreSQL에 데이터를 저장합니다.

## API 기능

- `POST/GET /accounts` — 계좌 생성·조회
- `POST/GET /categories` — 수입/지출 카테고리 생성·조회
- `POST /transactions`, `GET /accounts/{id}/transactions` — 거래 저장·조회
- `GET /accounts-with-tx` — 계좌와 거래의 1:N 중첩 응답
- `GET /stats/by-category` — 지출 카테고리별 GROUP BY 집계
- `GET /health` — 배포 상태 및 PostgreSQL 연결 확인

## 로컬 실행

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# .env의 DATABASE_URL을 Supabase Session pooler 주소로 교체
uvicorn main:app --reload
```

`http://127.0.0.1:8000/docs`에서 API를 시험할 수 있습니다. `.env`는 Git에 포함되지 않습니다.

## Render 배포

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variable: `DATABASE_URL` = Supabase Session pooler 연결 문자열

## 실습 기록

계좌와 거래를 분리해 하나의 계좌가 여러 거래를 가질 수 있는 1:N 관계로 모델링했습니다. SQLAlchemy 모델 클래스는 PostgreSQL 테이블과 대응하고, `ForeignKey`와 `relationship`이 이 관계를 표현합니다. 접속 문자열은 비밀번호가 포함된 비밀 정보이므로 `.env`와 Render 환경변수로 분리했습니다.

AI에게 워크북 요구사항을 바탕으로 API 구조와 배포 설정의 누락 여부를 점검받았습니다. 로컬 SQLite에서 계좌·카테고리·거래 생성, 중첩 조회와 집계 처리 함수를 실행해 검증했습니다. Render의 `/health`에서 PostgreSQL 연결을 확인했고, `/accounts`에서 계좌 3개를 조회했습니다.
