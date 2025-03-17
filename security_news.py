import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin

class BoanCrawler:
    def __init__(self):
        self.host = 'https://www.boannews.com'
        self.header = {
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

    def absurl(self, path):
        """상대 경로를 절대 경로로 변환"""
        return urljoin(self.host, path)

    def beautiful_soup(self, response):
        """응답을 BeautifulSoup으로 변환"""
        return BeautifulSoup(response.text, 'html.parser')

    def url_request(self, url):
    # requests.get 호출 시 verify=False를 추가하여 SSL 인증서 검증을 비활성화합니다.
        return requests.get(url, headers=self.header, verify=False)

    def url_parse(self, url):
        """URL 파싱"""
        url = self.absurl(url)
        response = self.url_request(url)
        soup = self.beautiful_soup(response)
        return soup

    def find_title_link(self, soup):
        """제목 링크 추출"""
        title_link_tag = soup.find('div', class_='news_main_title')
        if title_link_tag:
            return title_link_tag.find('a')['href']
        return None

    def get_title(self, soup):
        """뉴스 제목 추출"""
        title_tag = soup.find('div', id='news_title02')
        if title_tag:
            return title_tag.get_text(strip=True)
        else:
            print("제목을 찾을 수 없습니다.")
            return None

    def get_content(self, soup):
        """뉴스 본문 추출"""
        content_tag = soup.find('div', id='news_content')
        if content_tag:
            for tag in content_tag.find_all(['br', 'div', 'p', 'img']):
                tag.extract()  # 불필요한 태그 제거
            return content_tag.get_text('\n', strip=True)
        else:
            print("본문을 찾을 수 없습니다.")
            return None

    def get_time(self, soup):
        """뉴스 작성일 추출"""
        time_tag = soup.find('div', id='news_util01')
        if time_tag:
            return time_tag.get_text(strip=True)
        else:
            print("작성일을 찾을 수 없습니다.")
            return None

    def crawl_news(self):
        """뉴스 크롤링"""
        soup = self.url_parse('/media/list.asp?Page=1&mkind=1&kind=')
        # 뉴스 제목 링크들 추출
        title_links = soup.find_all('div', class_='news_main_title')
        for link in title_links:
            href = link.find('a')['href']
            if href:
                page_soup = self.url_parse(href)
                title = self.get_title(page_soup)
                content = self.get_content(page_soup)
                time = self.get_time(page_soup)
                if title and content and time:
                    print(f'[{title}]')
                    print(f"작성일: {time}")
                    print(content, end='\n\n')
            sleep(2)


if __name__ == "__main__":
    boan = BoanCrawler()
    boan.crawl_news()
