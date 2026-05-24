import os
import requests
from bs4 import BeautifulSoup
import json
import feedparser

RSS_FEEDS: dict[str, str] = {
    "Anthropic":        "https://www.anthropic.com/rss.xml",
    "OpenAI":           "https://openai.com/news/rss.xml",
    "Google DeepMind":  "https://deepmind.google/blog/rss.xml",
    "Hugging Face":     "https://huggingface.co/blog/feed.xml",
    "TechCrunch AI":    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI":     "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "MIT Tech Review":  "https://www.technologyreview.com/feed/",
    "Ars Technica":     "https://feeds.arstechnica.com/arstechnica/technology-lab",
}

def get_zdnet_ai_news():
    url = "https://search.zdnet.co.kr/?kwd=AI"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    news_posts = soup.find_all("div", class_="newsPost")
    
    news_list = []
    # 국내 뉴스는 상위 3개만 가져옵니다 (해외 뉴스와 밸런스를 맞추기 위함)
    for post in news_posts[:3]:
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
        news_list.append({"title": title, "link": href, "source": "지디넷코리아"})
        
    return news_list

def get_rss_news():
    news_list = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                # 각 소스별로 가장 최신 기사 1개씩만 가져옵니다.
                latest_entry = feed.entries[0]
                news_list.append({
                    "title": latest_entry.title,
                    "link": latest_entry.link,
                    "source": source
                })
        except Exception as e:
            print(f"{source} RSS 파싱 오류: {e}")
            continue
    return news_list

def send_slack_message(zdnet_news, rss_news):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("오류: SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.")
        return

    if not zdnet_news and not rss_news:
        print("가져올 뉴스 기사가 없습니다.")
        return

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🗞️ 일일 글로벌 AI 최신 뉴스",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]

    if zdnet_news:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🇰🇷 국내 AI 주요 뉴스 (지디넷코리아)*"
            }
        })
        for news in zdnet_news:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• <{news['link']}|*{news['title']}*>"
                }
            })
        blocks.append({"type": "divider"})

    if rss_news:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🌍 해외 빅테크 & IT매체 AI 뉴스*"
            }
        })
        for news in rss_news:
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
        print("뉴스를 가져오는 중...")
        zdnet = get_zdnet_ai_news()
        rss = get_rss_news()
        
        print(f"지디넷 {len(zdnet)}개, 해외 RSS {len(rss)}개의 기사를 가져왔습니다. 슬랙으로 전송합니다...")
        send_slack_message(zdnet, rss)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
