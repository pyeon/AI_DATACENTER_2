"""
Datacenter News Monitor v10.1
✅ FIXED: Yahoo + Google + Naver 합집합 수집
"""

import yfinance as yf
import requests
import os
import json
from datetime import datetime, timedelta
from googletrans import Translator
import time
import warnings
from collections import defaultdict
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import feedparser
from urllib.parse import quote
import re

warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID', '')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET', '')

STOCKS = [
    {'name': 'NVIDIA', 'ticker': 'NVDA', 'priority': 1, 'country': 'US', 
     'search_terms': ['NVIDIA AI', 'NVIDIA datacenter']},
    {'name': 'AMD', 'ticker': 'AMD', 'priority': 1, 'country': 'US', 
     'search_terms': ['AMD AI chip', 'AMD datacenter']},
    {'name': 'Intel', 'ticker': 'INTC', 'priority': 2, 'country': 'US', 
     'search_terms': ['Intel datacenter', 'Intel AI']},
    {'name': 'Super Micro', 'ticker': 'SMCI', 'priority': 1, 'country': 'US', 
     'search_terms': ['Super Micro AI server']},
    {'name': 'Broadcom', 'ticker': 'AVGO', 'priority': 1, 'country': 'US', 
     'search_terms': ['Broadcom AI chip']},
    {'name': 'Micron', 'ticker': 'MU', 'priority': 1, 'country': 'US', 
     'search_terms': ['Micron HBM', 'Micron memory']},
    {'name': 'SK Hynix', 'ticker': '000660.KS', 'priority': 1, 'country': 'KR', 
     'search_terms': ['SK하이닉스 HBM', 'SK하이닉스 AI']},
    {'name': 'Samsung', 'ticker': '005930.KS', 'priority': 1, 'country': 'KR', 
     'search_terms': ['삼성전자 반도체', '삼성전자 HBM']},
    {'name': 'LS ELECTRIC', 'ticker': '010120.KS', 'priority': 1, 'country': 'KR', 
     'search_terms': ['LS ELECTRIC 데이터센터']},
    {'name': 'Hanmi', 'ticker': '042700.KQ', 'priority': 2, 'country': 'KR', 
     'search_terms': ['한미반도체 AI']},
]

ENGLISH_KEYWORDS = {
    'high': ['AI', 'GPU', 'HBM', 'datacenter', 'data center', 'earnings', 'chip'],
    'medium': ['partnership', 'contract', 'launch', 'investment'],
}

KOREAN_KEYWORDS = {
    'high': ['AI', 'HBM', 'GPU', '데이터센터', '반도체', '실적', '수주'],
    'medium': ['파트너십', '계약', '투자', '출시'],
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_seen_links():
    """Load previously seen news links from history file"""
    try:
        with open('news_history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('seen_links', []))
    except:
        return set()


def save_seen_links(links):
    """Save seen news links to history file"""
    try:
        data = {
            'last_updated': datetime.now().isoformat(),
            'seen_links': list(links)
        }
        with open('news_history.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass


def calculate_score(title, keywords_dict):
    """
    Calculate relevance score based on keywords
    Returns: (score, matched_keywords)
    """
    text = title.lower()
    score = 0
    matched_keywords = []
    
    for keyword in keywords_dict.get('high', []):
        if keyword.lower() in text:
            score += 10
            matched_keywords.append(keyword)
            break
    
    if score == 0:
        for keyword in keywords_dict.get('medium', []):
            if keyword.lower() in text:
                score += 6
                matched_keywords.append(keyword)
                break
    
    return max(score, 1), matched_keywords


def translate_text(text, max_length=500):
    """Translate English text to Korean"""
    if not text:
        return text
    
    korean_chars = sum(1 for c in text if '가' <= c <= '힣')
    if len(text) > 0 and korean_chars / len(text) > 0.5:
        return text
    
    try:
        translator = Translator()
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        result = translator.translate(text, src='en', dest='ko')
        return result.text if result and result.text else text
    except:
        return text


# ============================================================================
# NEWS COLLECTION FUNCTIONS
# ============================================================================

def get_yahoo_news_method1(ticker, seen_links):
    """
    Method 1: Collect news using yfinance library
    """
    news_list = []
    print(f"      [Method 1] yfinance...")
    
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            print(f"        Result: 0 items")
            return []
        
        print(f"        Result: {len(news)} items")
        week_ago = datetime.now() - timedelta(days=7)
        
        for item in news[:10]:
            try:
                title = item.get('title', '').strip()
                link = item.get('link', '').strip()
                publisher = item.get('publisher', 'Yahoo').strip()
                published = item.get('providerPublishTime')
                
                if not title or not link or len(title) < 10:
                    continue
                if link in seen_links:
                    continue
                
                pub_date = datetime.fromtimestamp(published) if published else datetime.now()
                if pub_date < week_ago:
                    continue
                
                summary = item.get('summary', '')[:300] or item.get('description', '')[:300] or ''
                
                news_list.append({
                    'title': title,
                    'description': summary,
                    'link': link,
                    'publisher': publisher,
                    'date': pub_date,
                    'source': 'Yahoo Finance'
                })
                seen_links.add(link)
                
            except:
                continue
        
        print(f"        Valid: {len(news_list)} items")
        
    except Exception as e:
        print(f"        ERROR: {str(e)}")
    
    return news_list


def get_google_news_rss(search_term, seen_links):
    """
    Method 2: Collect news using Google News RSS
    """
    news_list = []
    print(f"      [Method 2] Google News RSS...")
    
    try:
        encoded_term = quote(search_term)
        rss_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print(f"        Result: 0 items")
            return []
        
        print(f"        Result: {len(feed.entries)} items")
        week_ago = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:10]:
            try:
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                summary = entry.get('summary', '').strip()
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = re.sub(r'http[s]?://\S+', '', summary)
                summary = summary.strip()[:300]
                
                if len(summary) < 20:
                    summary = ''
                
                published = entry.get('published_parsed')
                
                if not title or not link or len(title) < 10:
                    continue
                if link in seen_links:
                    continue
                
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < week_ago:
                        continue
                else:
                    pub_date = datetime.now()
                
                publisher = entry.get('source', {}).get('title', 'Google News')
                
                news_list.append({
                    'title': title,
                    'description': summary,
                    'link': link,
                    'publisher': publisher,
                    'date': pub_date,
                    'source': 'Google News'
                })
                seen_links.add(link)
                
            except:
                continue
        
        print(f"        Valid: {len(news_list)} items")
        
    except Exception as e:
        print(f"        ERROR: {str(e)}")
    
    return news_list


def get_us_news(ticker, company_name, search_terms, seen_links):
    """
    ✅ FIXED: Get US company news using BOTH Yahoo and Google (union)
    Previously: Yahoo OR Google (only one)
    Now: Yahoo + Google (both sources)
    """
    all_news = []
    
    print(f"    Collecting from multiple sources...")
    
    # 1. Always collect from Yahoo Finance
    yahoo_news = get_yahoo_news_method1(ticker, seen_links)
    all_news.extend(yahoo_news)
    
    # 2. ✅ FIXED: Always collect from Google News (not just as fallback!)
    print(f"      Collecting Google News...")
    for term in search_terms[:2]:
        google_news = get_google_news_rss(term, seen_links)
        all_news.extend(google_news)
        time.sleep(1)
    
    print(f"    Total collected: {len(all_news)} articles (Yahoo: {len(yahoo_news)}, Google: {len(all_news) - len(yahoo_news)})")
    return all_news


def get_naver_news(search_term, seen_links):
    """
    Get Korean news from Naver API
    """
    news_list = []
    
    try:
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            return []
        
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {
            "query": search_term,
            "display": 20,
            "sort": "date"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            items = response.json().get('items', [])
            week_ago = datetime.now() - timedelta(days=7)
            
            for item in items:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '').strip()
                description = item.get('description', '').replace('<b>', '').replace('</b>', '').strip()
                link = item.get('originallink', item.get('link', '')).strip()
                
                if not title or not link or len(title) < 10:
                    continue
                if link in seen_links:
                    continue
                
                try:
                    pub_date_str = item.get('pubDate', '')
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
                    pub_date = pub_date.replace(tzinfo=None)
                    if pub_date < week_ago:
                        continue
                except:
                    pub_date = datetime.now()
                
                publisher = 'Naver'
                if item.get('originallink'):
                    try:
                        publisher = item['originallink'].split('/')[2]
                    except:
                        pass
                
                news_list.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'publisher': publisher,
                    'date': pub_date,
                    'source': 'Naver API'
                })
                seen_links.add(link)
                
    except Exception as e:
        print(f"      Naver ERROR: {str(e)}")
    
    return news_list


# ============================================================================
# OUTPUT GENERATION FUNCTIONS
# ============================================================================

def create_docx_report(news_by_company, filename='outputs/news_report.docx'):
    """Create Word document report"""
    os.makedirs('outputs', exist_ok=True)
    
    doc = Document()
    
    title = doc.add_heading('Datacenter News Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    date_para = doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    for company, news_list in news_by_company.items():
        flag = "KR" if news_list[0]['country'] == 'KR' else "US"
        doc.add_heading(f'[{flag}] {company}', level=1)
        
        for news in news_list:
            emoji = "HIGH" if news['score'] >= 10 else "MED" if news['score'] >= 6 else "LOW"
            
            para = doc.add_paragraph()
            para.add_run(f'[{emoji}] ').bold = True
            para.add_run(news.get('translated_title', news['title'])).bold = True
            
            if news.get('translated_description'):
                doc.add_paragraph(f"Summary: {news['translated_description']}")
            
            hours = int((datetime.now() - news['date']).total_seconds() / 3600)
            time_str = "Now" if hours < 1 else f"{hours}h ago" if hours < 24 else f"{hours//24}d ago"
            
            doc.add_paragraph(f'Time: {time_str} | Source: {news["publisher"]} ({news["source"]})')
            
            link_para = doc.add_paragraph()
            link_para.add_run('Link: ').bold = True
            link_para.add_run(news['link'])
            
            doc.add_paragraph()
    
    doc.save(filename)
    return filename


def send_telegram_message(text):
    """Send text message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    return response.status_code == 200


def send_telegram_document(file_path, caption=''):
    """Send document file to Telegram"""
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        response = requests.post(url, files=files, data=data)
        return response.status_code == 200


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("="*70)
    print("Datacenter News Monitor v10.1 - MULTI-SOURCE (FIXED)")
    print("  ✅ US: Yahoo Finance + Google News (UNION)")
    print("  ✅ KR: Naver API")
    print("  Full validation & logging")
    print("="*70)
    
    seen_links = load_seen_links()
    print(f"\nSeen links: {len(seen_links)}")
    
    print("\n" + "="*70)
    print("PHASE 1: NEWS COLLECTION")
    print("="*70)
    
    all_news_by_company = defaultdict(list)
    stats = {'US_yahoo': 0, 'US_google': 0, 'KR_naver': 0}
    
    for idx, stock in enumerate(STOCKS, 1):
        print(f"\n[{idx}/{len(STOCKS)}] {stock['name']} ({stock['country']})")
        
        if stock['country'] == 'US':
            news = get_us_news(
                stock['ticker'], 
                stock['name'], 
                stock.get('search_terms', []), 
                seen_links
            )
            for item in news:
                if item['source'] == 'Yahoo Finance':
                    stats['US_yahoo'] += 1
                else:
                    stats['US_google'] += 1
        else:
            news = []
            for term in stock.get('search_terms', [stock['name']]):
                print(f"    Search: {term}")
                naver_news = get_naver_news(term, seen_links)
                news.extend(naver_news)
                stats['KR_naver'] += len(naver_news)
                print(f"    Found: {len(naver_news)} articles")
                time.sleep(0.3)
        
        keywords = KOREAN_KEYWORDS if stock['country'] == 'KR' else ENGLISH_KEYWORDS
        
        for news_item in news:
            score, matched = calculate_score(news_item['title'], keywords)
            news_item['score'] = score
            news_item['matched_keywords'] = matched
            news_item['company'] = stock['name']
            news_item['country'] = stock['country']
            all_news_by_company[stock['name']].append(news_item)
    
    save_seen_links(seen_links)
    
    print("\n" + "="*70)
    print("COLLECTION STATS")
    print("="*70)
    print(f"US Yahoo: {stats['US_yahoo']}")
    print(f"US Google: {stats['US_google']}")
    print(f"KR Naver: {stats['KR_naver']}")
    print(f"TOTAL: {sum(stats.values())}")
    
    filtered = {}
    for company, news_list in all_news_by_company.items():
        news_list.sort(key=lambda x: (x['score'], x['date']), reverse=True)
        filtered[company] = news_list[:2]
    
    final_count = sum(len(n) for n in filtered.values())
    print(f"Final (top 2 each): {final_count}")
    
    if final_count == 0:
        msg = f"📰 데이터센터 뉴스\n\n뉴스 없음\n\n통계:\nYahoo: {stats['US_yahoo']}\nGoogle: {stats['US_google']}\nNaver: {stats['KR_naver']}"
        send_telegram_message(msg)
        return
    
    print("\n" + "="*70)
    print("PHASE 2: TRANSLATION")
    print("="*70)
    
    for company, news_list in filtered.items():
        for news in news_list:
            news['translated_title'] = translate_text(news['title'], 300)
            if news.get('description'):
                news['translated_description'] = translate_text(news['description'], 200)
            time.sleep(0.5)
    
    print("\n" + "="*70)
    print("PHASE 3: MESSAGE GENERATION")
    print("="*70)
    
    messages = []
    msg = f"📰 데이터센터 뉴스\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*30}\n\n"
    msg += f"📊 기사: {final_count}개\n"
    msg += f"Yahoo: {stats['US_yahoo']} | Google: {stats['US_google']} | Naver: {stats['KR_naver']}\n\n"
    
    for company, news_list in sorted(filtered.items(), 
                                    key=lambda x: max(n['score'] for n in x[1]), 
                                    reverse=True):
        flag = "🇰🇷" if news_list[0]['country'] == 'KR' else "🇺🇸"
        section = f"{flag} {company}\n{'-'*30}\n\n"
        
        for news in news_list:
            emoji = "🔥" if news['score'] >= 10 else "📈"
            hours = int((datetime.now() - news['date']).total_seconds() / 3600)
            time_str = "방금" if hours < 1 else f"{hours}시간 전" if hours < 24 else f"{hours//24}일 전"
            
            section += f"{emoji} {news['translated_title']}\n\n"
            if news.get('translated_description'):
                section += f"{news['translated_description']}\n\n"
            section += f"⏰ {time_str} | 📰 {news['publisher']}\n"
            section += f"🔗 {news['link']}\n\n"
        
        section += "="*30 + "\n\n"
        
        if len(msg + section) > 3500:
            messages.append(msg)
            msg = section
        else:
            msg += section
    
    if msg:
        messages.append(msg)
    
    docx = create_docx_report(filtered, f"outputs/news_{datetime.now().strftime('%Y%m%d')}.docx")
    
    print("\n" + "="*70)
    print(f"PHASE 4: TELEGRAM DELIVERY ({len(messages)} messages)")
    print("="*70)
    
    for idx, m in enumerate(messages, 1):
        send_telegram_message(m)
        print(f"  Message {idx}: Sent")
        time.sleep(1)
    
    send_telegram_document(docx, '📰 데이터센터 뉴스 리포트')
    print("  DOCX: Sent")
    
    print("\n" + "="*70)
    print("✅ COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
