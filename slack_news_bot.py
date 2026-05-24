import os
import requests
from bs4 import BeautifulSoup
import json

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
    for post in news_posts[:5]:
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
        news_list.append({"title": title, "link": href})
        
    return news_list

def send_slack_message(news_list):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("오류: SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.")
        return

    if not news_list:
        print("가져올 뉴스 기사가 없습니다.")
        return

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🗞️ 지디넷코리아 AI 최신 뉴스",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]

    for news in news_list:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{news['title']}*\n<{news['link']}|기사 링크>"
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
        print("지디넷코리아에서 AI 뉴스를 가져오는 중...")
        news = get_zdnet_ai_news()
        if news:
            print(f"성공적으로 {len(news)}개의 기사를 가져왔습니다. 슬랙으로 전송합니다...")
            send_slack_message(news)
        else:
            print("뉴스를 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
