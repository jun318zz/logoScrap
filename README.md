### Description
- 위키피디아 페이지 내 공식 사이트 url로 접속 후 로고 이미지 url 수집
- 로고 이미지 선정 기준:
  1. 링크 주소가 / 인 a 태그 안의 이미지 (getImgLink1)
  2. 이미지 태그의 속성값 중 logo 문자열이 포함된 이미지 (getImgLink2)
- 결과물
  1. csv 파일: 'data_'+time.strftime("%Y%m%d_%H_%M")+'.csv'<br>
     (name, wikipedia url, wikipedia logo url, official site url, official site logo url, verified)
  2. html 파일: csv 파일과 동일 이름의 .html 파일
- 기타
  1. 추가 설치 패키지 <br>
     pip install requests[security]
  2. 이미지 수집 샘플 페이지 <br>
     https://jun318zz.github.io/logoScrap.html
  3. 개인사이트(로고 수집) <br>
     https://jjun.herokuapp.com/logo/
### Usage
    python3 logo_scraper.py
