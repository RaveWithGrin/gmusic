import re
import requests
import bs4
from bs4 import BeautifulSoup
from gmusicapi import Mobileclient
from pprint import pprint


def clear_playlist(api, playlist):
    track_ids = []
    for track in playlist['tracks']:
        track_ids.append(track['id'])
    if(len(track_ids) > 0):
        api.remove_entries_from_playlist(track_ids)


def get_playlist(api, playlist_name):
    playlists = api.get_all_user_playlist_contents()
    for playlist in playlists:
        if (playlist['name'] == playlist_name):
            return playlist


def search_song(api, query):
    results = api.search(query)
    return results['song_hits']


def add_to_playlist(api, playlistId, songs):
    api.add_songs_to_playlist(playlistId, songs)


def get_edge_playlist():
    page = requests.get('https://edge.ca/edge-top-30/')
    soup = BeautifulSoup(page.content, 'html.parser')
    song_list = soup.find('ol')
    children = list(song_list.children)
    songs = []
    for child in children:
        if (type(child) is not bs4.element.NavigableString):
            songs.append(re.sub(u'\u2013', '-', child.get_text()))
    return songs


def print_playlist(playlist):
    for track in playlist['tracks']:
        title = re.sub(u'\u201d', '"', re.sub(
            u'\u201c', '"', track['track']['title']))
        artist = re.sub(u'\u201d', '"', re.sub(
            u'\u201c', '"', track['track']['artist']))
        album = re.sub(u'\u201d', '"', re.sub(
            u'\u201c', '"', track['track']['album']))
        print('{} - {} ({})'.format(title, artist, album))


def update_edge_playlist(api):
    edge_playlist = get_edge_playlist()
    print('Edge playlist:')
    pprint(edge_playlist)
    song_ids = []
    for song in edge_playlist:
        artist = song[:song.index(' - ')]
        title = song[song.index(' - ') + 3:]
        results = search_song(api, song)
        if len(results) > 0:
            match = 0
            for index, result in enumerate(results):
                if result['track']['artist'] == artist and result['track']['title'] == title:
                    match = index
                    break
            song_ids.append(results[match]['track']['storeId'])
    my_playlist = get_playlist(api, 'Edge Top 30')
    clear_playlist(api, my_playlist)
    add_to_playlist(api, my_playlist['id'], song_ids)
    new_playlist = get_playlist(api, 'Edge Top 30')
    print('New gmusic playlist:')
    print_playlist(new_playlist)


def login():
    api = Mobileclient()
    logged_in = api.oauth_login(Mobileclient.FROM_MAC_ADDRESS)

    if not logged_in:
        print('Unable to login, attemping oauth')
        api.perform_oauth()
        logged_in = api.oauth_login(Mobileclient.FROM_MAC_ADDRESS)

    if not logged_in:
        print('Unable to auth')
    else:
        print('Logged in')
        update_edge_playlist(api)


if __name__ == '__main__':
    login()
