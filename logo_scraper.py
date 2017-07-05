#from urllib.request import urlopen
#from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import requests
import sys
import re
import csv
import time



def getHtml(url):

    try:
        #html = urlopen(url, timeout=3)
        #bsObj = BeautifulSoup(html.read(), "html.parser")
        html = requests.get(url, timeout=3)
        bsObj = BeautifulSoup(html.content, "html.parser")

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

        print("== getWikiWebSiteLogoLinks ... ==")
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
                if 'src' not in img.attrs.keys():
                    return img.attrs["srcset"].split(',')[0]
                else:
                    return img.attrs["src"]

    except AttributeError as e:
        #print("loop:{}, message:{}".format(i, e))
        pass

    return None



def getOfficialSiteLogoLinks(data):

    file_name = 'data_'+time.strftime("%Y%m%d_%H_%M")+'.csv'
    f = open(file_name, 'a+')
    writer = csv.writer(f)

    for i, row in enumerate(data):

        bsObj = getHtml(row[3])
        img_link = 'N'
        funcs = (getImgLink1, getImgLink2)

        for func in funcs:
            link = func(bsObj)
            if link != None:
                img_link = link
                break

        row.append(img_link)

        print("== getOfficialSiteLogoLinks ... ==")
        writer.writerow(row)
        print(row)
        print("total: {} done: {}".format(len(data), i+1))

    f.close()



def summary(data):

    wikipedia_logo_url = official_site_url = official_site_logo_url = 0
    names = []
    total = len(data)

    for row in data:
        if row[2] != 'N':
            wikipedia_logo_url += 1
            if row[4] == 'N':
                names.append(row[0])

        if row[3] != 'N':
            official_site_url += 1

        if row[4] != 'N':
            official_site_logo_url += 1

    print("\n[ Summary ]")
    print("* Toral rows: {}".format(total))

    print("- wikipedia_logo_url")
    print("  number of url: {}".format(wikipedia_logo_url))
    print("  number of N: {}\n".format(total - wikipedia_logo_url))

    print("- official_site_url")
    print("  number of url: {}".format(official_site_url))
    print("  number of N: {}\n".format(total - official_site_url))

    print("- official_site_logo_url")
    print("  number of url: {}".format(official_site_logo_url))
    print("  number of N: {}\n".format(total - official_site_logo_url))

    print("- wikipedia_logo_url exists, but official_site_logo_url is 'N'")
    print("  number: {}".format(len(names)))
    print("  data: {}\n".format(names))





'''
final data list values:
data = [ [name,
          wikipedia url,
          wikipedia logo url,
          official site url,
          official site logo url], ... ]
'''
if __name__ == "__main__":

    data = []
    getWikiLinks(data)
    getWikiWebSiteLogoLinks(data)
    getOfficialSiteLogoLinks(data)
    summary(data)
