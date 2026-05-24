import requests, bs4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.naver.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}
res = requests.get('https://search.naver.com/search.naver?where=news&query=AI&sort=1', headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
with open("naver_debug.txt", "w", encoding="utf-8") as f:
    f.write(f"Status: {res.status_code}\n")
    items = soup.select('.bx')
    f.write(f"Found .bx items: {len(items)}\n")
    for item in items[:3]:
        tit = item.select_one('.news_tit')
        if tit:
            f.write(tit.get_text() + "\n")
