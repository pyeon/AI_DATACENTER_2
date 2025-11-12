# 🚀 빠른 시작 가이드

## 📦 제공 파일

### 1. datacenter_report_enhanced.py
**용도**: 일일 리포트 생성 (매일 실행)
**출력**:
- Excel 파일 (datacenter_report_YYYYMMDD.xlsx)
- 텔레그램 메시지 (개선된 버전)

### 2. stock_selection_system.py
**용도**: 종목 자동 선정 (월 1회 실행)
**출력**:
- Excel 파일 (selected_stocks_YYYYMMDD.xlsx)
- Python 코드 (STOCKS 리스트)

### 3. investment_system_guide.md
**용도**: 종합 사용 설명서
**내용**: 모든 지표 설명 및 투자 전략

---

## 🎯 즉시 적용 방법

### Step 1: 기존 코드 교체
```bash
# 기존 파일 백업
cp your_script.py your_script_backup.py

# 새 파일로 교체
cp datacenter_report_enhanced.py your_script.py
```

### Step 2: 첫 실행
```bash
# 환경변수 설정 (필요시)
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 실행
python datacenter_report_enhanced.py
```

### Step 3: Excel 파일 확인
- `/mnt/user-data/outputs/datacenter_report_YYYYMMDD.xlsx` 열기
- 4개 시트 확인:
  1. 종합분석
  2. 지표설명서
  3. 대분류별통계
  4. 투자추천TOP10

---

## 📊 주요 개선사항 요약

### ✅ 요청사항 1: Excel 리포트
**해결**: 4개 시트로 구성된 Excel 자동 생성
- 모든 분석 데이터 포함
- 색상/서식 자동 적용
- 열 너비 자동 조정

### ✅ 요청사항 2: 칼럼 의미 설명
**해결**: Excel 내 "지표설명서" 시트 추가
- 15개 지표 상세 설명
- 계산식, 해석, 투자활용 방법 포함

### ✅ 요청사항 3: 세부영역 구분
**해결**: 3단계 분류 체계
```
대분류 (5개) → 중분류 (7개) → 세부분류 (15개)

예시:
메모리/스토리지 → HBM → HBM메모리
AI 인프라 → AI칩 → GPU
```

### ✅ 요청사항 4: 추가 매매 지표
**해결**: 단기/중기/장기 지표 추가

#### 추가된 지표
| 구분 | 지표 | 용도 |
|------|------|------|
| 단기 | RSI | 과매수/과매도 |
| 단기 | BB Position | 변동성 구간 |
| 중기 | MACD | 추세 전환 |
| 중기 | Death Cross | 하락 신호 |
| 장기 | MA200 대비 | 장기 추세 |
| 장기 | 3개월 수익률 | 모멘텀 |
| 종합 | Momentum Score | 투자 매력도 |

#### 매매 신호 예시
```
"단기과매도, 중기상승, 장기상승추세"
→ 매수 타이밍!

"단기과매수, 중기하락, BB상단"
→ 단기 조정 가능성
```

### ✅ 요청사항 5: 종목 자동 선정
**해결**: stock_selection_system.py
- 100점 만점 평가 시스템
- 5가지 기준 (시가총액 30점, 거래량 20점 등)
- 각 세부영역별 최고 점수 종목 자동 선정

---

## 🔥 핵심 활용법

### 매일 확인할 것
1. **텔레그램 메시지**
   - 상승/하락 TOP 5
   - 골든크로스 종목
   - 강한 모멘텀 종목 (80점 이상)
   - RSI 과매도 종목 (매수 기회)

2. **Excel - 투자추천TOP10 시트**
   - 모멘텀 점수 상위 10개
   - 매매신호 확인

3. **Excel - 종합분석 시트**
   - 보유 종목 점검
   - 매매신호 변화 확인

### 매월 1일 할 것
1. **종목 선정 스크립트 실행**
   ```bash
   python stock_selection_system.py
   ```

2. **결과 확인 및 적용**
   - selected_stocks_YYYYMMDD.xlsx 열기
   - 점수 확인
   - 출력된 STOCKS 리스트를 메인 스크립트에 복사

3. **포트폴리오 리밸런싱**
   - 점수 낮은 종목 교체
   - 대분류별 균형 조정

---

## 💡 투자 시나리오

### 시나리오 1: 단기 매매
```
조건: RSI < 30 + BB하단 + 거래량 200%↑
행동: 매수 → 목표가 +5% → 익절

예시:
Intel: RSI 28.5, BB Position 15, 거래량 250%
→ 단기 매수 기회!
```

### 시나리오 2: 스윙 트레이딩
```
조건: 골든크로스 + MACD 양수 + 모멘텀 80점↑
행동: 매수 → 데드크로스 발생 시 매도

예시:
NVIDIA: 골든크로스, MACD +2.5, 모멘텀 95점
→ 중기 보유 전략
```

### 시나리오 3: 장기 투자
```
조건: MA200 위 + 3개월 수익률 20%↑ + 대분류 평균 이상
행동: 매수 후 장기 보유

예시:
SK hynix: MA200 대비 +15%, 3개월 +28%
→ 포트폴리오 핵심 종목
```

---

## 📈 텔레그램 메시지 개선 비교

### Before (기존)
```
⭐ 골든크로스 (25개)
• NVIDIA
• AMD
• Intel
```

### After (개선)
```
⭐ 골든크로스 (25개)
• NVIDIA (GPU)
• AMD (GPU)
• Intel (CPU)

💪 강한 모멘텀 (8개)
• NVIDIA: 95점
• Broadcom: 88점

🎯 RSI 과매도 (매수기회)
• Intel: RSI 28.5

📂 대분류별 현황
• AI 인프라: 4/5개 상승 (평균 +3.2%)
• 전력/쿨링: 5/7개 상승 (평균 +1.8%)
```

**개선점**:
- 세부영역 표시 (GPU, CPU 등)
- 모멘텀 점수 추가
- RSI 과매도 종목 (매수 기회)
- 대분류별 통계 추가

---

## 🎓 학습 로드맵

### Week 1: 기본 지표 이해
- RSI, MACD, 이동평균선
- Excel "지표설명서" 시트 정독
- 각 지표별 매매 신호 확인

### Week 2: 복합 신호 활용
- 골든크로스 + MACD 조합
- RSI + BB Position 조합
- 모멘텀 스코어 활용법

### Week 3: 실전 적용
- 소액으로 단기 매매 연습
- 매일 텔레그램 + Excel 점검
- 매매 일지 작성

### Week 4: 전략 고도화
- 종목 선정 시스템 활용
- 포트폴리오 구성
- 리밸런싱 전략 수립

---

## 🔧 문제 해결

### Q1: Excel 파일이 생성되지 않아요
```bash
# openpyxl 설치 확인
pip install openpyxl

# 경로 확인
ls -la /mnt/user-data/outputs/
```

### Q2: 일부 종목 데이터가 없어요
- 한국 종목: 장 시간 확인 (9:00~15:30)
- 미국 종목: 장 시간 확인 (23:30~06:00 한국시간)
- 일시적 오류: 재실행

### Q3: 텔레그램 메시지가 안 와요
```bash
# 환경변수 확인
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# 직접 테스트
curl "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text=test"
```

### Q4: 종목 선정 점수가 이상해요
- 시가총액 작은 종목: 정상 (점수 낮음)
- 최근 급락 종목: 정상 (수익률 음수)
- 거래량 적은 종목: 정상 (점수 낮음)

---

## 📚 추가 학습 자료

### 추천 도서
1. "Technical Analysis Explained" - Martin Pring
2. "Trading for a Living" - Alexander Elder

### 추천 사이트
1. Investopedia (기술적 지표 학습)
2. TradingView (차트 분석)
3. Seeking Alpha (종목 분석)

---

## ⚡ Quick Commands

```bash
# 일일 리포트 실행
python datacenter_report_enhanced.py

# 종목 선정 실행
python stock_selection_system.py

# Excel 파일 확인
ls -lh /mnt/user-data/outputs/*.xlsx

# 가장 최근 Excel 열기
open /mnt/user-data/outputs/datacenter_report_$(date +%Y%m%d).xlsx
```

---

## 📞 도움이 필요하면

1. `investment_system_guide.md` 전체 문서 참고
2. Excel "지표설명서" 시트 확인
3. GitHub Issue 등록

**Happy Trading! 🚀📈**
