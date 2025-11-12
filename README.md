# 📊 데이터센터 투자 자동화 시스템 v2.0

![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

자동화된 데이터센터 관련 종목 분석 및 일일 리포트 생성 시스템입니다.

## ✨ 주요 기능

### 📈 일일 자동 리포트
- **실행**: 매일 한국시간 15:00 (미국장 마감 후)
- **출력**: 
  - Excel 파일 (종합분석 + 지표설명 + 통계)
  - 텔레그램 메시지 (실시간 알림)
- **분석 종목**: 26개 데이터센터 관련 주식
- **분석 지표**: 16개 (RSI, MACD, 볼린저밴드, 골든크로스 등)

### 🔍 월간 종목 선정
- **실행**: 매월 1일 한국시간 10:00
- **기능**: 100점 만점 평가로 최적 종목 자동 선정
- **평가 기준**: 시가총액(30점) + 거래량(20점) + 수익률(35점) + 기술지표(15점)

### 🎯 수동 실행
- **방법**: Actions 탭에서 "Run workflow" 클릭
- **옵션**: 일일 리포트 / 종목 선정 / 둘 다

## 📂 프로젝트 구조

```
datacenter-investment/
├── .github/workflows/      # GitHub Actions 워크플로우
│   ├── daily_report.yml
│   ├── monthly_selection.yml
│   └── manual_run.yml
├── scripts/                # Python 스크립트
│   ├── datacenter_report_enhanced.py
│   └── stock_selection_system.py
├── docs/                   # 문서
│   ├── investment_system_guide.md
│   ├── quick_start_guide.md
│   └── github_deployment_guide.md
├── outputs/                # 결과 파일 (Excel)
├── requirements.txt        # Python 패키지
└── README.md
```

## 🚀 빠른 시작

### 1. 저장소 설정

```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/datacenter-investment.git
cd datacenter-investment

# 필수 디렉토리 생성
mkdir -p outputs
```

### 2. Secrets 설정

GitHub 저장소에서:
1. `Settings` → `Secrets and variables` → `Actions`
2. 다음 Secrets 추가:
   - `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
   - `TELEGRAM_CHAT_ID`: 텔레그램 채팅 ID

### 3. 수동 실행 테스트

1. `Actions` 탭 이동
2. `🎯 Manual Run` 클릭
3. `Run workflow` 버튼 클릭
4. 작업 선택 후 실행

### 4. 결과 다운로드

- 실행 완료 후 `Artifacts` 섹션에서 Excel 파일 다운로드
- 텔레그램으로 실시간 알림 수신

## 📊 분석 지표

### 수익률 지표
- 1일, 1주, 1개월, 3개월 수익률

### 기술적 지표
- **RSI**: 과매수/과매도 판단 (30 이하: 매수, 70 이상: 매도)
- **MACD**: 추세 전환 포착
- **볼린저밴드**: 변동성 구간 분석
- **골든크로스/데드크로스**: 중기 추세 확인
- **이동평균선**: MA20, MA60, MA200 대비
- **모멘텀 스코어**: 종합 투자 매력도 (0~100점)

### 통합 매매 신호
각 종목마다 단기/중기/장기 관점의 종합 신호 제공
- 예: "단기과매도, 중기상승, 장기상승추세" → 매수 타이밍!

## 📱 텔레그램 메시지 예시

```
📊 데이터센터 종목 일일 리포트
🕐 2025-11-12 15:00
━━━━━━━━━━━━━━━

🔥 오늘 상승 TOP 5
🚀 NVIDIA (GPU): +5.79%
🚀 SK hynix (HBM메모리): +6.44%
...

⭐ 골든크로스 (25개)
• NVIDIA (GPU)
• AMD (GPU)
...

💪 강한 모멘텀 (8개)
• NVIDIA: 95점
• Broadcom: 88점
...

🎯 RSI 과매도 (매수기회)
• Intel: RSI 28.5
...

📂 대분류별 현황
• AI 인프라: 4/5개 상승 (평균 +3.2%)
• 전력/쿨링: 5/7개 상승 (평균 +1.8%)
...

📈 상승: 23개
📉 하락: 3개
📊 총 26개 종목
```

## 📈 종목 분류 체계

### 대분류 (5개)
1. **AI 인프라**: GPU, CPU, AI서버
2. **전력/쿨링**: 전력관리, 발전기, HVAC
3. **네트워크**: 스위치, 광통신, 광섬유
4. **메모리/스토리지**: HBM, 패키징, SSD
5. **DC 부동산**: 데이터센터 REIT

### 분석 종목 (26개)
- NVIDIA, AMD, Intel (AI칩)
- SK hynix, Samsung, Micron (HBM)
- Arista, Broadcom, Marvell (네트워크)
- Vertiv, Eaton (전력)
- Digital Realty, Equinix (REIT)
- 기타 11개 종목

## 🔄 자동 실행 스케줄

| 작업 | 실행 시간 | 설명 |
|------|-----------|------|
| 일일 리포트 | 매일 15:00 (KST) | 자동 분석 + 텔레그램 전송 |
| 종목 선정 | 매월 1일 10:00 (KST) | 최적 종목 자동 선정 |
| 수동 실행 | 언제든 | Actions에서 즉시 실행 |

## 📖 상세 문서

- **[종합 가이드](docs/investment_system_guide.md)**: 모든 지표 상세 설명 및 투자 전략
- **[빠른 시작](docs/quick_start_guide.md)**: 핵심 요약 및 즉시 적용법
- **[배포 가이드](docs/github_deployment_guide.md)**: GitHub 배포 및 실행 완벽 가이드

## 💡 활용 팁

### 단기 매매 (1일~1주)
- RSI < 30 + BB하단 → 매수 기회
- RSI > 70 + BB상단 → 단기 조정 가능성
- 거래량 200%↑ + 상승 → 추격 매수

### 중기 매매 (1주~1개월)
- 골든크로스 + MACD 양수 → 매수
- 모멘텀 80점↑ → 보유 강화
- 데드크로스 발생 → 매도

### 장기 투자 (3개월 이상)
- MA200 위 + 3개월 수익률 +20%↑ → 장기 보유
- 투자추천 TOP10에서 분산 투자

## 🛠️ 로컬 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 실행
python scripts/datacenter_report_enhanced.py
python scripts/stock_selection_system.py
```

## 🐛 문제 해결

### Q: Excel 파일이 어디에 저장되나요?
**A**: GitHub Actions 실행 후 `Artifacts` 탭에서 다운로드 가능 (30일 보관)

### Q: 텔레그램 메시지가 안 옵니다
**A**: Secrets 설정 확인 (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`)

### Q: Cron이 실행되지 않습니다
**A**: 
1. UTC 시간 확인 (한국 시간 - 9시간)
2. main 브랜치에 워크플로우 파일 확인
3. 저장소가 Public이거나 Actions 활성화 확인

## 📄 라이선스

MIT License

## 🙋 문의

- **Issues**: 버그 리포트 및 기능 제안
- **Discussions**: 사용 방법 질문

---

**Happy Investing! 📈💰**

Made with ❤️ by Claude
