#!/bin/env python

from ytmusicapi import YTMusic
import json

yt = YTMusic('/etc/yt_music/headers_auth.json')
liked_songs = yt.get_liked_songs(10000000)
playlists = yt.get_library_playlists(1000000)
artist_array = []
with open('/etc/yt_music/yt_sync.config') as f:
        playlist_name = f.readlines()[0].strip()

playlist_id = None
for playlist in playlists:
    if playlist_name == playlist['title']:
        playlist_id = playlist['playlistId']

if playlist_id == None:
    print(f'{playlist_name} not found')
    quit()

public_song_array = []
public_songs = yt.get_playlist(playlist_id, 100000000)
for public_song in public_songs['tracks']:
    artist_info = public_song['artists'][0]
    public_song_id = public_song['videoId']
    public_song_array.append(public_song_id)
    artist_array.append(artist_info)

used_ids = []
dupe_ids = []
for artist in artist_array:
    artist_id = artist['id']
    artist_name = artist['name']
    if not artist_name == 'Manu Chao':
        continue
    exists = used_ids.count(artist_id)
    if exists > 0:
        print(f'{artist_name} has already been processed. Skipping...')
        dupe_ids.append([artist_name, artist_id])
        continue
    used_ids.append(artist_id)
    print(artist_name)
#    channel_id = yt.get_artist(artist['id'])
#    print(channel_id)
    print(artist['id'])
    try:
        channel_id = yt.get_artist(artist['id'])['channelId']
    except:
        print(f'{artist_name} has no music in channel. Skipping...')
        continue
#    album_title = yt.get_artist(artist['id'])['albums']['results'][0]['title']
    try:
        albums = yt.get_artist(channel_id)['albums']['results']
    except:
        singles = yt.get_artist(channel_id)['singles']['results']
        for single in singles:
            single_title = single['title']
            single_browse_id = single['browseId']
            print(f'{single_title} : {single_browse_id}')
#   FIGURE OUT how to target individual songs in web browser instead of playlists,channels. /watch maybe a solution
        continue
#        print(f'{artist_name} has no albums. Skipping...')
#        continue
    for album in yt.get_artist(channel_id)['albums']['results']:
        album_id = album['browseId']
        album_title = album['title']
#        print(json.dumps(yt.get_album(album_id), indent=4))
#        quit
        album_playlist_id = yt.get_album(album_id)['audioPlaylistId']
        print(artist_name)
        print(album_title)
        print(album_playlist_id)
        print(channel_id)
        print('-----------------------------------------------------------')
        print(dupe_ids)
        print('-----------------------------------------------------------')
    quit

for liked_song in liked_songs['tracks']:
    liked_song_id = liked_song['videoId']
    liked_song_array.append(liked_song_id)

liked_song_array.sort()
public_song_array.sort()
extraneous_songs = list(set(liked_song_array) - set(public_song_array))
if not extraneous_songs:
    print(f'{playlist_name} and Liked Playlists are fully synced. Exiting')
    quit()
for extraneous_song_id in extraneous_songs:
    ex_song_title = (yt.get_song(extraneous_song_id)['videoDetails']['title'])
    yt.add_playlist_items(playlist_id, [extraneous_song_id])
    print(f'{ex_song_title}:{extraneous_song_id} added to {playlist_name}')
#yt.create_playlist("Test_Playlist", "Liked Song playlist duplicate", "PUBLIC", id_array, "")
