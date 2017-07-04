### Description
- 위키피디아 페이지 내 공식 사이트 url로 접속 후 로고 이미지 url 수집
- 로고 이미지 선정 기준:
  1. 링크 주소가 / 인 a 태그 안의 이미지 (getImgLink1)
  2. 이미지 태그의 속성값 중 logo 문자열이 포함된 이미지 (getImgLink2)
- 결과물: data.csv
  name, wiki url, wiki logo url, official site url, official site logo url

### Usage
    python3 logo_scraper.py
