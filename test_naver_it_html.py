import requests, bs4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
res = requests.get('https://news.naver.com/section/105', headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
with open("naver_it_full.txt", "w", encoding="utf-8") as f:
    item = soup.select_one('.sa_item_inner')
    f.write(item.prettify() if item else "Not found")
