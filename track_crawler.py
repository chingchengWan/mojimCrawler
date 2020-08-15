import requests
from bs4 import BeautifulSoup 
import json
from datetime import datetime
import re


rootUrl = 'https://mojim.com/'


def extract_album_list(trackList, album, releasedDate, albumIntro):
    albumInfo = {
        'album': album,
        'released_date': releasedDate,
        'album_intro': albumIntro,
        'tracks': trackList
    }
    # print(json.dumps(albumInfo, indent=4, ensure_ascii=False))
    return albumInfo


def extract_track_list(tagAlist, trackCnt):
    trackList = []
    for tagA in tagAlist:
        trackCnt += 1
        tackInfo = {
            'track': tagA.get_text(),
            'lyrics_url': rootUrl + tagA.get('href')
            }
        trackList.append(tackInfo)
    return (trackList, trackCnt)
        
def parse_album_intro(mainText):
    findTab0Class = mainText.find(class_ = "tab0")
    findTagA = findTab0Class.find_all('a')
    for TagA in findTagA:
        if TagA.get_text() == '專輯介紹':
            albumInfoUrl = rootUrl + TagA.get('href')
            resp = requests.get(albumInfoUrl)
            soup = BeautifulSoup(resp.text, 'lxml')
            findId = soup.find(id = "ss_y_tb3_1")
            albumIntro = str(findId.find('p'))
            return albumIntro
        else:
            continue
        
    return "None"

def parse_singer_intro(mainText):
    findTab0Class = mainText.find(class_ = "tab0")
    findTagA = findTab0Class.find_all('a')
    for TagA in findTagA:
        if TagA.get_text() == '歌手介紹':
            singerInfoUrl = rootUrl + TagA.get('href')
            resp = requests.get(singerInfoUrl)
            soup = BeautifulSoup(resp.text, 'lxml')
            findId = soup.find(id = "ss_y_tb3_1")
            singerIntro = str(findId.find('p'))
            return singerIntro
        else:
            continue
        
    return "None"

def parse_tagA_list(albumUrl):  
    tagAList = []
    newTagAList = []
    resp = requests.get(albumUrl)
    soup = BeautifulSoup(resp.text, 'lxml')
    findId = soup.find(id = "page3_01")
    parse_album_intro(findId)
    albumIntro = parse_album_intro(findId)
    findHc3Class = findId.find_all(class_ = "hc3")
    for hc3 in findHc3Class:
        tagAList.extend(hc3.find_all('a'))  

    for tagA in tagAList:
        if tagA.has_attr('class') and tagA['class'][0] == 'X3':
            continue
        newTagAList.append(tagA)

    findH2 = findId.find('h2')
    try:
        match = re.search(r'\d{4}-\d{2}-\d{2}', str(findH2))
        releasedDate = str(datetime.strptime(match.group(), '%Y-%m-%d').date())
        
    except:
        releasedDate = "None"
    

    return (newTagAList, releasedDate, albumIntro)


def parse_albums_list(hb2aUrl):
    resp = requests.get(hb2aUrl)
    soup = BeautifulSoup(resp.text, 'lxml')
    findId = soup.find(id = "fsYY002")
    findX3Class = findId.find_all(class_ = "X3")
    singerIntro = parse_singer_intro(soup)

    return (findX3Class, singerIntro)
    

def parse_tag_hb2a(hd2Url):
    resp = requests.get(hd2Url)
    soup = BeautifulSoup(resp.text, 'lxml')
    findHb2Class = soup.find(class_ = "hb2")
    findHc1Class = findHb2Class.find('a').get('href')
    return (rootUrl + findHc1Class)


def parse_tag_hd2(singerUrl):
    resp = requests.get(singerUrl)
    soup = BeautifulSoup(resp.text, 'lxml')
    findClass = soup.find(class_="hd2")
    tagAlist = findClass.find('a').get('href')
    return (rootUrl + tagAlist)


def real_main():
    try:
        seenDbPath = './singers_seenDB.txt'
        # load seenDB to avoid crawling repeat data
        try:
            with open(seenDbPath, 'r') as fp:
                seenDB = fp.read().splitlines()
        except:
            seenDB = []
        

        
        fp = open('./singers_list.json', 'r')
        singersList = json.load(fp)
        crawlCnt = 0
        totalAlbums = 0
        totalTracks = 0
        for singer in singersList:
            if singer['singer_url'] in seenDB:
                print('... Singer %s is already crawled... program continue...' % singer['singer'])
                continue
            albumCrawl = []
            almumCnt = 0
            trackCnt = 0
            crawlCnt += 1
            albumList = []
            hd2Url = parse_tag_hd2(singer['singer_url'])
            try:
                hb2aUrl = parse_tag_hb2a(hd2Url)
                parse_albums_list(hb2aUrl)
                (albumsList, singerIntro) = parse_albums_list(hb2aUrl)
                for album in albumsList:
                    almumCnt += 1
                    (tagAList, releasedDate, albumIntro) = parse_tagA_list(rootUrl + album.get('href'))
                    (trackList, trackCnt) = extract_track_list(tagAList, trackCnt)
                    albumInfo = extract_album_list(trackList, album.get_text(), releasedDate, albumIntro)
                    albumList.append(albumInfo)
            except:
                continue
            
            singer['singer_intro'] = singerIntro

            singer['albums'] = albumList
            # print(json.dumps(singer, indent=4, ensure_ascii=False))
            albumCrawl.append(singer)
        
            totalAlbums += almumCnt
            totalTracks += trackCnt
                
                
            print('[%d] singer: %s ....... albums: %d ....... tracks: %d' % (crawlCnt,singer['singer'], almumCnt, trackCnt))
            print('totalAlbums: %d,  totalTrack: %d \n'% (totalAlbums, totalTracks))
        
            # print(json.dumps(albumCrawl, indent = 4, ensure_ascii = False))
            with open('all_singers_album.json', 'a') as fs:
                fs.write(json.dumps(albumCrawl, ensure_ascii = False))
                fs.write('\n')
            
            with open(seenDbPath, 'a') as fptr:
                fptr.write('%s\n' % singer['singer_url'])


                
        fp.close()
    except:
        print('error on line 185.')
        real_main()


if __name__ == '__main__':
    real_main()