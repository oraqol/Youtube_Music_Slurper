#!/bin/env python

from ytmusicapi import YTMusic
import json
import os
import subprocess
import time
import glob
import eyed3
import sys

for filename in glob.iglob('/homepool/music/discographies/' + '**/*mp3', recursive=True):
#for filename in glob.iglob('/homepool/music/discographies/', recursive=True):
    path_array = filename.split('/')
    path_artist_name = path_array[4].strip()
    path_artist_album = path_array[5].strip()
#    if not path_artist_name == 'Thirty Seconds To Mars':
#        continue
#    print(f"**{path_artist_name}*****")
    mp3 = eyed3.load(filename)
#    print(mp3.tag.artist)
    id3_artist_name = mp3.tag.album_artist
#    if not path_artist_name == id3_artist_name:
    mp3.tag.album_artist = path_artist_name.encode('ascii', 'ignore').decode('ascii')
    mp3.tag.artist = path_artist_name.encode('ascii', 'ignore').decode('ascii')
    mp3.tag.album = path_artist_album.encode('ascii', 'ignore').decode('ascii')
    mp3.tag.save()
    print(filename)
    print(f"Path Artist:{path_artist_name}|ID3 Artist:{id3_artist_name}|Album:{path_artist_album}\n\n\n\n")
#        time.sleep(30)

