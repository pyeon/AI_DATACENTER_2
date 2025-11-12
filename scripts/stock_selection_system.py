"""
데이터센터 종목 자동 선정 시스템 v1.0
- 월 1회 실행하여 각 세부영역별 최적 종목 선정
- 시가총액, 거래량, 수익률, 모멘텀 등을 종합 평가
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🔍 데이터센터 종목 자동 선정 시스템 v1.0")
print("="*80 + "\n")

# 각 세부영역별 후보 종목 Pool
CANDIDATE_POOLS = {
    # AI 인프라 - GPU
    'GPU': [
        {'name': 'NVIDIA', 'ticker': 'NVDA', 'exchange': 'US'},
        {'name': 'AMD', 'ticker': 'AMD', 'exchange': 'US'},
    ],
    
    # AI 인프라 - CPU
    'CPU': [
        {'name': 'Intel', 'ticker': 'INTC', 'exchange': 'US'},
        {'name': 'AMD', 'ticker': 'AMD', 'exchange': 'US'},
    ],
    
    # AI 인프라 - 서버제조
    '서버제조': [
        {'name': 'Super Micro', 'ticker': 'SMCI', 'exchange': 'US'},
        {'name': 'Dell', 'ticker': 'DELL', 'exchange': 'US'},
        {'name': 'HPE', 'ticker': 'HPE', 'exchange': 'US'},
        {'name': 'Lenovo', 'ticker': '0992.HK', 'exchange': 'HK'},
    ],
    
    # 전력/쿨링 - 전력관리
    '전력관리': [
        {'name': 'Vertiv', 'ticker': 'VRT', 'exchange': 'US'},
        {'name': 'Eaton', 'ticker': 'ETN', 'exchange': 'US'},
        {'name': 'Schneider Electric', 'ticker': 'SU.PA', 'exchange': 'EU'},
    ],
    
    # 전력/쿨링 - 전력기기
    '전력기기': [
        {'name': 'LS ELECTRIC', 'ticker': '010120.KS', 'exchange': 'KR'},
        {'name': 'LS', 'ticker': '006260.KS', 'exchange': 'KR'},
    ],
    
    # 전력/쿨링 - 발전기
    '발전기': [
        {'name': 'Cummins', 'ticker': 'CMI', 'exchange': 'US'},
        {'name': 'Generac', 'ticker': 'GNRC', 'exchange': 'US'},
        {'name': 'Caterpillar', 'ticker': 'CAT', 'exchange': 'US'},
    ],
    
    # 전력/쿨링 - HVAC
    'HVAC': [
        {'name': 'Johnson Controls', 'ticker': 'JCI', 'exchange': 'US'},
        {'name': 'Trane Tech', 'ticker': 'TT', 'exchange': 'US'},
        {'name': 'Carrier Global', 'ticker': 'CARR', 'exchange': 'US'},
    ],
    
    # 네트워크 - 스위치
    '스위치': [
        {'name': 'Arista Networks', 'ticker': 'ANET', 'exchange': 'US'},
        {'name': 'Cisco', 'ticker': 'CSCO', 'exchange': 'US'},
        {'name': 'Juniper', 'ticker': 'JNPR', 'exchange': 'US'},
    ],
    
    # 네트워크 - 네트워크칩
    '네트워크칩': [
        {'name': 'Broadcom', 'ticker': 'AVGO', 'exchange': 'US'},
        {'name': 'Marvell', 'ticker': 'MRVL', 'exchange': 'US'},
        {'name': 'Microchip', 'ticker': 'MCHP', 'exchange': 'US'},
    ],
    
    # 네트워크 - 광트랜시버
    '광트랜시버': [
        {'name': 'HFR', 'ticker': '230240.KQ', 'exchange': 'KR'},
        {'name': '옵트론텍', 'ticker': '082210.KQ', 'exchange': 'KR'},
    ],
    
    # 네트워크 - 광섬유케이블
    '광섬유케이블': [
        {'name': 'Corning', 'ticker': 'GLW', 'exchange': 'US'},
        {'name': 'Prysmian', 'ticker': 'PRY.MI', 'exchange': 'EU'},
    ],
    
    # 네트워크 - 광학부품
    '광학부품': [
        {'name': 'Lumentum', 'ticker': 'LITE', 'exchange': 'US'},
        {'name': 'II-VI', 'ticker': 'COHR', 'exchange': 'US'},
    ],
    
    # 메모리/스토리지 - HBM메모리
    'HBM메모리': [
        {'name': 'SK hynix', 'ticker': '000660.KS', 'exchange': 'KR'},
        {'name': 'Samsung', 'ticker': '005930.KS', 'exchange': 'KR'},
        {'name': 'Micron', 'ticker': 'MU', 'exchange': 'US'},
    ],
    
    # 메모리/스토리지 - 반도체패키징
    '반도체패키징': [
        {'name': '한미반도체', 'ticker': '042700.KQ', 'exchange': 'KR'},
        {'name': 'Amkor', 'ticker': 'AMKR', 'exchange': 'US'},
        {'name': 'ASE Technology', 'ticker': '3711.TW', 'exchange': 'TW'},
    ],
    
    # 메모리/스토리지 - 스토리지
    '스토리지': [
        {'name': 'Western Digital', 'ticker': 'WDC', 'exchange': 'US'},
        {'name': 'Seagate', 'ticker': 'STX', 'exchange': 'US'},
        {'name': 'NetApp', 'ticker': 'NTAP', 'exchange': 'US'},
    ],
    
    # DC 부동산 - 데이터센터REIT
    '데이터센터REIT': [
        {'name': 'Digital Realty', 'ticker': 'DLR', 'exchange': 'US'},
        {'name': 'Equinix', 'ticker': 'EQIX', 'exchange': 'US'},
        {'name': 'CyrusOne', 'ticker': 'CONE', 'exchange': 'US'},
    ],
}

# 세부영역과 대분류/중분류 매핑
SECTOR_MAPPING = {
    'GPU': {'category': 'AI 인프라', 'sector': 'AI칩'},
    'CPU': {'category': 'AI 인프라', 'sector': 'AI칩'},
    '서버제조': {'category': 'AI 인프라', 'sector': 'AI서버'},
    '전력관리': {'category': '전력/쿨링', 'sector': '전력'},
    '전력기기': {'category': '전력/쿨링', 'sector': '전력'},
    '발전기': {'category': '전력/쿨링', 'sector': '발전'},
    'HVAC': {'category': '전력/쿨링', 'sector': '쿨링'},
    '스위치': {'category': '네트워크', 'sector': '네트워크'},
    '네트워크칩': {'category': '네트워크', 'sector': '네트워크'},
    '광트랜시버': {'category': '네트워크', 'sector': '광통신'},
    '광섬유케이블': {'category': '네트워크', 'sector': '광섬유'},
    '광학부품': {'category': '네트워크', 'sector': '광통신'},
    'HBM메모리': {'category': '메모리/스토리지', 'sector': 'HBM'},
    '반도체패키징': {'category': '메모리/스토리지', 'sector': '패키징'},
    '스토리지': {'category': '메모리/스토리지', 'sector': 'SSD'},
    '데이터센터REIT': {'category': 'DC 부동산', 'sector': 'DC REIT'},
}

def calculate_selection_score(ticker, name, exchange):
    """
    종목 선정 점수 계산 (100점 만점)
    - 시가총액: 30점
    - 거래량: 20점
    - 3개월 수익률: 20점
    - 6개월 수익률: 15점
    - 기술적 지표: 15점
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 기본 정보
        info = stock.info
        market_cap = info.get('marketCap', 0)
        
        # 가격 데이터
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 126:
            print(f"  ⚠️ {name}: 데이터 부족")
            return None
        
        current = hist['Close'].iloc[-1]
        
        # 수익률
        return_3m = ((current / hist['Close'].iloc[-63]) - 1) * 100 if len(hist) >= 63 else 0
        return_6m = ((current / hist['Close'].iloc[-126]) - 1) * 100 if len(hist) >= 126 else 0
        
        # 거래량
        avg_volume_20 = hist['Volume'].rolling(20).mean().iloc[-1]
        avg_volume_60 = hist['Volume'].rolling(60).mean().iloc[-1]
        volume_trend = (avg_volume_20 / avg_volume_60) if avg_volume_60 > 0 else 1
        
        # 이동평균
        ma_20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma_60 = hist['Close'].rolling(60).mean().iloc[-1]
        golden_cross = ma_20 > ma_60
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = rsi.iloc[-1]
        
        # 점수 계산
        score = 0
        
        # 1. 시가총액 점수 (30점)
        if market_cap >= 100_000_000_000:  # 1000억 달러 이상
            score += 30
        elif market_cap >= 50_000_000_000:  # 500억 달러 이상
            score += 25
        elif market_cap >= 10_000_000_000:  # 100억 달러 이상
            score += 20
        elif market_cap >= 5_000_000_000:   # 50억 달러 이상
            score += 15
        elif market_cap >= 1_000_000_000:   # 10억 달러 이상
            score += 10
        else:
            score += 5
        
        # 2. 거래량 점수 (20점)
        if volume_trend >= 1.5:  # 최근 거래량 급증
            score += 20
        elif volume_trend >= 1.2:
            score += 15
        elif volume_trend >= 1.0:
            score += 10
        else:
            score += 5
        
        # 3. 3개월 수익률 점수 (20점)
        if return_3m >= 30:
            score += 20
        elif return_3m >= 20:
            score += 17
        elif return_3m >= 10:
            score += 14
        elif return_3m >= 0:
            score += 10
        elif return_3m >= -10:
            score += 5
        # 마이너스 크면 0점
        
        # 4. 6개월 수익률 점수 (15점)
        if return_6m >= 40:
            score += 15
        elif return_6m >= 25:
            score += 12
        elif return_6m >= 10:
            score += 9
        elif return_6m >= 0:
            score += 6
        elif return_6m >= -15:
            score += 3
        
        # 5. 기술적 지표 점수 (15점)
        tech_score = 0
        if golden_cross:
            tech_score += 6
        if 40 <= rsi_value <= 60:  # 중립구간 (좋음)
            tech_score += 6
        elif 30 <= rsi_value <= 70:
            tech_score += 3
        
        price_vs_ma20 = (current / ma_20 - 1) * 100
        if price_vs_ma20 > 0:  # 20일선 위
            tech_score += 3
        
        score += tech_score
        
        return {
            'name': name,
            'ticker': ticker,
            'exchange': exchange,
            'market_cap': market_cap,
            'return_3m': return_3m,
            'return_6m': return_6m,
            'volume_trend': volume_trend,
            'golden_cross': golden_cross,
            'rsi': rsi_value,
            'score': score
        }
        
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:100]}")
        return None

def select_best_stocks_per_sector():
    """각 세부영역별로 최고 점수 종목 선정"""
    
    selected_stocks = []
    
    for sub_sector, candidates in CANDIDATE_POOLS.items():
        print(f"\n{'='*60}")
        print(f"📂 세부영역: {sub_sector}")
        print(f"   후보: {len(candidates)}개")
        print(f"{'='*60}")
        
        sector_results = []
        
        for candidate in candidates:
            print(f"  분석 중: {candidate['name']:20s} ... ", end='')
            result = calculate_selection_score(
                candidate['ticker'],
                candidate['name'],
                candidate['exchange']
            )
            
            if result:
                sector_results.append(result)
                print(f"✅ {result['score']:.1f}점")
            else:
                print("❌")
        
        # 점수 순으로 정렬
        sector_results.sort(key=lambda x: x['score'], reverse=True)
        
        if sector_results:
            # 1위 종목 선정
            best = sector_results[0]
            
            # 대분류, 중분류 정보 추가
            mapping = SECTOR_MAPPING[sub_sector]
            best['category'] = mapping['category']
            best['sector'] = mapping['sector']
            best['sub_sector'] = sub_sector
            
            selected_stocks.append(best)
            
            print(f"\n  ⭐ 선정: {best['name']} ({best['score']:.1f}점)")
            print(f"     시가총액: ${best['market_cap']/1e9:.1f}B")
            print(f"     3개월 수익률: {best['return_3m']:+.2f}%")
            print(f"     골든크로스: {'✅' if best['golden_cross'] else '❌'}")
            
            # 2위 종목도 표시 (참고용)
            if len(sector_results) > 1:
                second = sector_results[1]
                print(f"  2위: {second['name']} ({second['score']:.1f}점)")
        else:
            print(f"  ⚠️ 해당 세부영역에서 선정 가능한 종목 없음")
    
    return selected_stocks

# 종목 선정 실행
print("\n🚀 종목 선정 프로세스 시작...\n")

selected = select_best_stocks_per_sector()

print(f"\n{'='*80}")
print(f"✅ 총 {len(selected)}개 종목 선정 완료!")
print(f"{'='*80}\n")

# DataFrame으로 변환
df_selected = pd.DataFrame(selected)

# 결과를 Excel로 저장
now = datetime.now()
date_str = now.strftime('%Y%m%d')
# GitHub Actions 및 로컬 실행 모두 호환되는 경로
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
excel_file = f'{output_dir}/selected_stocks_{date_str}.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # 1. 선정 결과
    df_export = df_selected[[
        'name', 'ticker', 'category', 'sector', 'sub_sector',
        'score', 'market_cap', 'return_3m', 'return_6m',
        'golden_cross', 'rsi'
    ]].copy()
    
    df_export['market_cap'] = df_export['market_cap'] / 1e9  # 10억 달러 단위
    df_export.columns = [
        '종목명', '티커', '대분류', '중분류', '세부분류',
        '종합점수', '시가총액(B$)', '3개월수익률(%)', '6개월수익률(%)',
        '골든크로스', 'RSI'
    ]
    
    df_export = df_export.round(2)
    df_export.to_excel(writer, sheet_name='선정결과', index=False)
    
    # 2. 대분류별 통계
    category_stats = df_selected.groupby('category').agg({
        'score': 'mean',
        'return_3m': 'mean',
        'name': 'count'
    }).round(2)
    category_stats.columns = ['평균점수', '평균3개월수익률', '종목수']
    category_stats.to_excel(writer, sheet_name='대분류별통계')
    
    # 3. 점수 상위 종목
    top_scores = df_selected.nlargest(10, 'score')[[
        'name', 'category', 'sub_sector', 'score', 'return_3m'
    ]].copy()
    top_scores.columns = ['종목명', '대분류', '세부분류', '점수', '3개월수익률']
    top_scores.to_excel(writer, sheet_name='점수TOP10', index=False)
    
    # 4. 선정 기준 설명
    criteria_df = pd.DataFrame({
        '평가항목': ['시가총액', '거래량', '3개월수익률', '6개월수익률', '기술적지표'],
        '배점': [30, 20, 20, 15, 15],
        '평가기준': [
            '1000억$↑: 30점, 500억$↑: 25점, 100억$↑: 20점...',
            '거래량 급증 여부 (최근20일 vs 60일)',
            '30%↑: 20점, 20%↑: 17점, 10%↑: 14점...',
            '40%↑: 15점, 25%↑: 12점, 10%↑: 9점...',
            '골든크로스, RSI 중립구간, 20일선 상향'
        ]
    })
    criteria_df.to_excel(writer, sheet_name='선정기준', index=False)

print(f"📊 결과 파일 저장: {excel_file}")

# Python 코드 생성 (main 스크립트에 복붙용)
print("\n" + "="*80)
print("📝 아래 코드를 main 스크립트의 STOCKS 변수에 복사하세요:")
print("="*80 + "\n")

print("STOCKS = [")
for _, row in df_selected.iterrows():
    print(f"    {{'name': '{row['name']}', 'ticker': '{row['ticker']}', "
          f"'category': '{row['category']}', 'sector': '{row['sector']}', "
          f"'sub_sector': '{row['sub_sector']}'}},")
print("]")

print("\n" + "="*80)
print("✅ 종목 선정 완료!")
print("💡 Tip: 매월 1일에 이 스크립트를 실행하여 종목을 업데이트하세요.")
print("="*80)
