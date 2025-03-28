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
        try:
            response = requests.get(url, headers=self.header, verify=False)  # SSL 검증을 활성화
            response.raise_for_status()  # 상태 코드 4xx, 5xx일 때 예외 발생
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def url_parse(self, url):
        url = self.absurl(url)
        response = self.url_request(url)
        if response:
            return self.beautiful_soup(response)
        return None

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
        last_crawled_title = None
        new_news = []

        # 기존 HTML 파일에서 이미 크롤링된 뉴스 제목 추출
        old_news = []
        if os.path.exists('boan_news.html'):
            with open('boan_news.html', 'r', encoding='utf-8') as f:
                old_content = f.read()
            old_soup = BeautifulSoup(old_content, 'html.parser')
            for title_tag in old_soup.find_all('h2'):
                title_text = title_tag.get_text(strip=True).replace('New', '').strip()
                new_titles.add(title_text)
                # 기존 뉴스에서 'New' 배지를 제거
                title_tag.find('span', class_='new-badge') and title_tag.find('span', class_='new-badge').extract()
            old_news = old_soup.find_all('div', class_='news-item')

        # 새 뉴스 크롤링
        for page_num in range(1, 6):  # 5페이지까지 크롤링
            soup = self.url_parse(f'/media/list.asp?Page={page_num}&mkind=1&kind=')
            if soup:
                title_links = soup.find_all('div', class_='news_main_title')

                for link in title_links:
                    href = link.find('a')['href']
                    if href:
                        page_soup = self.url_parse(href)
                        if page_soup:
                            title = self.get_title(page_soup)

                            if title in new_titles:
                                continue

                            content = self.get_content(page_soup)
                            time = self.get_time(page_soup)

                            if title and content and time:
                                new_news.append(f"""
                                <div class="news-item">
                                    <h2>{title} <span class="new-badge">New</span></h2>
                                    <time>{time}</time>
                                    <p>{content}</p>
                                    <span class="delete-button" onclick="deleteNews(this)">삭제</span>
                                </div>
                                """)
                                new_titles.add(title)
                                if not last_crawled_title:
                                    last_crawled_title = title
                            sleep(1)  # 크롤링 속도 개선을 위한 대기 시간
            else:
                print(f"페이지 {page_num} 크롤링 실패.")
                break

        # 새로운 HTML 생성 (기존 뉴스 유지, 새 뉴스 상단 추가)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>&#128680;보안 뉴스</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                h1 {{ color: #333; text-align: center; }}
                .last-crawled {{ color: #d9534f; text-align: center; margin-bottom: 20px; }}
                .news-item {{ background-color: #fff; margin-bottom: 20px; padding: 15px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                .news-item h2 {{ color: #1e70bf; }}
                .new-badge {{ color: #fff; background: #d9534f; padding: 2px 5px; border-radius: 5px; font-size: 0.8em; margin-left: 5px; }}
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
            {f'<div class="last-crawled">마지막 크롤링 뉴스: {last_crawled_title}</div>' if last_crawled_title else ''}
            {''.join(new_news)}
            {''.join(str(item) for item in old_news)}
        </body>
        </html>
        """

        # 새 HTML 파일 생성
        with open('boan_news.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 출력 메시지
        if new_news:
            print("뉴스 내용이 추가되었습니다. boan_news.html에서 확인하세요.")
        else:
            print("새로운 뉴스가 없습니다.")

if __name__ == "__main__":
    boan = BoanCrawler()  # 선언
    boan.crawl_news()
