#from urllib.request import urlopen
#from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import sys
import re
import csv
import time
import threading
import os




class LogoScrap:

    data = []
    index = []
    thread_check = [None]
    statistic = {'wikipedia_logo_url':0, 'official_site_url':0, 'official_site_logo_url':0, 'hmm':[]}


    def __init__(self, number):
        self.url = "https://en.wikipedia.org/wiki/List_of_programming_languages"
        self.thread_num = number
        LogoScrap.thread_check = [None]*number


    def checkThread(self):

        while True:
            time.sleep(2)

            print("[ Thread Status ]")
            print(LogoScrap.thread_check)

            check = [data['complete'] for data in LogoScrap.thread_check]

            if all(check):
                print("ALL COMPLETE!")
                self.mergeFile()
                self.report()
                return None


    def mergeFile(self):
        csv_header = ('name','wikipedia url', 'wikipedia logo url', 'official site url', 'official site logo url')
        file_name = 'data_'+time.strftime("%Y%m%d_%H_%M")
        files = [data['file'] for data in LogoScrap.thread_check]

        with open(file_name+".csv", 'a+') as csv_file, open(file_name+".html", 'a+') as html_file:
             for f in files:
                with open(f+'.csv') as cf, open(f+'.html') as hf:
                    csv_file.write(cf.read())
                    html_file.write(hf.read())

        for f in files:
            os.remove(f+'.csv')
            os.remove(f+'.html')


    def getWikiLinks(self):

        print("== getWikiLinks ... ==")
        bsObj = LogoScrap.getHtml(self.url)['obj']

        try:
            divs = bsObj.findAll("div", {"class":"div-col columns column-count column-count-2"})
            for div in divs:
                for a in div.findAll("a"):
                    LogoScrap.data.append([a.get_text(), a["href"]])

        except AttributeError as e:
            print(e)
            return None

        data_total = len(LogoScrap.data)
        devide = data_total // self.thread_num
        LogoScrap.index = [i for i in range(0, data_total, devide)]
        LogoScrap.index = LogoScrap.index[:self.thread_num]
        LogoScrap.index.append(data_total)

        #print(LogoScrap.index)
        print("\n[ Info ]")
        print("- total data lenth: {}".format(data_total))
        print("- thread lenth: {}".format(self.thread_num))
        print("- index lenth: {}\n".format(len(LogoScrap.index)))
        time.sleep(1)


    @staticmethod
    def getHtml(url):

        print("==> getHtml ...")
        data = dict(obj=None, resp_url=None)

        if url == 'N':
            return data

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


    @staticmethod
    def getImgLink1(bsObj, home_url):

        print("==> getImgLink1 ...")

        if bsObj == None:
            return None

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


    @staticmethod
    def getImgLink2(bsObj, *args):

        print("==> getImgLink2 ...")

        if bsObj == None:
            return None

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


    def report(self):

        total = len(LogoScrap.data)
        wikipedia_logo_url = LogoScrap.statistic['wikipedia_logo_url']
        official_site_url = LogoScrap.statistic['official_site_url']
        official_site_logo_url = LogoScrap.statistic['official_site_logo_url']

        print("\n[ Report ]")
        print("* toral data: {}\n".format(total))

        print("* wikipedia_logo_url")
        print("  - exist: {}".format(wikipedia_logo_url))
        print("  - not exist(N): {}\n".format(total - wikipedia_logo_url))

        print("* official_site_url")
        print("  - exist: {}".format(official_site_url))
        print("  - not exist(N): {}\n".format(total - official_site_url))

        print("* official_site_logo_url")
        print("  - exist: {}".format(official_site_logo_url))
        print("  - not exist(N): {}\n".format(total - official_site_logo_url))

        print("* to check (wikipedia_logo_url, official_site_url exist, but official_site_logo_url is 'N')")
        print("  - count: {}".format(len(LogoScrap.statistic['hmm'])))
        print("  - data: {}\n".format(LogoScrap.statistic['hmm']))




class LogoScraper:

    def __init__(self, number):

        self.data = []
        self.instance_num = number
        self.fp = [None]*2

        self.index_start = LogoScrap.index[self.instance_num]
        self.index_end = LogoScrap.index[self.instance_num+1]
        self.data.extend(LogoScrap.data[self.index_start:self.index_end])

        self.file_name = str(self.instance_num)+'_data'
        self.fp[0] = open(self.file_name+".csv", 'a+')
        self.fp[1] = open(self.file_name+".html", 'a+')

        LogoScrap.thread_check[self.instance_num] = {'done': 0, 'complete': False, 'file':None}


    def scrap(self):

        for i, row in enumerate(self.data):
            temp = []
            temp.extend(row)

            self.getWikiWebSiteLogoLinks(temp)
            self.getOfficialSiteLogoLinks(temp)
            self.writeCSV(temp)
            self.writeHTML(temp)
            self.statistic(temp)
            LogoScrap.thread_check[self.instance_num]['done'] = i+1

        self.afterJobDone()


    def afterJobDone(self):
        for i in range(2):
            self.fp[i].close()
        LogoScrap.thread_check[self.instance_num]['complete'] = True
        LogoScrap.thread_check[self.instance_num]['file'] = self.file_name


    def statistic(self, row):

        if row[2] != 'N': LogoScrap.statistic['wikipedia_logo_url'] += 1
        if row[3] != 'N': LogoScrap.statistic['official_site_url'] += 1
        if row[4] != 'N': LogoScrap.statistic['official_site_logo_url'] += 1

        # 추가로 점검할 것
        if row[2] != 'N' and row[3] != 'N' and row[4] == 'N':
            LogoScrap.statistic['hmm'].append(row[0])


    def getWikiWebSiteLogoLinks(self, row):

        print("== getWikiWebSiteLogoLinks ... ==")

        wiki_img_url = official_url = 'N'
        bsObj = LogoScrap.getHtml("https://en.wikipedia.org"+row[1])['obj']

        # 우측 정보 테이블
        try:
            table = bsObj.find("table", {"class":"infobox vevent"})
        except AttributeError as e:
            #print("loop:{}, message:{}".format(i, e))
            row.append(wiki_img_url)
            row.append(official_url)
            return None

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


    def getOfficialSiteLogoLinks(self, row):

        print("== getOfficialSiteLogoLinks ... ==")

        result = LogoScrap.getHtml(row[3])
        bsObj = result['obj']

        img_link = 'N'
        funcs = (LogoScrap.getImgLink1, LogoScrap.getImgLink2)

        if row[3] != 'N':
            row[3] = result['resp_url']

        for func in funcs:
            link = func(bsObj, row[3])

            if link != None:
                img_link = link
                break

        row.append(img_link)


    def writeCSV(self, row):

        writer = csv.writer(self.fp[0])
        writer.writerow(row)


    def writeHTML(self, row):

        if row[4] == 'N':
            return None

        html = \
        '''
        <h3><a href="{official_site_url}" target="_blank">{name}</a></h3>
        <li>scrapped image</li>
        <img src="{scrapped_img_src}">

        <li><a href="{wikipedia_url}" target="_blank">wikipedia</a> image</li>
        <img src="{wikipedia_img_src}">
        <hr>
        '''

        img_src = urljoin(row[3], row[4])
        wiki_url = urljoin("https://en.wikipedia.org", row[1])

        self.fp[1].write(html.format(official_site_url = row[3],
                                        name = row[0],
                                        scrapped_img_src = img_src,
                                        wikipedia_url = wiki_url,
                                        wikipedia_img_src = row[2]))




'''
final data list values:
data = [ [name,
          wikipedia url,
          wikipedia logo url,
          official site url,
          official site logo url], ... ]
'''
if __name__ == "__main__":

    THREAD_NUM = 30
    scrap = LogoScrap(THREAD_NUM)
    scrap.getWikiLinks()

    for i in range(THREAD_NUM):
        instance = LogoScraper(i)
        t = threading.Thread(target=instance.scrap)
        t.daemon = True
        t.start()

    scrap.checkThread()
