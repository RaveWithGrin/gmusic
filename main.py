import re
import requests
import bs4
from bs4 import BeautifulSoup
from gmusicapi import Mobileclient
from pprint import pprint
from getpass import getpass


def clear_playlist(playlist):
    track_ids = []
    for track in playlist['tracks']:
        track_ids.append(track['id'])
    if(len(track_ids) > 0):
        api.remove_entries_from_playlist(track_ids)


def get_playlist(playlist_name):
    playlists = api.get_all_user_playlist_contents()
    for playlist in playlists:
        if (playlist['name'] == playlist_name):
            return playlist


def search_song(query):
    results = api.search(query)
    return results['song_hits']


def add_to_playlist(playlistId, songs):
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


creds = {}
creds['email'] = raw_input('Email: ')
creds['password'] = getpass()
api = Mobileclient()
logged_in = api.login(creds['email'], creds['password'],
                      Mobileclient.FROM_MAC_ADDRESS)

if logged_in:
    edge_playlist = get_edge_playlist()
    song_ids = []
    for song in edge_playlist:
        artist = song[:song.index(' - ')]
        title = song[song.index(' - ') + 3:]
        results = search_song(song)
        if len(results) > 0:
            match = 0
            for index, result in enumerate(results):
                if result['track']['artist'] == artist and result['track']['title'] == title:
                    match = index
                    break
            song_ids.append(results[match]['track']['storeId'])
    my_playlist = get_playlist('Edge Top 30')
    clear_playlist(my_playlist)
    add_to_playlist(my_playlist['id'], song_ids)
    my_playlist = get_playlist('Edge Top 30')
    pprint(my_playlist)
