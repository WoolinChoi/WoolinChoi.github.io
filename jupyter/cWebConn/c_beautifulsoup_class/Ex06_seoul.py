"""
http://www.seoul.go.kr > 청사안내 > 자치구
https://www.seoul.go.kr/seoul/autonomy.do

BeautifulSoup  : 파서를 이용해서 html 의 요소를 추출하게 해주는 모듈
        - 단점은 개행문자를 고려해야 한다
Tag : 태그
NavigableString : 원래는 tag 사이의 문자열

#  xpath를 사용하면 개행문자를 고려하지 않아도 된단다
#  https://developer.mozilla.org/ko/docs/XPath
"""

import requests
from bs4 import BeautifulSoup, NavigableString

# 웹 문서 가져오기
url = "https://www.seoul.go.kr/seoul/autonomy.do"
html = requests.get(url).text

# 구청이름 / 구청주소 / 구청전화번호 / 구청홈페이지
soup = BeautifulSoup(html, "html.parser")

tabcont = soup.select('.tabcont')
for tab in tabcont:
    li = tab.find_all('li')
    print(tab.strong.text+'청', '/', li[0].text, '/', li[1].text, '/', li[2].a.text)