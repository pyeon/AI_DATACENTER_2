"""
Datacenter News Monitor v10.3 - HOTFIX
🚨 번역 제거 + Yahoo 우회 + 안정성 우선
"""

import yfinance as yf
import requests
import os
import json
from datetime import datetime, timedelta
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
    """Load previously seen news links"""
    try:
        with open('news_history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('seen_links', []))
    except:
        return set()


def save_seen_links(links):
    """Save seen news links"""
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
    """Calculate relevance score"""
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


# ============================================================================
# NEWS COLLECTION - GOOGLE NEWS ONLY (STABLE)
# ============================================================================

def get_google_news_rss(search_term, seen_links):
    """Collect news using Google News RSS"""
    news_list = []
    
    try:
        encoded_term = quote(search_term)
        rss_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            return []
        
        week_ago = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:20]:  # 더 많이 수집
            try:
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                
                if not title or not link or len(title) < 10:
                    continue
                    
                if link in seen_links:
                    continue
                
                published = entry.get('published_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < week_ago:
                        continue
                else:
                    pub_date = datetime.now()
                
                summary = entry.get('summary', '').strip()
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = re.sub(r'http[s]?://\S+', '', summary)
                summary = summary.strip()[:300]
                
                if len(summary) < 20:
                    summary = ''
                
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
        
    except Exception as e:
        print(f"      [ERROR] Google News: {str(e)}")
    
    return news_list


def get_us_news(search_terms, seen_links):
    """Get US company news - Google News only"""
    all_news = []
    
    for term in search_terms[:2]:
        news = get_google_news_rss(term, seen_links)
        all_news.extend(news)
        print(f"      [{term}] {len(news)} articles")
        time.sleep(1)
    
    return all_news


def get_naver_news(search_term, seen_links):
    """Get Korean news from Naver API"""
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
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        items = response.json().get('items', [])
        week_ago = datetime.now() - timedelta(days=7)
        
        for item in items:
            try:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '').strip()
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
                
                description = item.get('description', '').replace('<b>', '').replace('</b>', '').strip()
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
                
            except:
                continue
        
    except Exception as e:
        print(f"      [ERROR] Naver: {str(e)}")
    
    return news_list


# ============================================================================
# OUTPUT GENERATION
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
            para.add_run(news['title']).bold = True
            
            if news.get('description'):
                doc.add_paragraph(f"Summary: {news['description']}")
            
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
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        return response.status_code == 200
    except:
        return False


def send_telegram_document(file_path, caption=''):
    """Send document file to Telegram"""
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            response = requests.post(url, files=files, data=data, timeout=30)
            return response.status_code == 200
    except:
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    
    print("="*70)
    print("Datacenter News Monitor v10.3 - HOTFIX")
    print("  🚨 Stable version: No translation, Google + Naver only")
    print("="*70)
    
    print("\n[CONFIG]")
    print(f"  Telegram: {'✓' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '✗'}")
    print(f"  Naver API: {'✓' if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET else '✗'}")
    
    seen_links = load_seen_links()
    print(f"  Seen links: {len(seen_links)}")
    
    print("\n" + "="*70)
    print("COLLECTING NEWS")
    print("="*70)
    
    all_news_by_company = defaultdict(list)
    stats = {'google': 0, 'naver': 0}
    
    for idx, stock in enumerate(STOCKS, 1):
        print(f"\n[{idx}/{len(STOCKS)}] {stock['name']} ({stock['country']})")
        
        if stock['country'] == 'US':
            news = get_us_news(stock.get('search_terms', []), seen_links)
            stats['google'] += len(news)
        else:
            news = []
            for term in stock.get('search_terms', [stock['name']]):
                naver_news = get_naver_news(term, seen_links)
                news.extend(naver_news)
                stats['naver'] += len(naver_news)
                print(f"      [{term}] {len(naver_news)} articles")
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
    print("STATS")
    print("="*70)
    print(f"Google: {stats['google']}")
    print(f"Naver: {stats['naver']}")
    print(f"TOTAL: {sum(stats.values())}")
    
    # 상위 2개씩 선택
    filtered = {}
    for company, news_list in all_news_by_company.items():
        news_list.sort(key=lambda x: (x['score'], x['date']), reverse=True)
        filtered[company] = news_list[:2]
    
    final_count = sum(len(n) for n in filtered.values())
    print(f"Final (top 2 each): {final_count}")
    
    if final_count == 0:
        msg = f"📰 Datacenter News\n\nNo news\n\nGoogle: {stats['google']}\nNaver: {stats['naver']}"
        send_telegram_message(msg)
        return
    
    print("\n" + "="*70)
    print("GENERATING MESSAGES")
    print("="*70)
    
    messages = []
    msg = f"📰 Datacenter News\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*30}\n\n"
    msg += f"📊 Articles: {final_count}\n"
    msg += f"Google: {stats['google']} | Naver: {stats['naver']}\n\n"
    
    for company, news_list in sorted(filtered.items(), 
                                    key=lambda x: max(n['score'] for n in x[1]), 
                                    reverse=True):
        flag = "🇰🇷" if news_list[0]['country'] == 'KR' else "🇺🇸"
        section = f"{flag} {company}\n{'-'*30}\n\n"
        
        for news in news_list:
            emoji = "🔥" if news['score'] >= 10 else "📈"
            hours = int((datetime.now() - news['date']).total_seconds() / 3600)
            time_str = "Now" if hours < 1 else f"{hours}h ago" if hours < 24 else f"{hours//24}d ago"
            
            section += f"{emoji} {news['title']}\n\n"
            
            if news.get('description'):
                section += f"{news['description']}\n\n"
            
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
    
    print(f"Generated {len(messages)} messages")
    
    docx = create_docx_report(filtered, f"outputs/news_{datetime.now().strftime('%Y%m%d')}.docx")
    
    print("\n" + "="*70)
    print(f"SENDING TO TELEGRAM")
    print("="*70)
    
    for idx, m in enumerate(messages, 1):
        send_telegram_message(m)
        print(f"  Message {idx}: Sent")
        time.sleep(1)
    
    send_telegram_document(docx, '📰 Datacenter News Report')
    print("  DOCX: Sent")
    
    print("\n" + "="*70)
    print("✅ DONE")
    print("="*70)


if __name__ == "__main__":
    main()
