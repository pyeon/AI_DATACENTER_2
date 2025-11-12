# 🚀 GitHub 배포 및 실행 완벽 가이드

## 📋 목차
1. [GitHub 저장소 구조](#github-저장소-구조)
2. [자동 실행 설정 (GitHub Actions)](#자동-실행-설정)
3. [수동 실행 방법](#수동-실행-방법)
4. [엑셀 파일 저장 및 다운로드](#엑셀-파일-저장-및-다운로드)
5. [문제 해결](#문제-해결)

---

## 📁 GitHub 저장소 구조

### 1. 최종 폴더 구조

```
datacenter-investment/
├── .github/
│   └── workflows/
│       ├── daily_report.yml          # 일일 리포트 (매일 자동)
│       ├── monthly_selection.yml     # 종목 선정 (매월 자동)
│       └── manual_run.yml            # 수동 실행용
│
├── scripts/
│   ├── datacenter_report_enhanced.py
│   └── stock_selection_system.py
│
├── docs/
│   ├── investment_system_guide.md
│   └── quick_start_guide.md
│
├── outputs/                          # 실행 결과 저장 (선택사항)
│   ├── .gitkeep
│   └── README.md
│
├── requirements.txt                  # Python 패키지
├── README.md
└── .gitignore
```

### 2. 필수 파일 내용

#### requirements.txt
```
yfinance>=0.2.28
pandas>=2.0.0
requests>=2.31.0
openpyxl>=3.1.0
```

#### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Output files (if you don't want to commit them)
outputs/*.xlsx
outputs/*.csv
!outputs/.gitkeep
!outputs/README.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets (중요!)
.env
secrets.txt
```

---

## ⚙️ 자동 실행 설정

### 방법 1: 일일 리포트 (매일 자동 실행)

**파일 위치**: `.github/workflows/daily_report.yml`

```yaml
name: 📊 Daily Datacenter Report

on:
  schedule:
    # 매일 한국시간 15:00 (미국장 마감 후)
    # UTC 06:00 = 한국시간 15:00
    - cron: '0 6 * * *'
  
  # 수동 실행 버튼 추가
  workflow_dispatch:

jobs:
  daily-report:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 코드 체크아웃
        uses: actions/checkout@v4
      
      - name: 🐍 Python 3.10 설정
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: 📦 패키지 설치
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 📊 일일 리포트 실행
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python scripts/datacenter_report_enhanced.py
      
      - name: 📁 결과 파일 업로드
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: daily-report-${{ github.run_number }}
          path: |
            outputs/*.xlsx
            outputs/*.csv
          retention-days: 30
      
      - name: ✅ 완료 알림
        if: success()
        run: |
          echo "✅ 일일 리포트 생성 완료!"
          echo "📁 Artifacts 탭에서 Excel 파일 다운로드 가능"
      
      - name: ❌ 실패 알림
        if: failure()
        run: |
          echo "❌ 일일 리포트 생성 실패"
          echo "🔍 로그를 확인하세요"
```

### 방법 2: 월간 종목 선정 (매월 1일 자동 실행)

**파일 위치**: `.github/workflows/monthly_selection.yml`

```yaml
name: 🔍 Monthly Stock Selection

on:
  schedule:
    # 매월 1일 한국시간 10:00
    # UTC 01:00 = 한국시간 10:00
    - cron: '0 1 1 * *'
  
  # 수동 실행 버튼
  workflow_dispatch:

jobs:
  monthly-selection:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 코드 체크아웃
        uses: actions/checkout@v4
      
      - name: 🐍 Python 3.10 설정
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: 📦 패키지 설치
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 🔍 종목 선정 실행
        run: |
          python scripts/stock_selection_system.py
      
      - name: 📁 결과 파일 업로드
        uses: actions/upload-artifact@v3
        with:
          name: stock-selection-${{ github.run_number }}
          path: |
            outputs/selected_stocks_*.xlsx
          retention-days: 90
      
      - name: 📝 Issue 생성 (선정 결과 알림)
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const date = new Date().toISOString().split('T')[0];
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `📊 ${date} 월간 종목 선정 완료`,
              body: `
              ## 🎯 월간 종목 선정이 완료되었습니다!
              
              ### 📥 다운로드
              - [Actions 탭](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})에서 Excel 파일 다운로드
              
              ### 📋 다음 단계
              1. Excel 파일 다운로드 및 검토
              2. 출력된 STOCKS 리스트 복사
              3. \`datacenter_report_enhanced.py\`의 STOCKS 변수 업데이트
              4. 변경사항 커밋
              
              ### 📅 다음 실행
              - 다음 달 1일 자동 실행 예정
              `
            });
      
      - name: ✅ 완료
        run: |
          echo "✅ 종목 선정 완료!"
          echo "📁 Artifacts에서 Excel 다운로드 가능"
```

### 방법 3: 수동 실행용 (언제든 클릭해서 실행)

**파일 위치**: `.github/workflows/manual_run.yml`

```yaml
name: 🎯 Manual Run (수동 실행)

on:
  workflow_dispatch:
    inputs:
      task:
        description: '실행할 작업 선택'
        required: true
        type: choice
        options:
          - daily_report
          - stock_selection
          - both
        default: 'daily_report'

jobs:
  manual-run:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 코드 체크아웃
        uses: actions/checkout@v4
      
      - name: 🐍 Python 3.10 설정
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: 📦 패키지 설치
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 📊 일일 리포트 실행
        if: ${{ github.event.inputs.task == 'daily_report' || github.event.inputs.task == 'both' }}
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          echo "📊 일일 리포트 실행 중..."
          python scripts/datacenter_report_enhanced.py
      
      - name: 🔍 종목 선정 실행
        if: ${{ github.event.inputs.task == 'stock_selection' || github.event.inputs.task == 'both' }}
        run: |
          echo "🔍 종목 선정 실행 중..."
          python scripts/stock_selection_system.py
      
      - name: 📁 결과 파일 업로드
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: manual-run-${{ github.run_number }}
          path: outputs/*.xlsx
          retention-days: 30
      
      - name: ✅ 완료
        run: |
          echo "✅ 수동 실행 완료!"
```

---

## 🔐 Secrets 설정

### 1. GitHub Secrets 등록

1. **저장소 페이지로 이동**
   ```
   https://github.com/YOUR_USERNAME/datacenter-investment
   ```

2. **Settings → Secrets and variables → Actions 클릭**

3. **New repository secret 클릭하여 추가**:
   
   **Secret 1: TELEGRAM_BOT_TOKEN**
   ```
   Name: TELEGRAM_BOT_TOKEN
   Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz (실제 토큰)
   ```
   
   **Secret 2: TELEGRAM_CHAT_ID**
   ```
   Name: TELEGRAM_CHAT_ID
   Value: 123456789 (실제 chat ID)
   ```

4. **Save 클릭**

---

## 🎮 수동 실행 방법

### 방법 1: GitHub 웹에서 클릭으로 실행

#### Step 1: Actions 탭으로 이동
```
https://github.com/YOUR_USERNAME/datacenter-investment/actions
```

#### Step 2: 실행할 워크플로우 선택
- **일일 리포트**: "📊 Daily Datacenter Report" 클릭
- **종목 선정**: "🔍 Monthly Stock Selection" 클릭
- **수동 실행**: "🎯 Manual Run" 클릭

#### Step 3: Run workflow 버튼 클릭
1. 오른쪽 상단 "Run workflow" 버튼 클릭
2. Branch 선택 (보통 `main`)
3. (수동 실행의 경우) 작업 선택
4. 초록색 "Run workflow" 버튼 클릭

#### Step 4: 실행 확인
- 페이지 새로고침하면 실행 중인 작업 표시
- 클릭하면 실시간 로그 확인 가능

### 방법 2: 터미널에서 gh CLI로 실행

```bash
# GitHub CLI 설치 (처음 한 번만)
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
sudo apt install gh

# 로그인
gh auth login

# 일일 리포트 실행
gh workflow run "daily_report.yml"

# 종목 선정 실행
gh workflow run "monthly_selection.yml"

# 수동 실행 (옵션 지정)
gh workflow run "manual_run.yml" -f task=daily_report
```

### 방법 3: 로컬에서 Python 직접 실행

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/datacenter-investment.git
cd datacenter-investment

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 5. 실행
python scripts/datacenter_report_enhanced.py
# 또는
python scripts/stock_selection_system.py

# 6. 결과 확인
ls -la outputs/
```

---

## 📥 엑셀 파일 저장 및 다운로드

### GitHub Actions에서 실행할 때

#### 📍 파일 저장 위치
```
GitHub Actions 실행 시:
- 임시 디렉토리에 생성: /home/runner/work/repo-name/outputs/
- Artifacts로 자동 업로드
- 실행 완료 후 임시 디렉토리는 삭제됨

저장소에 커밋하지 않음 (용량 관리를 위해)
```

#### 📥 다운로드 방법

**방법 1: 웹 UI에서 다운로드**

1. **Actions 탭 이동**
   ```
   https://github.com/YOUR_USERNAME/datacenter-investment/actions
   ```

2. **완료된 워크플로우 클릭**
   - 초록색 체크마크가 있는 실행 클릭

3. **Artifacts 섹션에서 다운로드**
   ```
   Artifacts (보관 기간: 30일)
   ├─ daily-report-123
   │  └─ datacenter_report_20251112.xlsx (1.2 MB)
   │     [Download] 버튼 클릭
   │
   └─ stock-selection-456
      └─ selected_stocks_20251112.xlsx (800 KB)
         [Download] 버튼 클릭
   ```

4. **ZIP 파일 압축 해제**
   - 다운로드한 ZIP 파일 압축 해제
   - Excel 파일 확인

**방법 2: gh CLI로 다운로드**

```bash
# 최근 실행의 artifacts 목록 보기
gh run list --limit 5

# 특정 실행의 artifacts 다운로드
gh run download RUN_ID

# 예시
gh run download 1234567890

# 결과
# 현재 디렉토리에 다운로드됨
# daily-report-123/
#   └─ datacenter_report_20251112.xlsx
```

**방법 3: GitHub API로 다운로드**

```bash
# 최신 artifact 자동 다운로드 스크립트
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip \
  -o artifact.zip

unzip artifact.zip
```

### 로컬에서 실행할 때

#### 📍 파일 저장 위치
```python
# datacenter_report_enhanced.py 내부
excel_filename = f'/mnt/user-data/outputs/datacenter_report_{date_str}.xlsx'

# 실제로는:
# - GitHub Actions: /home/runner/work/repo/repo/outputs/
# - 로컬 실행: 스크립트가 있는 디렉토리의 outputs/
```

#### 📂 수정 방법 (저장소에 커밋하고 싶은 경우)

**파일 수정**: `scripts/datacenter_report_enhanced.py`

```python
# 기존
excel_filename = f'/mnt/user-data/outputs/datacenter_report_{date_str}.xlsx'

# 변경 →
import os
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
excel_filename = f'{output_dir}/datacenter_report_{date_str}.xlsx'
```

그리고 `.gitignore`에서 제외:
```
# .gitignore에서 이 줄 제거
# outputs/*.xlsx
```

**⚠️ 주의**: Excel 파일을 Git에 커밋하면 저장소 크기가 계속 증가합니다!

---

## 🔄 자동화 스케줄 요약

| 작업 | 실행 시간 | 설명 | 파일 |
|------|-----------|------|------|
| **일일 리포트** | 매일 15:00 (KST) | 자동 실행 + 텔레그램 전송 | daily_report.yml |
| **종목 선정** | 매월 1일 10:00 (KST) | 자동 실행 + Issue 생성 | monthly_selection.yml |
| **수동 실행** | 원할 때 | 클릭으로 즉시 실행 | manual_run.yml |

### Cron 표현식 이해하기

```
┌───────────── 분 (0 - 59)
│ ┌───────────── 시 (0 - 23) UTC 기준!
│ │ ┌───────────── 일 (1 - 31)
│ │ │ ┌───────────── 월 (1 - 12)
│ │ │ │ ┌───────────── 요일 (0 - 6) (0=일요일)
│ │ │ │ │
* * * * *

예시:
'0 6 * * *'     → 매일 06:00 UTC = 15:00 KST
'0 1 1 * *'     → 매월 1일 01:00 UTC = 10:00 KST
'0 6 * * 1-5'   → 월~금 06:00 UTC (주말 제외)
'0 6,18 * * *'  → 매일 06:00, 18:00 UTC (하루 2번)
```

### 시간대 변환

```
한국 (KST) = UTC + 9시간

원하는 한국시간 → UTC로 변환:
15:00 KST → 06:00 UTC
10:00 KST → 01:00 UTC
22:00 KST → 13:00 UTC
```

---

## 📋 완전한 배포 체크리스트

### ✅ 초기 설정 (한 번만)

```bash
# 1. GitHub 저장소 생성
# - 저장소 이름: datacenter-investment
# - Public 또는 Private 선택

# 2. 로컬에서 초기화
cd /path/to/your/project
git init
git remote add origin https://github.com/YOUR_USERNAME/datacenter-investment.git

# 3. 필수 파일 생성
mkdir -p .github/workflows scripts docs outputs
touch outputs/.gitkeep

# 4. 파일 복사
# - datacenter_report_enhanced.py → scripts/
# - stock_selection_system.py → scripts/
# - 가이드 문서들 → docs/

# 5. 설정 파일 생성
cat > requirements.txt << EOF
yfinance>=0.2.28
pandas>=2.0.0
requests>=2.31.0
openpyxl>=3.1.0
EOF

cat > .gitignore << EOF
__pycache__/
*.py[cod]
venv/
.env
outputs/*.xlsx
!outputs/.gitkeep
.DS_Store
EOF

# 6. GitHub Actions 워크플로우 생성
# - daily_report.yml
# - monthly_selection.yml
# - manual_run.yml

# 7. README.md 작성
cat > README.md << EOF
# 📊 데이터센터 투자 자동화 시스템

자동화된 데이터센터 종목 분석 및 리포트 생성 시스템

## 기능
- 일일 자동 리포트 (텔레그램 + Excel)
- 월간 종목 자동 선정
- 16개 기술적 지표 분석

## 사용 방법
Actions 탭에서 "Run workflow" 클릭
EOF

# 8. 커밋 및 푸시
git add .
git commit -m "Initial commit: 데이터센터 투자 시스템"
git branch -M main
git push -u origin main
```

### ✅ GitHub Secrets 설정

```
1. Settings → Secrets and variables → Actions
2. New repository secret 클릭
3. TELEGRAM_BOT_TOKEN 추가
4. TELEGRAM_CHAT_ID 추가
5. Save
```

### ✅ 첫 실행 테스트

```
1. Actions 탭 이동
2. "🎯 Manual Run" 선택
3. "Run workflow" 클릭
4. task: daily_report 선택
5. "Run workflow" 클릭
6. 실행 완료 대기 (1~2분)
7. Artifacts에서 Excel 다운로드
8. 텔레그램 메시지 확인
```

---

## 🐛 문제 해결

### 문제 1: "yfinance 설치 실패"

**증상**:
```
ERROR: Could not find a version that satisfies the requirement yfinance
```

**해결**:
```yaml
# workflow 파일에서 Python 버전 확인
- uses: actions/setup-python@v4
  with:
    python-version: '3.10'  # 3.9 이상 필요
```

### 문제 2: "텔레그램 메시지가 안 옴"

**확인 사항**:
```bash
# 1. Secrets 확인
Settings → Secrets → TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 2. 토큰 테스트
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# 3. Chat ID 확인
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

**해결**:
- Secrets 이름이 정확한지 확인
- 토큰에 공백이 없는지 확인
- Chat ID가 숫자인지 확인 (문자열 X)

### 문제 3: "Artifacts가 없음"

**원인**:
```yaml
# path가 잘못됨
path: /mnt/user-data/outputs/*.xlsx  # ❌ GitHub Actions에서 작동 안함
```

**해결**:
```python
# Python 파일 수정
import os

# 상대 경로 사용
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
excel_file = f'{output_dir}/report_{date}.xlsx'
```

```yaml
# workflow 파일 수정
- name: 📁 결과 파일 업로드
  uses: actions/upload-artifact@v3
  with:
    path: outputs/*.xlsx  # ✅ 상대 경로
```

### 문제 4: "Cron이 실행 안 됨"

**확인**:
```
1. UTC 시간으로 계산했는지 확인
2. 저장소가 Public인지, 또는 Private이면 Actions 활성화했는지
3. main 브랜치에 워크플로우 파일이 있는지
```

**테스트**:
```bash
# 수동 실행으로 먼저 테스트
Actions → Run workflow → 수동 실행 성공 확인
→ Cron 스케줄 대기
```

### 문제 5: "Excel 파일을 Git에 커밋하고 싶음"

**방법 1: Artifacts 대신 커밋**

```yaml
- name: 📊 리포트 실행
  run: python scripts/datacenter_report_enhanced.py

- name: 💾 Git 커밋
  run: |
    git config user.name "GitHub Actions Bot"
    git config user.email "actions@github.com"
    git add outputs/*.xlsx
    git commit -m "📊 Update report $(date +%Y-%m-%d)" || echo "No changes"
    git push
```

**방법 2: GitHub Pages로 공개**

```yaml
- name: 🌐 GitHub Pages 배포
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./outputs
```

---

## 💡 추가 팁

### 1. 실행 시간 최적화

```yaml
# 거래 시간에만 실행 (주말 제외)
on:
  schedule:
    - cron: '0 6 * * 1-5'  # 월~금만
```

### 2. 실패 시 알림

```yaml
- name: 📧 실패 알림
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: ❌ Daily Report Failed
    body: Check the logs!
    to: your-email@gmail.com
```

### 3. 여러 텔레그램 채널에 전송

```python
# Python 코드 수정
CHAT_IDS = os.environ.get('TELEGRAM_CHAT_ID').split(',')

for chat_id in CHAT_IDS:
    payload = {"chat_id": chat_id.strip(), "text": message}
    requests.post(url, data=payload)
```

```yaml
# Secrets에 쉼표로 구분
TELEGRAM_CHAT_ID: "123456789,987654321,555555555"
```

---

## 📞 요약

| 질문 | 답변 |
|------|------|
| **깃허브에 업로드?** | ✅ 위 파일들을 `.github/workflows/`에 업로드 |
| **한 달에 한 번?** | ✅ `cron: '0 1 1 * *'` (매월 1일 10:00 KST) |
| **일자별 텔레그램?** | ✅ `cron: '0 6 * * *'` (매일 15:00 KST) |
| **수동 실행?** | ✅ Actions 탭 → Run workflow 클릭 |
| **엑셀 저장 위치?** | ✅ Artifacts (30일 보관) 또는 Git 커밋 |

**다음 단계**: GitHub 저장소 생성 후 파일 업로드하면 자동 실행됩니다! 🚀
