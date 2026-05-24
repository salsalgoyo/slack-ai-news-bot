import requests, bs4
soup = bs4.BeautifulSoup(requests.get('https://search.naver.com/search.naver?where=news&query=AI&sort=1', headers={'User-Agent': 'Mozilla/5.0'}).text, 'html.parser')
with open("naver_bx.txt", "w", encoding="utf-8") as f:
    item = soup.select_one('ul.list_news > li.bx')
    f.write(item.prettify() if item else "Not found")
