#!/usr/bin/env python
import os
import subprocess
import fleep
import time
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(CURRENT_DIR, "snapull_out")

if not os.path.exists(os.path.join(SAVE_DIR, '.tmp')):
    os.makedirs(os.path.join(SAVE_DIR, '.tmp', ''))
if not os.path.exists(os.path.join(SAVE_DIR, 'Photos')):
    os.makedirs(os.path.join(SAVE_DIR, 'Photos'))
if not os.path.exists(os.path.join(SAVE_DIR, 'Videos')):
    os.makedirs(os.path.join(SAVE_DIR, 'Videos'))
saved_files = os.listdir(os.path.join(SAVE_DIR, 'Photos'))+os.listdir(os.path.join(SAVE_DIR, 'Videos'))
for index, value in enumerate(saved_files):
    saved_files[index] = value.split('.')[1]
file_list_command = subprocess.Popen(['adb shell su -c "ls -tr /data/data/com.snapchat.android/files/file_manager/chat_snap/"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
(out, err) = file_list_command.communicate()

videos = 0
photos = 0
ignored = 0

if err.decode('utf-8') == '':
    files_in_cache = out.decode('utf-8').split('\n')[:-1]
    for file in files_in_cache:
        if not file.split('.')[0] in saved_files:
            pulled_file_path = os.path.join(SAVE_DIR, '.tmp', file)
            #print('-> [A] Pulling remote file to : '+pulled_file_path)
            with open(pulled_file_path, "w+") as tmpfile:
                result = subprocess.Popen(['adb shell su -c "dd if=/data/data/com.snapchat.android/files/file_manager/chat_snap/{file}"'.format(file=file)], stdout=tmpfile, stderr=subprocess.DEVNULL, shell=True)
                result.wait()
            tmp_file_info = fleep.get(open(pulled_file_path, "rb").read(128))
            if tmp_file_info.type_matches("raster-image"):
                #print('--> [S] Detected image file')
                os.replace(pulled_file_path, os.path.join(SAVE_DIR, 'Photos', file+"."+tmp_file_info.extension[0]))
                photos = photos+1
            elif tmp_file_info.type_matches("video"):
                os.replace(pulled_file_path, os.path.join(SAVE_DIR, 'Videos', file+"."+tmp_file_info.extension[0]))
                videos = videos+1
            else:
                ignored = ignored+1

    print("##############--SUMMARY--################")
    print("Photos fetched: "+str(photos))
    print("Videos fetched: "+str(videos))
    print("__________________________________________")
    print("Total fetched : "+str(photos+videos) )
    print("Total Ignored : "+str(ignored))
else:
    print('----> [E] Uhh oh, Something went wrong')
    print(err.decode('utf-8'))
