<p align="center">
	<img width="200" height="200" alt="Jemyeonso AI Logo" src="https://github.com/user-attachments/assets/fbc5e739-c8d0-4267-862b-6b75ff25594f" align="center">

</p>
<p align="center"><h1 align="center">Jemyeonso-AI</h1></p>
<p align="center">
	<em>AI-Powered Resume-Based Interview Preparation System<br>이력서 기반 인공지능 면접 준비 플랫폼</em>
	<p align="center">
  <a href="https://disquiet.io/product/%EC%A0%9C%EB%A9%B4%EC%86%8C">
    <img src="https://disquiet.io/assets/gold-badge-BDLfTZOJ.svg" alt="Disquiet Product of the Week - Gold Badge" width="150" />
  </a>
</p>
</p>
<p align="center">
	<img src="https://img.shields.io/github/last-commit/je-myeon-so/Jemyeonso-AI?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/je-myeon-so/Jemyeonso-AI?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/badge/Version-v1.0.0%20Complete-success?style=flat&logo=checkmarx&logoColor=white" alt="version">
</p>
<p align="center">Tech Stack:</p>
<p align="center">
	<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
	<img src="https://img.shields.io/badge/OpenAI-412991.svg?style=flat&logo=OpenAI&logoColor=white" alt="OpenAI">
	<img src="https://img.shields.io/badge/Transformers-FF6F00.svg?style=flat&logo=huggingface&logoColor=white" alt="Transformers">
	<img src="https://img.shields.io/badge/PyTorch-EE4C2C.svg?style=flat&logo=PyTorch&logoColor=white" alt="PyTorch">
	<br>
	<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/MySQL-4479A1.svg?style=flat&logo=MySQL&logoColor=white" alt="MySQL">
	<img src="https://img.shields.io/badge/Amazon%20S3-569A31.svg?style=flat&logo=Amazon-S3&logoColor=white" alt="S3">
</p>
<br>

## 🔗 Table of Contents

- [📍 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#-prerequisites)
  - [⚙️ Installation](#-installation)
  - [🤖 Usage](#-usage)
- [📊 API Documentation](#-api-documentation)
- [🔧 Development](#-development)
- [🧪 Testing](#-testing)
- [📌 Project Status](#-project-status)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---
> **🌐 For International Viewers:** This repository is primarily documented in Korean as per team requirements. For the best reading experience, please use your browser's page translation feature (Chrome: right-click → "Translate to English" | Firefox/Safari: similar options available). All code comments, commit messages, and wiki documentation are also in Korean.

## 📍 Overview

**Jemyeonso-AI**는 인공지능 기반 면접 준비 플랫폼으로, 사용자의 이력서를 분석하여 맞춤형 면접 질문을 생성하고 답변에 대한 피드백을 제공합니다. OpenAI GPT와 Hugging Face Transformers를 활용하여 개인화된 면접 연습 환경을 제공합니다.

### Core Purpose
- **이력서 기반 질문 생성**: 업로드된 이력서를 분석하여 직무별 맞춤 면접 질문 자동 생성
- **AI 답변 분석**: 사용자 답변에 대한 상세한 피드백과 개선 제안 제공
- **개인정보 보호**: 이력서 내 민감 정보 탐지 및 보호 기능
- **캐싱 최적화**: 질문 생성 캐싱을 통한 빠른 응답 속도
- **클라우드 스토리지**: S3를 통한 안전한 파일 저장 및 관리

---

## ✨ Key Features

### Intelligent Question Generation
- **이력서 분석**: PDF 파일을 파싱하여 경력, 기술 스택, 프로젝트 경험 추출
- **직무별 맞춤화**: 지원 직무에 맞는 기술/인성/상황 면접 질문 생성
- **난이도 조절**: 초급, 중급, 고급 수준별 질문 제공
- **연속 질문**: 이전 질문과 답변을 고려한 심화 질문 생성

### AI-Powered Answer Analysis
- **상세 피드백**: 답변의 구조, 내용, 표현력에 대한 종합 분석
- **개선 제안**: 구체적이고 실행 가능한 답변 개선 방향 제시
- **강점/약점 분석**: 답변에서 드러나는 역량과 보완점 식별
- **점수화**: 객관적인 평가 점수와 근거 제공

### Privacy & Security
- **PII 탐지**: 이력서 내 개인식별정보 자동 탐지 및 로깅
- **데이터 보호**: 민감 정보 처리 시 보안 프로토콜 적용
- **파일 관리**: S3를 통한 안전한 파일 저장 및 접근 제어

### Performance Optimization
- **질문 캐싱**: 생성된 질문 캐싱을 통한 응답 속도 향상
- **메모리 관리**: 효율적인 캐시 관리 및 만료 처리
- **비동기 처리**: FastAPI 기반 고성능 비동기 API

---

## 🏗️ Architecture
- TBA
---

## 📁 Project Structure

```sh
jemyeonso-ai/
├── 📦 app/                           # 메인 애플리케이션
│   ├── 🧠 core/                      # 핵심 서비스
│   │   ├── llm_utils.py             # LLM 유틸리티
│   │   ├── mysql_database.py        # MySQL 데이터베이스 연결
│   │   ├── mysql_utils.py           # MySQL 유틸리티
│   │   ├── question_cache.py        # 질문 캐싱 시스템
│   │   ├── regex_utils.py           # 정규식 유틸리티
│   │   └── s3_utils.py              # S3 스토리지 유틸리티
│   │
│   ├── 🎤 interview/                 # 면접 관련 로직
│   │   ├── answer_analyzer.py       # 답변 분석 엔진
│   │   ├── prompt_loader.py         # 프롬프트 관리
│   │   └── question_generator.py    # 질문 생성 엔진
│   │
│   ├── 📄 resume/                    # 이력서 처리
│   │   ├── parser.py                # PDF 파싱
│   │   ├── pii_detector.py          # 개인정보 탐지
│   │   └── pii_logger.py            # PII 로깅
│   │
│   ├── 🌐 router/                    # API 엔드포인트
│   │   ├── health.py                # 헬스체크
│   │   ├── interview.py             # 면접 API
│   │   ├── pii_check.py             # PII 체크 API
│   │   ├── resume.py                # 이력서 API
│   │   └── s3_connection.py         # S3 연결 API
│   │
│   ├── 📋 schemas/                   # 데이터 모델
│   │   ├── interview.py             # 면접 스키마
│   │   └── resume.py                # 이력서 스키마
│   │
│   └── 🧪 tests/                     # 테스트 파일
│       ├── api/                     # API 테스트
│       ├── integration/             # 통합 테스트
│       ├── unit/                    # 단위 테스트
│       └── *.http                   # HTTP 테스트 파일
│
├── 🐳 Dockerfile                     # 컨테이너 설정
├── 📋 requirements.txt               # Python 의존성
├── ⚙️ config.py                     # 설정 파일
└── 🚀 main.py                       # 메인 애플리케이션
```

---

## 🚀 Getting Started

### ☑️ Prerequisites

- **Python 3.12+** 및 pip 패키지 매니저
- **Docker & Docker Compose** (선택사항)
- **MySQL Database** 데이터 저장용
- **AWS S3 Bucket** 파일 저장용
- **OpenAI API Key** AI 모델 사용

### ⚙️ Installation

#### Quick Start

```bash
# 저장소 클론
git clone https://github.com/je-myeon-so/jemyeonso-ai.git
cd jemyeonso-ai

# 가상환경 설정
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env에 필요한 설정 입력:
# OPENAI_API_KEY=your_openai_key
# MYSQL_HOST=localhost
# MYSQL_USER=your_user
# MYSQL_PASSWORD=your_password
# AWS_ACCESS_KEY_ID=your_aws_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret
```

#### Docker Setup

```bash
# 컨테이너 빌드 및 실행
docker build -t jemyeonso-ai .
docker run -p 8000:8000 --env-file .env jemyeonso-ai
```

### 🤖 Usage

#### Starting the Server

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### API 접속
- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000/health

---

## 📌 Project Status

### ✅ Current Features
- [x] **이력서 업로드 및 파싱**: PDF 파일 처리 및 텍스트 추출
- [x] **AI 질문 생성**: OpenAI GPT 기반 맞춤형 면접 질문 생성
- [x] **답변 분석**: 사용자 답변에 대한 AI 피드백 제공
- [x] **개인정보 탐지**: 이력서 내 PII 정보 자동 탐지
- [x] **질문 캐싱**: 성능 최적화를 위한 캐시 시스템
- [x] **S3 통합**: 파일 저장 및 관리
- [x] **MySQL 연동**: 데이터 영속성 보장

### 🚀 Future Enhancements
- [ ] **버전 2** 09/04 출시 예정

---

## 🙌 Acknowledgments

### AI Models & Services
- **OpenAI GPT**: 고품질 자연어 생성 및 분석
- **Hugging Face Transformers**: 오픈소스 NLP 모델 생태계
- **KiwiPie**: 한국어 자연어 처리

### Development Stack
- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **PDFPlumber**: PDF 텍스트 추출
- **MySQL**: 안정적인 관계형 데이터베이스
- **Amazon S3**: 확장 가능한 클라우드 스토리지

### Libraries & Tools
- **PyTorch**: 딥러닝 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버
- **Docker**: 컨테이너화 플랫폼

---

<p align="center">
<strong>Jemyeonso-AI</strong><br>
<em>인공지능 기반 면접 준비 플랫폼</em>
</p>
