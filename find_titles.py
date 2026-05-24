import requests, bs4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
res = requests.get('https://search.naver.com/search.naver?where=news&query=AI&sort=1', headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

with open("naver_titles.txt", "w", encoding="utf-8") as f:
    # Just find all <a> tags that contain the word "AI"
    for a in soup.find_all('a'):
        text = a.get_text(strip=True)
        if 'AI' in text or '인공지능' in text:
            f.write(f"Class: {a.get('class')} | Text: {text}\n")
