import requests, bs4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
res = requests.get('https://news.naver.com/section/105', headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
with open("naver_it.txt", "w", encoding="utf-8") as f:
    for a in soup.select('.sa_text_title'):
        f.write(a.get_text(strip=True) + "\n")
