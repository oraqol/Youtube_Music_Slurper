#!/bin/env python

from ytmusicapi import YTMusic
from random import randint
import os
import subprocess
import time
import sys
import touch
import eyed3
import glob

def downloader(ex_artist, ex_album, ex_url):
    path_artist_name = ex_artist.encode('ascii', 'ignore').decode('ascii')
    path_artist_album = ex_album.encode('ascii', 'ignore').decode('ascii')
    print(f'/homepool/music/discographies/{path_artist_name}/{path_artist_album}')
    filename = f'/homepool/music/discographies/{path_artist_name}/{path_artist_album}'
    if not os.path.exists(filename):
        os.makedirs(filename)
    subprocess.call(f"/usr/local/bin/yt-dlp --default-search 'ytsearch' -i --yes-playlist --restrict-filenames -R 3 --add-metadata --extract-audio --audio-quality 0 --audio-format mp3 --prefer-ffmpeg --embed-thumbnail -f 'bestaudio' --download-archive /homepool/music/discographies/youtube_dl.archive -o '/homepool/music/discographies/{path_artist_name}/{path_artist_album}/%(title)s - %(artist)s - %(album)s.%(ext)s' {ex_url}", shell=True)

def append_spent_artists(name_of_artist):
        list_of_spent_artists = open("/etc/yt_music/yt_sync.artist_log", "a")
        list_of_spent_artists.write(f"{name_of_artist}\n")
        list_of_spent_artists.close()

flag = sys.argv[1]
yt = YTMusic('/etc/yt_music/browser.json')
liked_songs = yt.get_liked_songs(10000000)
playlists = yt.get_library_playlists(100000)
artist_array = []
liked_song_array = []
spent_artists = []
touch.touch('/etc/yt_music/yt_sync.artist_log')

with open('/etc/yt_music/yt_sync.config') as f:
        playlist_name = f.readlines()[0].strip()

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
    if public_song['artists'] == None:
        #artist_info = 'Misc'
        next
    else:
        artist_info = public_song['artists'][0]
    public_song_id = public_song['videoId']
    public_song_array.append(public_song_id)
    artist_array.append(artist_info)

used_ids = []
dupe_ids = []
total_artists = len(artist_array)
counter = 0

for artist in artist_array:
    print(artist)
    counter += 1
    artist_id = artist['id']
    artist_name = artist['name'].strip()
    print('\n\n----------------------------------------------------------------')
    print(f'{artist_name}  {counter}/{total_artists}')
    print('----------------------------------------------------------------')
    if flag == '--refresh-artist-log':
        append_spent_artists(artist_name)
        continue
#    if artist_name in ['Tash Sultana', 'Mix n Blend', 'BOOTS']:
#        continue
#    if not artist_name == 'The Killers':
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

    #print(artist_cat_info)

    try:
        albums = yt.get_artist_albums(channel_id, artist_cat_info['albums']['params'])
    except:
        try:
            albums = artist_cat_info['albums']['results']
        except:
            print('No albums. Skipping...')

    try:
        singles = artist_cat_info['singles']['results']
    except:
        print('No singles. Skipping...')

    try:
        ind_songs = artist_cat_info['songs']['results']
    except:
        print('No individual songs. Skipping...')
    
    try:
        playlist_songs = artist_cat_info['playlists']['results']
    except:
        print('No individual songs. Skipping...')
#    if artist_name in ['Smooth McGroove']:
#        try:
#                video_songs = artist_cat_info['videos']['results']
#        except:
#            print('No videos. Skipping...')

    print('\n\nLooping through albums...')
    try:
        for album in albums:
            album_id = album['browseId']
            album_title = album['title']
            for tracks in yt.get_album(album_id)['tracks']:
                print(tracks)
                print("\n\n\n")
            album_playlist_id = yt.get_album(album_id)['audioPlaylistId']
            print(f'{album_title} {album_id}: https://music.youtube.com/playlist?list={album_playlist_id}')
            downloader(artist_name, album_title, f'https://music.youtube.com/playlist?list={album_playlist_id}')
    except:
        print('No albums found')

    try:
        print('\n\nLooping through singles...')
        for single in singles:
            single_title = single['title']
            single_browse_id = single['browseId']
            singles_list = yt.get_album(single_browse_id)
            single_playlist_id = singles_list['audioPlaylistId']
            print(f'{single_title} : https://music.youtube.com/playlist?list={single_playlist_id}')
            downloader(artist_name, 'Singles', f'https://music.youtube.com/playlist?list={single_playlist_id}')
    except:
        print('No singles found')

#    try:
#        print('\n\nLooping through playlists...')
#        for playlist_song in playlist_songs:
#            playlist_title = playlist_song['title']
#            playlist_browse_id = playlist_song['playlistId']
#            singles_list = yt.get_album(single_browse_id)
#            single_playlist_id = singles_list['audioPlaylistId']
#            print(f'{playlist_title} : https://music.youtube.com/playlist?list={playlist_browse_id}')
#            downloader(artist_name, 'Playlists', f'https://music.youtube.com/playlist?list={playlist_browse_id}')
#    except:
#        print('No playlists found')
#    try:
#        print('\n\nLooping through videos...')
#        for video in videos:
#            video_title = video['title']
#            video_browse_id = video['browseId']
#            video_list = yt.get_album(video_browse_id)
#            video_playlist_id = video_list['videoId']
#            video_details = yt.get_song(video_playlist_id)['microformat']['urlCanonical']
#            print(video_details)
#            print(f'{video_title} : https://music.youtube.com/playlist?list={single_playlist_id}')
#            downloader(artist_name, 'Singles', f'https://music.youtube.com/playlist?list={single_playlist_id}')
#    except:
#        print('No singles found')
#    try:
#        print('\n\nLooping through individual songs...')
            #        ind_songs = artist_cat_info['songs']['results']
#        for ind_song in ind_songs:
#            song_details = yt.get_song(ind_song['videoId'])
#            song_url = song_details['microformat']['microformatDataRenderer']['urlCanonical']
#            song_title = song_details['videoDetails']['title']
#            print(f'{song_title} : {song_url}')
#            downloader(artist_name, 'Singles', song_url)
#    except:
#        print('No individual songs found')
    
    append_spent_artists(artist_name)

for artist in artist_array:
    artist_name = artist['name'].strip()
    print(artist_name)
    for filename in glob.iglob(f'/homepool/music/discographies/{artist_name}/**/*mp3', recursive=True):
        path_array = filename.split('/')
        path_artist_name = path_array[4].strip().encode('ascii', 'ignore').decode('ascii')
        path_artist_album = path_array[5].strip().encode('ascii', 'ignore').decode('ascii')
        try:
            mp3 = eyed3.load(filename)
            id3_artist_name = mp3.tag.album_artist
            if (mp3.tag.album_artist != path_artist_name) or (mp3.tag.artist != path_artist_name) or (mp3.tag.album != path_artist_album):
                mp3.tag.album_artist = path_artist_name
                mp3.tag.artist = path_artist_name
                mp3.tag.album = path_artist_album
                mp3.tag.save()
                print(filename)
                print(f"Path Artist:{path_artist_name}|ID3 Artist:{id3_artist_name}|Album:{path_artist_album}")
                print(f"********{mp3.tag.album_artist}***********\n\n\n\n\n")
        except:
            print(f"Excption: Path Artist:{path_artist_name}|ID3 Artist:{id3_artist_name}|Album:{path_artist_album}")
            continue
