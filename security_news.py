import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin
import os

class BoanCrawler:
    def __init__(self):
        self.host = 'https://www.boannews.com'
        self.header = {
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

    def absurl(self, path):
        return urljoin(self.host, path)

    def beautiful_soup(self, response):
        return BeautifulSoup(response.text, 'html.parser')

    def url_request(self, url):
        return requests.get(url, headers=self.header, verify=False)

    def url_parse(self, url):
        url = self.absurl(url)
        response = self.url_request(url)
        soup = self.beautiful_soup(response)
        return soup

    def get_title(self, soup):
        title_tag = soup.find('div', id='news_title02')
        return title_tag.get_text(strip=True) if title_tag else None

    def get_content(self, soup):
        content_tag = soup.find('div', id='news_content')
        if content_tag:
            for tag in content_tag.find_all(['br', 'div', 'p', 'img']):
                tag.extract()
            return content_tag.get_text('\n', strip=True)
        return None

    def get_time(self, soup):
        time_tag = soup.find('div', id='news_util01')
        return time_tag.get_text(strip=True) if time_tag else None

    def crawl_news(self):
        new_titles = set()
        news_items = ""

        # 기존 HTML 파일에서 이미 크롤링된 뉴스 제목 추출
        old_news = []
        if os.path.exists('boan_news.html'):
            with open('boan_news.html', 'r', encoding='utf-8') as f:
                old_content = f.read()
            old_soup = BeautifulSoup(old_content, 'html.parser')
            for title_tag in old_soup.find_all('h2'):
                new_titles.add(title_tag.text)
            old_news = old_soup.find_all('div', class_='news-item')

        # 새 뉴스 크롤링
        soup = self.url_parse('/media/list.asp?Page=1&mkind=1&kind=')
        title_links = soup.find_all('div', class_='news_main_title')
        for link in title_links:
            href = link.find('a')['href']
            if href:
                page_soup = self.url_parse(href)
                title = self.get_title(page_soup)

                # 중복 방지: 이미 있는 경우는 건너뜀
                if title in new_titles:
                    continue

                content = self.get_content(page_soup)
                time = self.get_time(page_soup)

                if title and content and time:
                    news_items += f"""
                    <div class="news-item">
                        <h2>{title}</h2>
                        <time>{time}</time>
                        <p>{content}</p>
                        <span class="delete-button" onclick="deleteNews(this)">삭제</span>
                    </div>
                    """
                    new_titles.add(title)
                sleep(5)

        # 새로운 HTML 생성 (기존 뉴스 유지, 새 뉴스 상단 추가)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>보안 뉴스</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                h1 {{ color: #333; text-align: center; }}
                .news-item {{ background-color: #fff; margin-bottom: 20px; padding: 15px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                .news-item h2 {{ color: #1e70bf; }}
                .news-item time {{ color: #888; font-size: 14px; }}
                .news-item p {{ line-height: 1.6; }}
                .delete-button {{ color: red; cursor: pointer; font-weight: bold; margin-top: 10px; }}
            </style>
            <script>
                function deleteNews(element) {{
                    var newsItem = element.parentElement;
                    newsItem.remove();
                }}
            </script>
        </head>
        <body>
            <h1>&#128680;Security News&#128680;</h1>
            {news_items}
        </body>
        </html>
        """

        # 기존 뉴스 추가 (중복 방지)
        with open('boan_news.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            for item in old_news:
                f.write(str(item))

        print("HTML 파일에 뉴스 내용이 추가되었습니다. boan_news.html에서 확인하세요.")

if __name__ == "__main__":
    boan = BoanCrawler()
    boan.crawl_news()
