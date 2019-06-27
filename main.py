import re
import requests
import bs4
from fuzzywuzzy import fuzz, process
from bs4 import BeautifulSoup
from gmusicapi import Mobileclient
from pprint import pprint
from unidecode import unidecode


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
            songs.append(unidecode(child.get_text()))
    return songs


def print_playlist(playlist):
    for track in playlist['tracks']:
        title = unidecode(track['track']['title'])
        artist = unidecode(track['track']['artist'])
        album = unidecode(track['track']['album'])
        print('{} - {} ({})'.format(title, artist, album))


def update_edge_playlist(api):
    edge_playlist = get_edge_playlist()
    print('Edge playlist:')
    pprint(edge_playlist)
    song_ids = []
    for song in edge_playlist:
        results = search_song(api, song)
        if len(results) > 0:
            best_ratio = 0
            match_index = 0
            for index, result in enumerate(results):
                result_song = '{} - {}'.format(unidecode(result['track']['artist']), unidecode(result['track']['title']))
                match_ratio = fuzz.ratio(song.lower(), result_song.lower())
                if match_ratio > best_ratio:
                    best_ratio = match_ratio
                    match_index = index
            song_ids.append(results[match_index]['track']['storeId'])
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
