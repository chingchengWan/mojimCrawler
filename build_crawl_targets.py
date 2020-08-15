import requests
from bs4 import BeautifulSoup 
import json


root_url = 'https://mojim.com/'

def parse_categories(start_url = 'https://mojim.com/twza1.htm'):
    resp = requests.get(start_url)
    soup = BeautifulSoup(resp.text, 'lxml')
    # extract category table on top
    temp = soup.find(id = 'mx123_T1')
    # extract first row of table
    temp = temp.find('tr')
    cates = temp.find_all('a')
    ret = list()
    for cate in cates:
        ret.append((cate.get_text(), root_url + cate.get('href')))
    return ret


def tag_extract_info(label, category):
    ret = {
        'category': category,
        'pinyin': label.get_text(),
        'pinyin_url': root_url + label.get('href')
    }
    return ret


def parse_article_label(doc):
    postEntries = doc.find(id='mx123_T2')
    tagAlist = postEntries.find_all('a')
    return tagAlist


def real_main():
    category_list = parse_categories()
    crawl_targets = []
    for category in category_list:
        url = category[1] 
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        labels = parse_article_label(soup)
        for label in labels:
            if label.get_text() == '熱門':
                continue

            rec = tag_extract_info(label, category[0])
            crawl_targets.append(rec)
    # with open('crawl_target.json', 'w') as fp:
    #     fp.write(json.dumps(crawl_targets, indent=4, ensure_ascii=False))

    print(len(crawl_targets))
    
if __name__ == '__main__':
    real_main()