#!/bin/env python

from ytmusicapi import YTMusic
import json
import os
import subprocess

def downloader(ex_artist, ex_album, ex_url):
    print('ping!')
    print(f'/homepool/music/discographies/{ex_artist}/{ex_album}')
    if not os.path.exists(f'/homepool/music/discographies/{ex_artist}/{ex_album}'):
        os.makedirs(f'/homepool/music/discographies/{ex_artist}/{ex_album}')
    subprocess.call(f"/usr/local/bin/youtube-dl --default-search 'ytsearch' -i --yes-playlist --restrict-filenames -R 3 --add-metadata --extract-audio --audio-quality 0 --audio-format mp3 --prefer-ffmpeg --embed-thumbnail -f 'bestaudio' --download-archive /homepool/music/discographies/youtube_dl.archive -o '/homepool/music/discographies/{ex_artist}/{ex_album}/%(title)s - %(artist)s - %(album)s.%(ext)s' {ex_url}", shell=True)

yt = YTMusic('/etc/yt_music/headers_auth.json')
liked_songs = yt.get_liked_songs(10000000)
playlists = yt.get_library_playlists(1000000)
artist_array = []
liked_song_array = []
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
    print('\n\n----------------------------------------------------------------')
    print(artist_name)
    print('----------------------------------------------------------------')
#    if not artist_name == 'Girls Who Care':
#        continue
    exists = used_ids.count(artist_id)
    if exists > 0:
        print(f'{artist_name} has already been processed. Skipping...')
        dupe_ids.append([artist_name, artist_id])
        continue
    used_ids.append(artist_id)
    try:
        artist_cat_info = yt.get_artist(artist['id'])
        channel_id = artist_cat_info['channelId']
    except:
        print(f'{artist_name} has no music in channel. Skipping...')
        continue

    try:
        print('\n\nLooping through albums...')
        albums = artist_cat_info['albums']['results']
        for album in yt.get_artist(channel_id)['albums']['results']:
            album_id = album['browseId']
            album_title = album['title']
            album_playlist_id = yt.get_album(album_id)['audioPlaylistId']
            album_url = ''
            print(f'{album_title} : https://music.youtube.com/playlist?list={album_playlist_id}')
            downloader(artist_name, album_title, f'https://music.youtube.com/playlist?list={album_playlist_id}')
    except:
        print('No albums found')
    try:
        print('\n\nLooping through singles...')
        singles = yt.get_artist(channel_id)['singles']['results']
        for single in singles:
            single_title = single['title']
            single_browse_id = single['browseId']
            singles_list = yt.get_album(single_browse_id)
            single_playlist_id = singles_list['audioPlaylistId']
            print(f'{single_title} : https://music.youtube.com/playlist?list={single_playlist_id}')
            downloader(artist_name, 'Singles', f'https://music.youtube.com/playlist?list={album_playlist_id}')
    except:
        print('No singles found')
    
    try:
        print('\n\nLooping through individual songs...')
        ind_songs = artist_cat_info['songs']['results']
        for ind_song in ind_songs:
            song_details = yt.get_song(ind_song['videoId'])
            song_url = song_details['microformat']['microformatDataRenderer']['urlCanonical']
            song_title = song_details['videoDetails']['title']
            print(f'{song_title} : {song_url}')
            downloader(artist_name, 'Singles', song_url)
    except:
        print('No individual songs found')
#    print(json.dumps(artist_cat_info, indent=4))

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
