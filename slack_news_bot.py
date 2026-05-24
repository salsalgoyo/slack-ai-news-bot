import os
import requests
from bs4 import BeautifulSoup
import json
import feedparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

KST = timezone(timedelta(hours=9))

def get_naver_news(limit=3):
    url = "https://news.naver.com/section/105"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    news_list = []
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        items = soup.select(".sa_item_inner")
        
        for item in items:
            if len(news_list) >= limit:
                break
                
            title_tag = item.select_one(".sa_text_title")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href")
            
            # AI 뉴스 필터링
            if 'AI' not in title.upper() and '인공지능' not in title:
                continue
                
            try:
                article_res = requests.get(link, headers=headers)
                article_soup = BeautifulSoup(article_res.text, "html.parser")
                date_tag = article_soup.select_one(".media_end_head_info_datestamp_time")
                
                if date_tag and date_tag.has_attr("data-date-time"):
                    date_str = date_tag["data-date-time"] # "2026-05-24 14:52:27"
                    pub_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
                    
                    # 최신순 정렬이므로 그대로 추가 (단, 2일 이상 지난 너무 오래된 기사 제외)
                    now = datetime.now(KST)
                    if (now - pub_time).days <= 2:
                        news_list.append({"title": title, "link": link, "source": "네이버 IT/과학"})
            except Exception as e:
                print(f"네이버 개별 기사 크롤링 오류: {e}")
                
    except Exception as e:
        print(f"네이버 뉴스 크롤링 오류: {e}")
        
    return news_list

def get_google_news(limit=5):
    url = "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko"
    news_list = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if len(news_list) >= limit:
                break
                
            try:
                pub_dt = parsedate_to_datetime(entry.published)
                pub_dt_kst = pub_dt.astimezone(KST)
                now = datetime.now(KST)
                if (now - pub_dt_kst).days <= 2:
                    news_list.append({"title": entry.title, "link": entry.link, "source": "구글 뉴스"})
            except Exception as e:
                print(f"구글 뉴스 시간 파싱 오류: {e}")
                continue
    except Exception as e:
        print(f"구글 뉴스 크롤링 오류: {e}")
    return news_list

def parse_zdnet_time(date_str):
    try:
        clean = date_str.strip()
        dt = datetime.strptime(clean, "%Y.%m.%d %H:%M")
        return dt.replace(tzinfo=KST)
    except:
        return None

def get_zdnet_news(limit=3):
    url = "https://search.zdnet.co.kr/?kwd=AI"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    news_list = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        news_posts = soup.find_all("div", class_="newsPost")
        
        for post in news_posts:
            if len(news_list) >= limit:
                break
                
            asset_text = post.find("div", class_="assetText")
            if not asset_text:
                continue
            
            link_tag = asset_text.find("a")
            if not link_tag:
                continue
                
            href = link_tag.get("href")
            if href and not href.startswith("http"):
                href = "https://zdnet.co.kr" + href
                
            h3_tag = link_tag.find("h3")
            if not h3_tag:
                continue
                
            title = h3_tag.get_text(strip=True)
            
            byline_span = post.select_one(".byline span")
            date_str = byline_span.get_text(strip=True) if byline_span else ""
            
            pub_time = parse_zdnet_time(date_str)
            now = datetime.now(KST)
            if pub_time and (now - pub_time).days <= 2:
                news_list.append({"title": title, "link": href, "source": "지디넷코리아"})
    except Exception as e:
        print(f"지디넷 크롤링 오류: {e}")
        
    return news_list

def send_slack_message(all_news):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("오류: SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.")
        return

    if not all_news:
        print("조건에 맞는(최근 48시간 이내) 기사가 없습니다.")
        return

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🗞️ 일일 주요 AI 뉴스 (최신)",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]

    for news in all_news:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"• `[{news['source']}]` <{news['link']}|*{news['title']}*>"
            }
        })

    payload = {
        "blocks": blocks
    }

    response = requests.post(
        webhook_url, 
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ 슬랙 메시지 전송 성공!")
    else:
        print(f"❌ 슬랙 메시지 전송 실패. 상태 코드: {response.status_code}, 응답: {response.text}")

if __name__ == "__main__":
    try:
        print("최신 뉴스를 가져오는 중...")
        
        zdnet = get_zdnet_news(limit=3)
        google = get_google_news(limit=5)
        naver = get_naver_news(limit=3)
        
        all_news = zdnet + google + naver
        
        print(f"지디넷 {len(zdnet)}개, 구글 {len(google)}개, 네이버 {len(naver)}개의 기사를 가져왔습니다.")
        send_slack_message(all_news)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
