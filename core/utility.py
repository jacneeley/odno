'''Module for utility functions.'''
import os
import sys
import datetime
import subprocess

import core.prompts as prompts
import core.odnologging as odnologging
import core.globalconstants as globalconstants

logger = odnologging.create_logger("utility.py")

def convert_date_str(date_time:str):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''
    if isinstance(date_time,int) and date_time < 10000:
        return datetime.datetime.strptime(str(date_time), "%Y")

    if "-" in date_time and len(date_time.split("-")) < 3:
        return datetime.datetime.strptime(date_time, "%Y-%m")

    if len(date_time) == 4:
        return datetime.datetime.strptime(date_time, "%Y")

    if "/" in date_time:
        return datetime.datetime.strptime(date_time, "%m/%d/%Y")

    return datetime.datetime.strptime(date_time, "%Y-%m-%d")

def bs_for_string(arr:list[str], target:str, ftype:bool, remove:bool) -> bool:
    '''
        BS search for target string.
        This search util can be used to quickly find if a string is present in a collection and/or remove that string when found.

        parameters:
            * arr -> list collection to search.
            * target -> str target string.
            * ftype -> bool is the target a name or a string representation of a file type.
            * remove -> bool remove the target once found.

        returns:
            * bool True if target is found else False.

    '''
    try:
        arr.sort()
        l, r = 0, len(arr) - 1

        while l <= r:
            m = l + (r - l) // 2
            curr = arr[m].lower().split(".")[-1] if ftype else arr[m].lower().split(".")[0]
            if target == curr:
                if remove:
                    del arr[m]

                return True

            if curr < target:
                l = m + 1

            else:
                r = m - 1

        return False

    except IndexError:
        if globalconstants.__debugflg__():
            logger.critical("bs_for_string() failed catastrophically...")


def get_track_file_value(track:str) -> int:
    '''
        Helper function to return the numeric value in the file name.

        parameters:
            * track -> str file name

        returns:
            * int value extracted from file name. 
    '''
    try:
        if "-" in track:
            return int(track.split("-")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))

        if "_" in track:
            return int(track.split("_")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))

        if "track" in track:
            return int(track.split(".")[0].replace("track",""))

        return int(track.split(".")[0])
    
    except TypeError:
        if globalconstants.__debugflg__():
            logger.critical("get_track_file_value() - failed to convert value to int")

def merge(track_list, l, m, r):
    '''
    Sort and merge after recursive merge_sort call.
    '''
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
        search_for_cover => time: O(n log n) ; space: O(n).
        merge_sort => time: O(n log n) ; space: O(n).
    '''
    try:
        bs_for_string(track_list, "cover", False, True)
        merge_sort(track_list, 0, len(track_list) - 1 )

    except ValueError as ve:
        prompts.bad_file_names()

        if globalconstants.__debugflg__():
            logger.exception(ve, ve.__traceback__)

        sys.exit()

    except (IndexError, TypeError) as ue:
        prompts.unexpected()

        if globalconstants.__debugflg__():
            logger.exception(ue, ue.__traceback__)

        sys.exit()

def remove_wavs(path:str) -> None:
    '''
        prompt the user if they wish to remove the original wav files from the rip.

        parameters:
            * path -> location of the wav files.
    '''
    try:
        items = os.listdir(path)

        wav_found = bs_for_string(items, "wav", True, False)

        if wav_found:
            rm_wav = prompts.rm_wav_prompt()
            if rm_wav == "y":
                subprocess.call(f"rm {path}/*.wav" , shell=True)

    except IndexError as ie:
        prompts.unexpected()

        if globalconstants.__debugflg__():
            logger.exception(ie, ie.__traceback__)

        sys.exit()