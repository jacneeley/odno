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

def search_for_cover(track_list:list[str]) -> None:
    '''
        BS search for cover.*.
        This is just to clean up the track_list if the selected album has been used before so that it ignores the cover img file.
    '''
    track_list.sort()
    target = "cover"
    low = 0
    hi = len(track_list) - 1

    while low <= hi:
        m = low + (hi - low) // 2

        file = track_list[m].lower().split(".")[0]

        if target == file:
            del track_list[m]
            break
        
        if file < target:
            low = m + 1

        else:
            hi = m - 1

def get_track_file_value(track:str) -> int:
        if "-" in track:
            return int(track.split("-")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))

        if "_" in track:
            return int(track.split("_")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))
        
        if "track" in track:
            return int(track.split(".")[0].replace("track",""))
        
        return int(track.split(".")[0])

def merge(track_list, l, m, r):
    n1 = m - l + 1
    n2 = r - m

    left = [0] * n1
    right = [0] * n2

    for i in range(n1):
        left[i] = track_list[l + i]
    
    for j in range(n2):
        right[j] = track_list[m + 1 + j]

    i = j = 0
    k = l

    while i < n1 and j < n2:
        if get_track_file_value(left[i]) <= get_track_file_value(right[j]):
            track_list[k] = left[i]
            i += 1
        
        else:
            track_list[k] = right[j]
            j += 1
        
        k += 1
    
    while i < n1:
        track_list[k] = left[i]
        i += 1
        k += 1
    
    while j < n2:
        track_list[k] = right[j]
        j += 1
        k += 1

def merge_sort(arr, l, r):
    '''
    classic merge sort algorithm for sorting file names in temp arr.
    This is done b/c listdr in os library randomly retrieves file names.
    time: O(n log n) ; space: O(n).
    ''' 
    if l < r:
        m = l + (r - l) // 2
        merge_sort(arr, l, m)
        merge_sort(arr, m + 1, r)
        merge(arr, l, m, r)

def sort_tracks(track_list:list[str]) -> None:
    '''
        Sort tracks from track_list arr using selection sort.
        time: O(n log n) ; space: O(n).
    '''
    try:
        #TODO: test merge sort
        start = datetime.datetime.second
        
        search_for_cover(track_list)
        merge_sort(track_list, 0, len(track_list) - 1 )
        
        end = datetime.datetime.second
        # print("time to sort in seconds:",end - start)

    except ValueError:
        prompts.bad_file_names()
        sys.exit()

    except IndexError:
        prompts.unexpected()
        sys.exit()


# def sort_tracks(track_list:list[str]) -> None:
#     '''
#         Sort tracks from track_list using bubble sort.

#         parameters:
#             * track_list -> list of tracks in album directory.
#     '''
#     l = len(track_list)
#     for i in range(l):
#         if "cover" in track_list[i]:
#             del track_list[i]
#             break

#     counter = 0
#     for i in track_list:
#         if i.split(".")[0].isalpha():
#             counter += 1
    
#     is_all_alpha = counter == len(track_list)
    
#     if is_all_alpha:
#         prompts.bad_file_names()
#         sys.exit()

#     else:
#         n = len(track_list)
#         for i in range(n):
#             swapped = False
#             for j in range(0, n - i - 1):
#                 curr = 0
#                 nxt = 0
#                 if "-" in track_list[j]:
#                     curr = int(track_list[j].split("-")[0]) if track_list[j][0].isnumeric() else int(track_list[j].split(".")[0].replace("track",""))
#                     nxt = int(track_list[j + 1].split("-")[0]) if track_list[j + 1][0].isnumeric() else int(track_list[j + 1].split(".")[0].replace("track",""))

#                 elif "_" in track_list[j]:
#                     curr = int(track_list[j].split("_")[0]) if track_list[j][0].isnumeric() else int(track_list[j].split(".")[0].replace("track",""))
#                     nxt = int(track_list[j + 1].split("_")[0]) if track_list[j + 1][0].isnumeric() else int(track_list[j + 1].split(".")[0].replace("track",""))
#                 else:
#                     if track_list[j].split(".")[0][-1].isnumeric() and track_list[j].split(".")[0][-1].isnumeric():
#                         curr = int(track_list[j].split(".")[0][-1])
#                         nxt = int(track_list[j + 1].split(".")[0][-1])
#                     else:
#                         curr = int(track_list[j].split(".")[0].replace("track",""))
#                         nxt = int(track_list[j + 1].split(".")[0].replace("track", ""))


#                 if curr > nxt:
#                     track_list[j], track_list[j + 1] = track_list[j + 1].strip() , track_list[j].strip()
#                     swapped = True
#             if not swapped:
#                 break
    
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