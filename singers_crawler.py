import requests
from bs4 import BeautifulSoup 
import json
import time


rootUrl = 'https://mojim.com/'

def extract_info(singersInfo,category):
    ret = {
        'singer': singersInfo.get_text(),
        'singer_url': rootUrl + singersInfo.get('href')
    }
    return ret


def parse_singers_list(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    findClass = soup.find("ul", class_ = "s_listA")
    tagAlist = findClass.find_all('a')
    return tagAlist


def real_main():
    crawlCnt = 0
    fp = open('./crawl_target.json', 'r')
    categoryList = json.load(fp)
    singersCrawl = []
    for category in categoryList:
        crawlCnt += 1
        singersList = parse_singers_list(category['pinyin_url'])
        for singer in singersList:
            ret = extract_info(singer, category)
            category.update(ret)
            singersCrawl.append(dict(category))

        print('[%d] pinyin: %s ............ %d' % (crawlCnt,category['pinyin'],len(singersList)))

    # with open('singers_list.json', 'w') as fs:
    #     fs.write(json.dumps(singersCrawl, indent=4, ensure_ascii=False))

    print(len(singersCrawl))
    fp.close()


if __name__ == '__main__':
    real_main()