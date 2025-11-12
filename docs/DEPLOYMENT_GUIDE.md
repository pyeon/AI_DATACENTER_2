# 🚀 최종 배포 가이드 - 단계별 완벽 가이드

## ✅ 생성된 모든 파일 목록

### 📁 핵심 파일들 (outputs 디렉토리에 모두 생성됨)

```
outputs/
├── Python 스크립트 (scripts/ 폴더에 넣기)
│   ├── datacenter_report_enhanced.py
│   └── stock_selection_system.py
│
├── GitHub Actions 워크플로우 (.github/workflows/ 폴더에 넣기)
│   ├── daily_report.yml
│   ├── monthly_selection.yml
│   └── manual_run.yml
│
├── 설정 파일 (루트 디렉토리에 넣기)
│   ├── requirements.txt
│   ├── .gitignore
│   └── README.md
│
└── 문서 (docs/ 폴더에 넣기)
    ├── investment_system_guide.md
    ├── quick_start_guide.md
    └── github_deployment_guide.md
```

---

## 🎯 3가지 배포 방법

### 방법 1: GitHub 웹에서 직접 업로드 (가장 간단!)

#### Step 1: GitHub 저장소 생성
1. https://github.com 접속
2. 우측 상단 `+` → `New repository`
3. 저장소 정보 입력:
   ```
   Repository name: datacenter-investment
   Description: 데이터센터 투자 자동화 시스템
   Public ✅ (또는 Private)
   Add a README file ✅
   ```
4. `Create repository` 클릭

#### Step 2: 폴더 구조 생성
1. 저장소 메인 페이지에서 `Add file` → `Create new file`
2. 다음 폴더들을 순서대로 생성:

**폴더 1: .github/workflows/**
```
파일명 입력: .github/workflows/.gitkeep
(아무 내용 없이 Commit 클릭)
```

**폴더 2: scripts/**
```
파일명 입력: scripts/.gitkeep
(아무 내용 없이 Commit 클릭)
```

**폴더 3: docs/**
```
파일명 입력: docs/.gitkeep
(아무 내용 없이 Commit 클릭)
```

**폴더 4: outputs/**
```
파일명 입력: outputs/.gitkeep
(아무 내용 없이 Commit 클릭)
```

#### Step 3: 파일 업로드

**A. Python 스크립트 업로드**
1. `scripts/` 폴더 진입
2. `Add file` → `Upload files`
3. 다음 파일 드래그:
   - `datacenter_report_enhanced.py`
   - `stock_selection_system.py`
4. `Commit changes` 클릭

**B. GitHub Actions 워크플로우 업로드**
1. `.github/workflows/` 폴더 진입
2. `Add file` → `Upload files`
3. 다음 파일 드래그:
   - `daily_report.yml`
   - `monthly_selection.yml`
   - `manual_run.yml`
4. `Commit changes` 클릭

**C. 설정 파일 업로드**
1. 루트 디렉토리로 이동 (저장소 이름 클릭)
2. `Add file` → `Upload files`
3. 다음 파일 드래그:
   - `requirements.txt`
   - `.gitignore`
4. `README.md` 파일 교체:
   - 기존 README.md 클릭 → 연필 아이콘(Edit) → 내용 전체 삭제
   - 새 README.md 내용 복사 & 붙여넣기
   - `Commit changes` 클릭

**D. 문서 파일 업로드**
1. `docs/` 폴더 진입
2. `Add file` → `Upload files`
3. 다음 파일 드래그:
   - `investment_system_guide.md`
   - `quick_start_guide.md`
   - `github_deployment_guide.md`
4. `Commit changes` 클릭

#### Step 4: Secrets 설정
1. 저장소에서 `Settings` 탭 클릭
2. 좌측 메뉴에서 `Secrets and variables` → `Actions` 클릭
3. `New repository secret` 버튼 클릭
4. 다음 두 개의 Secret 추가:

**Secret 1:**
```
Name: TELEGRAM_BOT_TOKEN
Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz (실제 토큰)
```
Save 클릭

**Secret 2:**
```
Name: TELEGRAM_CHAT_ID
Value: 123456789 (실제 chat ID)
```
Save 클릭

#### Step 5: 수동 실행 테스트
1. `Actions` 탭 클릭
2. `🎯 Manual Run` 클릭
3. 오른쪽 `Run workflow` 버튼 클릭
4. Branch: main, Task: daily_report 선택
5. 초록색 `Run workflow` 버튼 클릭
6. 페이지 새로고침 → 실행 중인 작업 확인
7. 작업 클릭 → 실시간 로그 확인
8. 완료 후 `Artifacts` 섹션에서 Excel 다운로드
9. 텔레그램 메시지 확인

✅ **성공!** 이제 자동 실행이 설정되었습니다!

---

### 방법 2: Git CLI로 배포 (터미널 사용)

```bash
# 1. GitHub 저장소 생성 (웹에서 먼저 생성)
# https://github.com/new

# 2. 로컬 폴더 생성 및 초기화
mkdir datacenter-investment
cd datacenter-investment
git init

# 3. 폴더 구조 생성
mkdir -p .github/workflows scripts docs outputs

# 4. 파일 복사 (downloads 폴더에서)
# outputs 디렉토리의 파일들을 적절한 위치로 복사
cp ~/Downloads/datacenter_report_enhanced.py scripts/
cp ~/Downloads/stock_selection_system.py scripts/
cp ~/Downloads/daily_report.yml .github/workflows/
cp ~/Downloads/monthly_selection.yml .github/workflows/
cp ~/Downloads/manual_run.yml .github/workflows/
cp ~/Downloads/requirements.txt .
cp ~/Downloads/.gitignore .
cp ~/Downloads/README.md .
cp ~/Downloads/investment_system_guide.md docs/
cp ~/Downloads/quick_start_guide.md docs/
cp ~/Downloads/github_deployment_guide.md docs/

# 5. outputs 폴더에 .gitkeep 생성
touch outputs/.gitkeep

# 6. Git 설정
git add .
git commit -m "Initial commit: 데이터센터 투자 시스템"

# 7. GitHub 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/datacenter-investment.git
git branch -M main
git push -u origin main

# 8. Secrets 설정 (GitHub 웹에서)
# Settings → Secrets → Actions → New repository secret
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID

# 9. 테스트
# Actions 탭에서 Manual Run 실행
```

---

### 방법 3: GitHub CLI로 배포 (가장 고급)

```bash
# 1. GitHub CLI 설치
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
sudo apt install gh

# 2. 로그인
gh auth login

# 3. 저장소 생성 (자동)
gh repo create datacenter-investment --public --description "데이터센터 투자 자동화 시스템"

# 4. 클론
gh repo clone YOUR_USERNAME/datacenter-investment
cd datacenter-investment

# 5. 폴더 구조 생성
mkdir -p .github/workflows scripts docs outputs

# 6. 파일 복사 (방법 2와 동일)
# ... 파일 복사 ...

# 7. 커밋 & 푸시
git add .
git commit -m "Initial commit: 데이터센터 투자 시스템"
git push

# 8. Secrets 설정 (CLI로)
gh secret set TELEGRAM_BOT_TOKEN
# 프롬프트가 나오면 토큰 입력

gh secret set TELEGRAM_CHAT_ID
# 프롬프트가 나오면 Chat ID 입력

# 9. 워크플로우 수동 실행
gh workflow run "manual_run.yml" -f task=daily_report

# 10. 실행 상태 확인
gh run list --limit 5
gh run view

# 11. Artifacts 다운로드
gh run download
```

---

## 🎮 사용 방법

### 매일 자동 실행 (설정 완료 후 자동!)
- **시간**: 매일 15:00 (한국시간)
- **동작**: 
  1. 26개 종목 데이터 수집
  2. 16개 지표 분석
  3. Excel 파일 생성 (Artifacts)
  4. 텔레그램 메시지 전송

### 매월 자동 실행 (설정 완료 후 자동!)
- **시간**: 매월 1일 10:00 (한국시간)
- **동작**:
  1. 각 세부영역별 후보 종목 평가
  2. 100점 만점으로 점수 계산
  3. 최고 점수 종목 자동 선정
  4. Excel 파일 생성 (Artifacts)
  5. GitHub Issue로 알림

### 수동 실행 (언제든 원할 때!)
1. **Actions 탭** 이동
2. 원하는 워크플로우 선택:
   - `📊 Daily Datacenter Report`: 일일 리포트
   - `🔍 Monthly Stock Selection`: 종목 선정
   - `🎯 Manual Run`: 둘 다 또는 선택
3. **Run workflow** 버튼 클릭
4. 옵션 선택 후 실행

### 결과 확인
1. **텔레그램**: 실시간 메시지 수신
2. **Artifacts**: 
   - Actions → 완료된 실행 클릭
   - Artifacts 섹션에서 ZIP 다운로드
   - 압축 해제 후 Excel 파일 확인

---

## 📥 Excel 파일 다운로드 위치

### GitHub Actions에서 실행할 때
```
위치: Artifacts (30일 보관)

다운로드 방법:
1. Actions 탭
2. 완료된 워크플로우 클릭
3. 아래 Artifacts 섹션
4. daily-report-123 (또는 stock-selection-456) 클릭
5. ZIP 다운로드
6. 압축 해제
```

### 로컬에서 실행할 때
```
위치: outputs/ 디렉토리

파일명:
- datacenter_report_20251112.xlsx
- selected_stocks_20251112.xlsx
```

---

## 🔍 자주 묻는 질문

### Q1: "Ctrl+Enter"로 실행할 수 있나요?
**A**: 아니요. GitHub에서는 다음 방법으로 실행합니다:
1. **자동 실행**: 정해진 시간에 자동 (설정 필요 없음)
2. **수동 실행**: Actions 탭 → Run workflow 클릭
3. **로컬 실행**: 저장소 클론 후 `python scripts/...` 실행

### Q2: Excel 파일이 어디에 저장되나요?
**A**: GitHub Actions에서 실행 시:
- **임시 저장**: 실행 중 생성
- **Artifacts로 업로드**: 30일간 보관
- **Git에는 커밋 안 됨**: 저장소 크기 관리

원한다면 Git에 커밋할 수도 있습니다:
1. `.gitignore`에서 `outputs/*.xlsx` 줄 삭제
2. 워크플로우에 Git push 단계 추가

### Q3: 종목을 바꾸려면?
**A**: 
1. **매월 자동**: 매월 1일에 자동으로 최적 종목 선정
2. **수동 변경**:
   - `scripts/datacenter_report_enhanced.py` 파일 열기
   - `STOCKS` 리스트 수정
   - Git push

### Q4: 텔레그램 없이 사용 가능한가요?
**A**: 가능합니다!
1. 워크플로우에서 텔레그램 관련 env 제거
2. Python 파일에서 텔레그램 전송 부분 주석 처리
3. Excel만 Artifacts로 받기

### Q5: 실행 시간을 변경하려면?
**A**: 워크플로우 파일 수정:
```yaml
# .github/workflows/daily_report.yml
on:
  schedule:
    - cron: '0 6 * * *'  # 이 부분 수정
    # '시간 분 일 월 요일' (UTC 기준)
    # 한국시간 = UTC + 9
```

### Q6: 비용이 드나요?
**A**: 
- **Public 저장소**: 완전 무료!
- **Private 저장소**: 
  - 무료 계정: 월 2,000분 제공
  - 일일 리포트: 약 1~2분 소요
  - 충분히 무료로 사용 가능

---

## ✅ 배포 완료 체크리스트

```
[ ] 1. GitHub 저장소 생성
[ ] 2. 폴더 구조 생성 (.github/workflows, scripts, docs, outputs)
[ ] 3. Python 스크립트 업로드 (scripts/)
[ ] 4. GitHub Actions 워크플로우 업로드 (.github/workflows/)
[ ] 5. 설정 파일 업로드 (requirements.txt, .gitignore)
[ ] 6. README.md 업데이트
[ ] 7. 문서 파일 업로드 (docs/)
[ ] 8. Secrets 설정 (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
[ ] 9. 수동 실행 테스트 (Actions → Manual Run)
[ ] 10. Artifacts 다운로드 확인
[ ] 11. 텔레그램 메시지 수신 확인
[ ] 12. 자동 실행 대기 (다음 스케줄 시간)
```

---

## 🎉 완료!

모든 설정이 끝났습니다! 이제:

✅ **매일 15:00**: 자동으로 분석 리포트 생성 & 텔레그램 전송
✅ **매월 1일 10:00**: 자동으로 최적 종목 선정
✅ **언제든**: Actions에서 수동 실행 가능
✅ **Excel**: Artifacts에서 다운로드

**Happy Investing! 📈💰**
