#!/bin/env python

import ytmusicapi
#from ytmusicapi import YTMusic
import json
import os
import subprocess
import time

#yt = YTMusic('/etc/yt_music/oauth.json')
stuff = ytmusicapi.setup_oauth()
print(stuff)
#yt = YTMusic('/etc/yt_music/headers_auth.json', '104862870707763213449')
