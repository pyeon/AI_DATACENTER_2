"""
데이터센터 투자 자동화 시스템 v2.0
- RSI 지표 추가
- 골든크로스/강한모멘텀/RSI 전체 표시
"""

import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("📊 데이터센터 투자 자동화 시스템 v2.0")
print("="*70 + "\n")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

STOCKS = [
    {'name': 'NVIDIA', 'ticker': 'NVDA', 'sector': 'AI칩'},
    {'name': 'AMD', 'ticker': 'AMD', 'sector': 'AI칩'},
    {'name': 'Intel', 'ticker': 'INTC', 'sector': 'AI칩'},
    {'name': 'Super Micro', 'ticker': 'SMCI', 'sector': 'AI서버'},
    {'name': 'Dell', 'ticker': 'DELL', 'sector': 'AI서버'},
    {'name': 'Vertiv', 'ticker': 'VRT', 'sector': '전력'},
    {'name': 'Eaton', 'ticker': 'ETN', 'sector': '전력'},
    {'name': 'LS ELECTRIC', 'ticker': '010120.KS', 'sector': '전력'},
    {'name': 'Cummins', 'ticker': 'CMI', 'sector': '발전'},
    {'name': 'Generac', 'ticker': 'GNRC', 'sector': '발전'},
    {'name': 'Johnson Controls', 'ticker': 'JCI', 'sector': '쿨링'},
    {'name': 'Trane Tech', 'ticker': 'TT', 'sector': '쿨링'},
    {'name': 'Arista Networks', 'ticker': 'ANET', 'sector': '네트워크'},
    {'name': 'Broadcom', 'ticker': 'AVGO', 'sector': '네트워크'},
    {'name': 'Marvell', 'ticker': 'MRVL', 'sector': '네트워크'},
    {'name': 'HFR', 'ticker': '230240.KQ', 'sector': '광통신'},
    {'name': 'Corning', 'ticker': 'GLW', 'sector': '광섬유'},
    {'name': 'Lumentum', 'ticker': 'LITE', 'sector': '광통신'},
    {'name': 'SK hynix', 'ticker': '000660.KS', 'sector': 'HBM'},
    {'name': 'Samsung', 'ticker': '005930.KS', 'sector': 'HBM'},
    {'name': 'Micron', 'ticker': 'MU', 'sector': 'HBM'},
    {'name': '한미반도체', 'ticker': '042700.KQ', 'sector': '패키징'},
    {'name': 'Amkor', 'ticker': 'AMKR', 'sector': '패키징'},
    {'name': 'Western Digital', 'ticker': 'WDC', 'sector': 'SSD'},
    {'name': 'Digital Realty', 'ticker': 'DLR', 'sector': 'DC REIT'},
    {'name': 'Equinix', 'ticker': 'EQIX', 'sector': 'DC REIT'},
]

print(f"📋 총 {len(STOCKS)}개 종목 모니터링\n")


def calculate_rsi(prices, period=14):
    """RSI(Relative Strength Index) 계산"""
    try:
        if len(prices) < period:
            return 50
        
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0)
        loss = -deltas.where(deltas < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    except:
        return 50


def get_stock_data(ticker, name, sector):
    """주가 데이터 수집 및 지표 계산"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty or len(hist) < 2:
            return None
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
        
        # 수익률 계산
        change_1d = ((current / prev) - 1) * 100
        change_1w = ((current / hist['Close'].iloc[-5]) - 1) * 100 if len(hist) >= 5 else 0
        change_1m = ((current / hist['Close'].iloc[-21]) - 1) * 100 if len(hist) >= 21 else 0
        
        # 이동평균
        ma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current
        ma_60 = hist['Close'].rolling(60).mean().iloc[-1] if len(hist) >= 60 else current
        
        vs_ma20 = ((current / ma_20) - 1) * 100 if ma_20 else 0
        golden_cross = ma_20 > ma_60 if (ma_20 and ma_60) else False
        
        # 거래량
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else volume
        volume_ratio = (volume / avg_volume * 100) if avg_volume else 100
        
        # RSI 계산
        rsi = calculate_rsi(hist['Close'], period=14)
        
        return {
            'name': name,
            'ticker': ticker,
            'sector': sector,
            'price': current,
            'change_1d': change_1d,
            'change_1w': change_1w,
            'change_1m': change_1m,
            'vs_ma20': vs_ma20,
            'golden_cross': golden_cross,
            'volume_ratio': volume_ratio,
            'rsi': rsi,
        }
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")
        return None


print("📈 주가 데이터 수집 중...\n")

results = []
for idx, stock in enumerate(STOCKS, 1):
    print(f"[{idx}/{len(STOCKS)}] {stock['name']:20s} ... ", end='')
    data = get_stock_data(stock['ticker'], stock['name'], stock['sector'])
    if data:
        results.append(data)
        print("✅")
    else:
        print("❌")

print(f"\n✅ 수집 완료: {len(results)}/{len(STOCKS)}개\n")

df = pd.DataFrame(results)

now = datetime.now().strftime('%Y-%m-%d %H:%M')

message = "📊 데이터센터 종목 일일 리포트\n"
message += f"🕐 {now}\n"
message += "━━━━━━━━━━━━━━━\n\n"

# 상승 TOP 5
top_gainers = df.nlargest(5, 'change_1d')
message += "🔥 오늘 상승 TOP 5\n"
for _, row in top_gainers.iterrows():
    emoji = "🚀" if row['change_1d'] > 5 else "📈"
    message += f"{emoji} {row['name']}: {row['change_1d']:+.2f}%\n"

message += "\n"

# 하락 TOP 5
top_losers = df.nsmallest(5, 'change_1d')
message += "📉 오늘 하락 TOP 5\n"
for _, row in top_losers.iterrows():
    message += f"📉 {row['name']}: {row['change_1d']:+.2f}%\n"

message += "\n"

# 골든크로스 - 전체 표시
golden = df[df['golden_cross'] == True]
if len(golden) > 0:
    message += f"⭐ 골든크로스 ({len(golden)}개)\n"
    for _, row in golden.iterrows():
        message += f"• {row['name']}\n"
    message += "\n"

# 거래량 급증 - 전체 표시
volume_spike = df[df['volume_ratio'] > 200].sort_values('volume_ratio', ascending=False)
if len(volume_spike) > 0:
    message += f"📊 거래량 급증 ({len(volume_spike)}개, 평균 대비 2배↑)\n"
    for _, row in volume_spike.iterrows():
        message += f"• {row['name']}: {row['volume_ratio']:.0f}%\n"
    message += "\n"

# RSI 과매수 - 전체 표시
rsi_overbought = df[df['rsi'] > 70].sort_values('rsi', ascending=False)
if len(rsi_overbought) > 0:
    message += f"🔴 RSI 과매수 ({len(rsi_overbought)}개, >70)\n"
    for _, row in rsi_overbought.iterrows():
        message += f"• {row['name']}: RSI {row['rsi']:.1f}\n"
    message += "\n"

# RSI 과매도 - 전체 표시
rsi_oversold = df[df['rsi'] < 30].sort_values('rsi')
if len(rsi_oversold) > 0:
    message += f"🟢 RSI 과매도 ({len(rsi_oversold)}개, <30)\n"
    for _, row in rsi_oversold.iterrows():
        message += f"• {row['name']}: RSI {row['rsi']:.1f}\n"
    message += "\n"

up_count = len(df[df['change_1d'] > 0])
down_count = len(df[df['change_1d'] < 0])

message += "━━━━━━━━━━━━━━━\n"
message += f"📈 상승: {up_count}개\n"
message += f"📉 하락: {down_count}개\n"
message += f"📊 총 {len(results)}개 종목"

print("📱 텔레그램 전송 중...\n")

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

try:
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ 텔레그램 전송 성공!")
    else:
        print(f"❌ 전송 실패: {response.status_code}")
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "="*70)
print("✅ 작업 완료!")
print("="*70)
