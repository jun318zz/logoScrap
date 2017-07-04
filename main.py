from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import sys
import re
import csv



def getHtml(url):

    try:
        html = urlopen(url, timeout=3)
        bsObj = BeautifulSoup(html.read(), "html.parser")
    except Exception as e:
        print(e)
        return None

    return bsObj



def getWikiLinks(data):

    url = "https://en.wikipedia.org/wiki/List_of_programming_languages"
    bsObj = getHtml(url)

    try:
        divs = bsObj.findAll("div", {"class":"div-col columns column-count column-count-2"})
        for div in divs:
            for a in div.findAll("a"):
                data.append( [a.get_text(), a["href"]] )
    except AttributeError as e:
        print(e)
        return None

    print("== getWikiLinks ... ==")
    print("total: {}".format(len(data)))



def getWikiWebSiteLogoLinks(data):

    for i, row in enumerate(data):

        wiki_img_url = official_url = 'N'
        bsObj = getHtml("https://en.wikipedia.org"+row[1])

        # 우측 정보 테이블
        try:
            table = bsObj.find("table", {"class":"infobox vevent"})
        except AttributeError as e:
            #print("loop:{}, message:{}".format(i, e))
            row.append(wiki_img_url)
            row.append(official_url)
            continue

        # 우측 정보 테이블 내 이미지
        try:
            wiki_img_url = table.tr.td.a.img.attrs["src"]
        except AttributeError as e:
            #print("loop:{}, message:{}".format(i, e))
            pass
        finally:
            row.append(wiki_img_url)

        # 우측 정보 테이블 내 Website 링크(공식사이트)
        try:
            official_url = table.find("th", text="Website").next_sibling.next_sibling.a.attrs["href"]
        except AttributeError as e:
            #print(i, e)
            pass
        finally:
            row.append(official_url)

        print("== getWebSiteLogoLinks ... ==")
        print(row)
        print("total: {} done: {}".format(len(data), i+1))



def getImgLink1(bsObj):

    # 링크 주소가 / 인 a 태그 안의 이미지
    try:
        a_tags = bsObj.findAll("a", href="/")
        for a in a_tags:
            if a.img is not None:
                return a.img.attrs["src"]

    except AttributeError as e:
        #print("loop:{}, message:{}".format(i, e))
        pass

    return None



def getImgLink2(bsObj):

    # 이미지 태그의 속성값 중 logo가 포함된 이미지
    try:
        imgs = bsObj.findAll("img")
        for img in imgs:

            # 이미지 태그의 모든 속성값 추출
            attr_list = []
            for key in img.attrs.keys():
                if key == "class":
                    attr_list.append(" ".join(img.attrs[key]))
                else:
                    attr_list.append(img.attrs[key])
                attr_str = " ".join(attr_list)

            if re.search("logo", attr_str) is not None:
                return img.attrs["src"]

    except AttributeError as e:
        #print("loop:{}, message:{}".format(i, e))
        pass

    return None



def getOfficialSiteLogoLinks(data):

    for i, row in enumerate(data):

        bsObj = getHtml(row[3])
        img_link = 'N'
        funcs = (getImgLink1, getImgLink2)

        for f in funcs:
            link = f(bsObj)
            if link != None:
                img_link = link
                break

        row.append(img_link)

        print("== getOfficialSiteLogoLinks ... ==")
        with open('data.csv', 'a+') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(row)
        print("total: {} done: {}".format(len(data), i+1))



'''
final data list values:
data = [ [name,
          wiki url,
          wiki logo url,
          official site url,
          official site logo url], ... ]
'''
if __name__ == "__main__":

    data = []
    getWikiLinks(data)
    getWikiWebSiteLogoLinks(data)
    getOfficialSiteLogoLinks(data)