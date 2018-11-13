import requests
import time
import json
import langid
import csv

electric_pid = 1998546358
light_pid = 62693867
ost_pid = 62707941
minorities_pid = 2074063402

session = requests.Session()

server = 'http://localhost:3000'


def get_request(url, output=False):
    print(url)
    response = None
    for i in range(10):
        response_body = session.get(server + url, cookies={
            'MUSIC_U': '0852af0764f51dc163f1531f15776f2fadf8366ff5c52c8cfe8d489c2402ec33e690246df7727558f2e0559997dd8fe7d43ce951a9680d52d4bacc78a7ed476d',
            '__csrf': '55067ff9c9445fe8fb5f796e97ff5285',
            '__remember_me': 'true',
            'appver': '1.5.9',
            'channel': 'netease',
            'os': 'osx',
            'osver': '%E7%89%88%E6%9C%AC%2010.13.2%EF%BC%88%E7%89%88%E5%8F%B7%2017C88%EF%BC%89'
        })
        try:
            response = response_body.json()
            break
        except ValueError:
            pass
    if not response:
        raise ValueError()
    if output:
        print(json.dumps(response, indent=2, separators=(',', ': '), ensure_ascii=False))
        print(session.cookies)
    return response


def login(output=False):
    url = '/login/cellphone?phone=13522308461&password=c1h2h1k1&timestamp=' + str(time.time())
    get_request(url, output)


def playlist_list(output=False):
    url = '/user/playlist?uid=' + str(61393491)
    get_request(url, output)


def playlist_detail(pid, output=False):
    url = '/playlist/detail?id=' + str(pid)
    get_request(url, output)


def add_track_to_playlist(pid, tid, output=False):
    url = '/playlist/tracks?op=add&pid=' + str(pid) + '&tracks=' + str(tid)
    get_request(url, output)


def del_track_from_playlist(pid, tid, output=False):
    url = '/playlist/tracks?op=del&pid=' + str(pid) + '&tracks=' + str(tid)
    get_request(url, output)


def get_playlist_tracks(pid, output=False):
    url = '/playlist/detail?id=' + str(pid)
    return get_request(url, output)['result']['tracks']


def track_detail(tid, output=False):
    url = '/song/detail?ids=' + str(tid)
    get_request(url, output)


def get_lyric(tid, output=False):
    url = '/lyric?id=' + str(tid)
    lyric_body = get_request(url, output)
    if 'nolyric' in lyric_body and lyric_body['nolyric']:
        lyric = None
    elif 'uncollected' in lyric_body and lyric_body['uncollected']:
        lyric = None
    else:
        lyric = lyric_body['lrc']['lyric'].split('\n')
    return lyric


def get_lang(tid, output=False):
    lyric = get_lyric(tid, output)
    if not lyric:
        return '', 0
    langs = [langid.classify(x)[0] for x in lyric]
    lang_dict = {}
    for lang in langs:
        if lang in lang_dict:
            lang_dict[lang] += 1
        else:
            lang_dict[lang] = 1
    lang = [(k, lang_dict[k]) for k in sorted(lang_dict, key=lang_dict.get, reverse=True)][0]
    return lang


def get_user_playlists():
    login()
    playlist_list(True)


def get_song_lang(pid):
    login(True)
    tracks = get_playlist_tracks(pid, True)
    minorities_in_ost = []
    to_add = []
    for track in tracks:
        try:
            print(str(track['id']).ljust(10) + '\t', end='')
            lang = get_lang(track['id'])
            print(str(lang[0]).ljust(4) + '\t', end='')
            print(track['name'])
            if lang[1] > 0:
                minorities_in_ost.append({'id': track['id'], 'name': track['name'], 'lang': lang[0]})
                if lang[0] != 'en':
                    to_add.append(track['id'])
        except ValueError:
            print()
            print('Cannot load song ' + track['id'])

    # for track_id in reversed(to_add):
    #     add_track_to_playlist(minorities_pid, track_id)

    with open('minorities.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, ['id', 'lang', 'name'])
        writer.writerows(minorities_in_ost)


def transfer_song_add(pid):
    with open('minorities.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, ['id', 'lang', 'name'])
        for row in reader:
            if row['lang'] != 'en':
                add_track_to_playlist(pid, int(row['id']), True)


def transfer_song_del(pid):
    with open('minorities.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, ['id', 'lang', 'name'])
        for row in reader:
            if row['lang'] != 'en':
                del_track_from_playlist(pid, int(row['id']), True)


def main():
    # get_song_lang(minorities_pid)
    # login(True)
    return
    # transfer_song_add(minorities_pid)


if __name__ == '__main__':
    main()
