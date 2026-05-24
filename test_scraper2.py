import requests
from bs4 import BeautifulSoup
import sys

def test_naver():
    url = "https://search.naver.com/search.naver?where=news&query=AI&sort=1"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".bx")
    with open("test_out2.txt", "w", encoding="utf-8") as f:
        f.write(f"Naver items: {len(items)}\n")
        for item in items[:5]:
            tit = item.select_one(".news_tit")
            if tit:
                info = item.select(".info_group span.info")
                date_str = info[-1].text if info else "Unknown"
                f.write(f"{tit.text} | {date_str}\n")

test_naver()
