import os
import sys
import datetime
import subprocess

import src.prompts as prompts

def convert_date_str(date_time:str):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''
    if "-" in date_time and len(date_time.split("-")) < 3:
        return datetime.datetime.strptime(date_time, "%Y-%m")
    
    if len(date_time) == 4:
        return datetime.datetime.strptime(date_time, "%Y")

    return datetime.datetime.strptime(date_time, "%Y-%m-%d")

def sort_tracks(track_list:list[str]) -> None:
    '''
        Sort tracks from track_list using bubble sort.

        parameters:
            * track_list -> list of tracks in album directory.
    '''
    l = len(track_list)
    for i in range(l):
        if "cover" in track_list[i]:
            del track_list[i]
            break

    counter = 0
    for i in track_list:
        if i.split(".")[0].isalpha():
            counter += 1
    
    is_all_alpha = counter == len(track_list)
    
    if is_all_alpha:
        prompts.bad_file_names()
        sys.exit()

    else:
        n = len(track_list)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                curr = 0
                nxt = 0
                if "-" in track_list[j]:
                    curr = int(track_list[j].split("-")[0]) if track_list[j][0].isnumeric() else int(track_list[j].split(".")[0].replace("track",""))
                    nxt = int(track_list[j + 1].split("-")[0]) if track_list[j + 1][0].isnumeric() else int(track_list[j + 1].split(".")[0].replace("track",""))

                elif "_" in track_list[j]:
                    curr = int(track_list[j].split("_")[0]) if track_list[j][0].isnumeric() else int(track_list[j].split(".")[0].replace("track",""))
                    nxt = int(track_list[j + 1].split("_")[0]) if track_list[j + 1][0].isnumeric() else int(track_list[j + 1].split(".")[0].replace("track",""))
                else:
                    if track_list[j].split(".")[0][-1].isnumeric() and track_list[j].split(".")[0][-1].isnumeric():
                        curr = int(track_list[j].split(".")[0][-1])
                        nxt = int(track_list[j + 1].split(".")[0][-1])
                    else:
                        curr = int(track_list[j].split(".")[0].replace("track",""))
                        nxt = int(track_list[j + 1].split(".")[0].replace("track", ""))


                if curr > nxt:
                    track_list[j], track_list[j + 1] = track_list[j + 1].strip() , track_list[j].strip()
                    swapped = True
            if not swapped:
                break
    
def remove_wavs(path:str) -> None:
    '''
        prompt the user if they wish to remove the original wav files from the rip.

        parameters:
            * path -> location of the wav files.
    '''

    items = os.listdir(path)
    if ".wav" in items:
        rm_wav = prompts.rm_wav_prompt()
        if rm_wav == "y":
            subprocess.call(f"rm {path}/*.wav" , shell=True)
            # subprocess.call("rm *.mp3", shell=debug)