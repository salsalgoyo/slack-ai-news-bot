import requests, bs4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
res = requests.get('https://n.news.naver.com/mnews/article/025/0003525396', headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
with open("naver_article.txt", "w", encoding="utf-8") as f:
    date_tags = soup.select('.media_end_head_info_datestamp_time')
    for tag in date_tags:
        f.write(tag.get('data-date-time', tag.get_text(strip=True)) + "\n")
