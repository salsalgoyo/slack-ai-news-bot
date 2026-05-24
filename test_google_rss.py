import feedparser
url = "https://news.google.com/rss/search?q=AI+site:n.news.naver.com&hl=ko&gl=KR&ceid=KR:ko"
feed = feedparser.parse(url)
with open("rss_out.txt", "w", encoding="utf-8") as f:
    for entry in feed.entries[:1]:
        f.write(entry.title + "\n")
        f.write(entry.description + "\n")
