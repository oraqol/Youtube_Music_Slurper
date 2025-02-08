#!/bin/env python

from ytmusicapi import YTMusic
import json
import os
import subprocess
import time

yt = YTMusic('/etc/yt_music/oauth.json')
#yt = YTMusic('/etc/yt_music/headers_auth.json', '104862870707763213449')
liked_songs = yt.get_liked_songs()
playlists = yt.get_library_playlists()
liked_song_array = []

with open('/etc/yt_music/yt_sync.config') as f:
        playlist_name = f.readlines()[0].strip()

playlist_id = None
for playlist in playlists:
    if playlist_name == playlist['title']:
        playlist_id = playlist['playlistId']

if playlist_id == None:
    print(f'{playlist_name} not found')

public_song_array = []

public_songs = yt.get_playlist(playlist_id, 100000000)
for public_song in public_songs['tracks']:
    artist_info = public_song['artists'][0]
    public_song_id = public_song['videoId']
    public_song_array.append(public_song_id)

for liked_song in liked_songs['tracks']:
    liked_song_id = liked_song['videoId']
    liked_song_array.append(liked_song_id)

liked_song_array.sort()
public_song_array.sort()
extraneous_songs = list(set(liked_song_array) - set(public_song_array))

if not extraneous_songs:
    print(f'{playlist_name} and Liked Playlists are fully synced. Exiting')
    quit()
else:
    for extraneous_song_id in extraneous_songs:
        ex_song_title = (yt.get_song(extraneous_song_id)['videoDetails']['title'])
        yt.add_playlist_items(playlist_id, [extraneous_song_id])
        print(f'{ex_song_title}:{extraneous_song_id} added to {playlist_name}')
#yt.create_playlist("Test_Playlist", "Liked Song playlist duplicate", "PUBLIC", id_array, "")
