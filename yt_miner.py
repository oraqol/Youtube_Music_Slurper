#!/bin/env python

from ytmusicapi import YTMusic
from random import randint
import os
import subprocess
import time
import sys
import touch

def downloader(ex_artist, ex_album, ex_url):
    print(f'/homepool/music/discographies/{ex_artist}/{ex_album}')
    if not os.path.exists(f'/homepool/music/discographies/{ex_artist}/{ex_album}'):
        os.makedirs(f'/homepool/music/discographies/{ex_artist}/{ex_album}')
    subprocess.call(f"/usr/local/bin/yt-dlp --default-search 'ytsearch' -i --yes-playlist --restrict-filenames -R 3 --add-metadata --extract-audio --audio-quality 0 --audio-format mp3 --prefer-ffmpeg --embed-thumbnail -f 'bestaudio' --download-archive /homepool/music/discographies/youtube_dl.archive -o '/homepool/music/discographies/{ex_artist}/{ex_album}/%(title)s - %(artist)s - %(album)s.%(ext)s' {ex_url}", shell=True)
#    time.sleep(randint(1,120))

def append_spent_artists(name_of_artist):
        list_of_spent_artists = open("/etc/yt_music/yt_sync.artist_log", "a")
        list_of_spent_artists.write(f"{name_of_artist}\n")
        list_of_spent_artists.close()

flag = sys.argv[1]
yt = YTMusic('/etc/yt_music/headers_auth.json', '104862870707763213449')
liked_songs = yt.get_liked_songs(10000000)
playlists = yt.get_library_playlists(100000)
artist_array = []
liked_song_array = []
spent_artists = []
touch.touch('/etc/yt_music/yt_sync.artist_log')

with open('/etc/yt_music/yt_sync.config') as f:
        playlist_name = f.readlines()[0].strip()

#if flag == '--full-scan':
#    if os.path.exists('/etc/yt_music/yt_sync.artist_log'):
#        os.remove('/etc/yt_music/yt_sync.artist_log')
if flag == '--light-scan':
    with open('/etc/yt_music/yt_sync.artist_log') as file:
        spent_artists = [line.rstrip() for line in file]

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
    artist_array.append(artist_info)


used_ids = []
dupe_ids = []
total_artists = len(artist_array)
counter = 0

for artist in artist_array:
    counter += 1
    artist_id = artist['id']
    artist_name = artist['name'].strip()
    if flag == '--refresh-artist-log':
        append_spent_artists(artist_name)
        continue
#    if not artist_name == 'Blue Öyster Cult':
#        continue
    elif flag == '--light-scan':
        if artist_name in spent_artists:
#        print(f'{artist_name} has already been processed. Skipping...')
            continue

    exists = used_ids.count(artist_id)

    if exists > 0:
        print(f'{artist_name} has already been processed. Skipping...')
        dupe_ids.append([artist_name, artist_id])
        append_spent_artists(artist_name)
        continue

    used_ids.append(artist_id)

    try:
        artist_cat_info = yt.get_artist(artist['id'])
        channel_id = artist_cat_info['channelId']
    except:
        print(f'{artist_name} has no music in channel. Skipping...')
        append_spent_artists(artist_name)
        continue

    try:
        print('\n\n----------------------------------------------------------------')
        print(f'{artist_name}  {counter}/{total_artists}')
        print('----------------------------------------------------------------')
        print('\n\nLooping through albums...')
        albums = artist_cat_info['albums']['results']
        for album in yt.get_artist(channel_id)['albums']['results']:
            album_id = album['browseId']
            album_title = album['title']
            album_playlist_id = yt.get_album(album_id)['audioPlaylistId']
            album_url = ''
            print(f'{album_title} {album_id}: https://music.youtube.com/playlist?list={album_playlist_id}')
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
    
    append_spent_artists(artist_name)

#yt.create_playlist("Test_Playlist", "Liked Song playlist duplicate", "PUBLIC", id_array, "")
