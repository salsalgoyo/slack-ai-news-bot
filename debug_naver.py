import requests, bs4
soup = bs4.BeautifulSoup(requests.get('https://search.naver.com/search.naver?where=news&query=AI&sort=1', headers={'User-Agent': 'Mozilla/5.0'}).text, 'html.parser')
with open("naver_dates.txt", "w", encoding="utf-8") as f:
    for item in soup.select('.bx'):
        info_tags = item.select(".info_group span.info")
        f.write(info_tags[-1].get_text(strip=True) if info_tags else "Empty")
        f.write("\n")
