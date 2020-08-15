import json
import requests
from bs4 import BeautifulSoup

def extract_track_info(singerName, category, album, track, releasedDate, lyrics):
    rec = {
        'singer': singerName,
        'category': category,
        'album': album,
        'track': track,
        'released_date': releasedDate,
        'lyrics': lyrics
    }
    return rec


def extract_lyrics(trackUrl):
    resp = requests.get(trackUrl)
    soup = BeautifulSoup(resp.text, 'lxml')
    findId = soup.find(id = "fsZx3") #.split('<br>').get_text()
    zz = str(findId).split('<br/>')
    return (zz[1:-1])
     

def real_main():
    # try:
        seenDbPath = './lyrics_seenBD.json'
        try:
            with open(seenDbPath, 'r') as fs:
                seenDB = {}
                for l in fs:
                    backupInfo = json.loads(l)
                    seenDB[tuple(backupInfo)] = True
        except:
            seenDB = {}
            print('error on line 36.')
            return

        ### main cralwer

        fp = open('./all_singers_album.json', 'r')
        cnt = 0
        debugTemp = ''
        for line in fp:
            debugTemp = line
            allSingers = json.loads(line)
            for singer in allSingers:
                # if singer['category'] in ['華語男生', '華語女生', '華語團體']:
                if singer['category'] == '歐美':
                    # print(json.dumps(singer, indent = 4, ensure_ascii = False))
                    singerName = singer['singer']
                    category = singer['category']
                    albums = singer['albums']
                    for album in albums:    
                        if album['album'] == '暫存':
                            albumName = 'None'
                        else:
                            albumName = album['album']

                        releasedDate = album['released_date']
                        
                        for track in album['tracks']:
                            trackUrl = track['lyrics_url']
                            trackName = track['track']
                            if seenDB.get((singerName, trackName)):
                                print('... %s - %s is already crawled... program continue...' % (singerName, trackName))
                                continue
                            
                            lyrics = extract_lyrics(trackUrl)

                            rec = extract_track_info(singerName, category, albumName, trackName, releasedDate, lyrics)
                            # print(json.dumps(rec, indent = 4, ensure_ascii = False)) 
                            cnt += 1
                            seenDB[(singerName, trackName)] = True

                            with open('all_lyrics_info.json', 'a') as fs:
                                fs.write(json.dumps(rec, ensure_ascii = False))
                                fs.write('\n')
                            
                            with open(seenDbPath, 'a') as fptr:
                                fptr.write(json.dumps([singerName, trackName], ensure_ascii = False))
                                fptr.write('\n')

                            if cnt % 100 == 0:
                                print(cnt)

        fp.close()
    
    # except:
    #     print('error on line 86.')
    #     real_main()
    


if __name__ == '__main__':
    real_main()