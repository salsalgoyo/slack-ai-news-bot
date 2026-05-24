import requests

def test_naver():
    url = "https://search.naver.com/search.naver?where=news&query=AI&sort=1"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    with open("naver_search.html", "w", encoding="utf-8") as f:
        f.write(res.text)

test_naver()
