#from urllib.request import urlopen
#from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import sys
import re
import csv
import time



def getHtml(url):

    data = {'obj': None, 'resp_url': None}

    if url == 'N': return data

    try:
        #html = urlopen(url, timeout=3)
        #bsObj = BeautifulSoup(html.read(), "html.parser")

        response = requests.get(url, timeout=3, verify=False)
        data['obj'] = BeautifulSoup(response.content, "html.parser")

        # url로 접속시 다른 사이트로 리다이렉트되었을 경우를 위해 저장
        data['resp_url'] = response.url

    except Exception as e:
        print(e)

    finally:
        return data



def getWikiLinks(data):

    url = "https://en.wikipedia.org/wiki/List_of_programming_languages"
    bsObj = getHtml(url)['obj']

    try:
        divs = bsObj.findAll("div", {"class":"div-col columns column-count column-count-2"})
        for div in divs:
            for a in div.findAll("a"):
                data.append( [a.get_text(), a["href"]] )
    except AttributeError as e:
        print(e)
        return None

    print("== getWikiLinks ... ==")
    print("total: {}\n".format(len(data)))



def getWikiWebSiteLogoLinks(data):

    for i, row in enumerate(data):

        print("== getWikiWebSiteLogoLinks ... ==")

        wiki_img_url = official_url = 'N'
        bsObj = getHtml("https://en.wikipedia.org"+row[1])['obj']

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
            wiki_img_url = re.sub(r'^//','https://', wiki_img_url)
            row.append(wiki_img_url)

        # 우측 정보 테이블 내 Website 링크(공식사이트)
        try:
            official_url = table.find("th", text="Website").next_sibling.next_sibling.a.attrs["href"]
        except AttributeError as e:
            #print(i, e)
            pass
        finally:
            official_url = re.sub(r'^//','https://', official_url)
            row.append(official_url)

        print(row)
        print("total: {} done: {}\n".format(len(data), i+1))



def getImgLink1(bsObj, home_url):

    if bsObj == None: return None

    o = urlparse(home_url)
    base = o.scheme + "://" + o.netloc

    # img src case 1:
    # / or https://www.python.org/ or https://www.python.org
    # img src case 2:
    # /index/ or /index or
    # https://www.python.org/index/ or #https://www.python.org/index
    if o.path in ('', '/'):
        regex_list = ['/', base+'/', base]
    else:
        path = o.path
        if o.path[-1] != '/':
            path += '/'
        regex_list = [path, path[0:-1], base + path, base + path[0:-1]]

    regex = [ '^' + l + '$' for l in regex_list ]

    try:
        src = None
        a_tags2 = bsObj.findAll("a", href=re.compile("|".join(regex)))

        for a in a_tags2:
            if a.img is not None:
                src = a.img.attrs["src"]
                break

    except AttributeError as e:
        #print("loop:{}, message:{}".format(i, e))
        pass

    finally:
        return src



def getImgLink2(bsObj, *args):

    if bsObj == None: return None

    # 이미지 태그의 속성값 중 logo가 포함된 이미지
    try:
        src = None
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
                    src = img.attrs["srcset"].split(',')[0]
                else:
                    src = img.attrs["src"]
                break

    except AttributeError as e:
        #print("loop:{}, message:{}".format(i, e))
        pass

    finally:
        return src



def getOfficialSiteLogoLinks(data):

    for i, row in enumerate(data):

        print("== getOfficialSiteLogoLinks ... ==")

        result = getHtml(row[3])
        bsObj = result['obj']

        img_link = 'N'
        funcs = (getImgLink1, getImgLink2)

        if row[3] != 'N':
            row[3] = result['resp_url']

        for func in funcs:
            link = func(bsObj, row[3])

            if link != None:
                img_link = link
                break

        row.append(img_link)

        print(row)
        print("total: {} done: {}\n".format(len(data), i+1))



def postProcess(data):

    file_name = 'data_'+time.strftime("%Y%m%d_%H_%M")
    f = open(file_name+".csv", 'a+')

    writer = csv.writer(f)
    writer.writerow(('name','wikipedia url','wikipedia logo url',
                     'official site url','official site logo url'))

    for row in data:
        writer.writerow(row)

    f.close()

    makeHtml(data, file_name)



def makeHtml(data, file_name):

    html = \
    '''
    <h3><a href="{official_site_url}" target="_blank">{name}</a></h3>
    <li>scrapped image</li>
    <img src="{scrapped_img_src}">

    <li><a href="{wikipedia_url}" target="_blank">wikipedia</a> image</li>
    <img src="{wikipedia_img_src}">
    <hr>
    '''

    with open(file_name+".html", 'a+') as f:
        for row in data:
            if row[4] == 'N':
                continue

            img_src = urljoin(row[3], row[4])
            wiki_url = urljoin("https://en.wikipedia.org", row[1])

            f.write(html.format(official_site_url = row[3],
                                name = row[0],
                                scrapped_img_src = img_src,
                                wikipedia_url = wiki_url,
                                wikipedia_img_src = row[2]
                                )
            )



def summary(data):

    wikipedia_logo_url = official_site_url = official_site_logo_url = 0
    names = []
    total = len(data)

    for row in data:

        if row[2] != 'N': wikipedia_logo_url += 1
        if row[3] != 'N': official_site_url += 1
        if row[4] != 'N': official_site_logo_url += 1

        # 추가로 점검할 조건
        if row[2] != 'N' and row[3] != 'N' and row[4] == 'N':
            names.append(row[0])

    print("\n[ Summary ]")
    print("* toral rows: {}".format(total))

    print("* wikipedia_logo_url (row[2])")
    print("  - exist: {}".format(wikipedia_logo_url))
    print("  - exist(N): {}\n".format(total - wikipedia_logo_url))

    print("* official_site_url (row[3])")
    print("  - exist: {}".format(official_site_url))
    print("  - no exist(N): {}\n".format(total - official_site_url))

    print("* official_site_logo_url (row[4])")
    print("  - exist: {}".format(official_site_logo_url))
    print("  - no exist(N): {}\n".format(total - official_site_logo_url))

    print("* to check (wikipedia_logo_url, official_site_url exist, but official_site_logo_url is 'N')")
    print("  - count: {}".format(len(names)))
    print("  - data: {}\n".format(names))





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
    postProcess(data)
    summary(data)
