'''Module for utility functions.'''
import os
import sys
import datetime
import subprocess

from collections import deque

import view.prompts as prompts

from core.odno_logging import odnologger
from exceptions.odno_exceptions import OdnoException

MODULE_NAME = "utility"

def convert_date_str(date_time):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''
    try:
        if isinstance(date_time, str) and "-" in date_time and len(date_time) == 10 and len(date_time.split("-")[0]) == 2:
            return datetime.datetime.strptime(date_time, "%m-%d-%Y")

        if isinstance(date_time,int) and date_time < 10000:
            return datetime.datetime.strptime(str(date_time), "%Y")

        if "-" in date_time and len(date_time.split("-")) < 3:
            return datetime.datetime.strptime(date_time, "%Y-%m")

        if len(date_time) == 4:
            return datetime.datetime.strptime(date_time, "%Y")

        if "/" in date_time:
            return datetime.datetime.strptime(date_time, "%m/%d/%Y")

        return datetime.datetime.strptime(date_time, "%Y-%m-%d")
    except Exception as e:
        raise ValueError(f'date: {date_time} could not be parsed...') from e

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
        if isinstance(arr, deque):
            arr = list(arr)
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

    except IndexError as ie:
        odnologger.log(msg="bs_for_string() failed catastrophically...", e=ie, module_name='f{MODULE_NAME}.bs_for_string')


def get_track_file_value(track:str) -> int:
    '''
        Helper function to return the numeric value in the file name.

        parameters:
            * track -> str file name

        returns:
            * int value extracted from file name. 
    '''
    try:
        track = track.lower()
        if "-" in track:
            return int(track.split("-")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))

        if "_" in track:
            return int(track.split("_")[0]) if track[0].isnumeric() else int(track.split(".")[0].replace("track",""))

        if "track" in track:
            return int(track.split(".")[0].replace("track",""))

        return int(track.split(".")[0])
    
    except (TypeError,ValueError) as e:
        odnologger.log(
            log_level="ERROR",
            msg="get_track_file_value() - failed to convert value to int",
            e=e,
            module_name=f'{MODULE_NAME}.get_track_file_value')

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
        odnologger.log(
            log_level="ERROR",
            msg=prompts.bad_file_names(),
            e=ve,
            module_name=f'{MODULE_NAME}.sort_tracks')

        sys.exit()

    except (IndexError, TypeError) as ue:
        odnologger.log(
            log_level="ERROR",
            msg=prompts.unexpected,
            e=ue,
            module_name=f'{MODULE_NAME}.sort_tracks')

        sys.exit()

def sort_log_files_by_date(log_files:list[str]) -> None:
    try:
        merge_sort(log_files, 0, len(log_files))
    except:
        OdnoException.handle_exception("Unknown log error.", OdnoException("Error occurred managing log files."), "sort_log_files_by_date")

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
        odnologger.log(
            log_level="ERROR",
            msg=prompts.unexpected,
            e=ie,
            module_name=f'{MODULE_NAME}.remove_wavs')

        sys.exit()

def clean_input_str(msg:str, yn:bool = False) -> str:
    '''
        clean input func value

        parameters:
            * msg -> string value of input msg
        
        returns:
            * string
    '''
    if not yn:
        return input(msg).strip()

    val = input(msg).lower().strip()

    #TODO: figure out why this is not working.
    if len(val) != 1 or val == "":
        print("invalid. answers with 'y/n'")
        return clean_input_str(msg, yn)
    
    return val

def clean_input_int(msg:str) -> int:
    '''
    clean input func value

    parameters:
        * msg -> string value of the input msg
    
    returns:
        * int
    '''
    val = input(msg).strip()
    if not val:
        return 0

    if len(val) > 99:
        print("invalid. try again...")
        return clean_input_int(msg)

    return int(val)

def __sort_log_files(files, stack):
    f = stack.pop()
    if not files:
        files.append(f)
    elif f > files[-1]:
        files.append(f)
    else:
        # sort_log_files_by_date(files)
        # files.sort()
        loc = 0
        for i, j in enumerate(files):
            if j > f:
                loc = i
                break

        tmp:list = files[:loc]
        tmp.append(f)
        files = tmp + files[loc:]

    return files



def clean_up_logs():
    '''manage log directory'''
    log_dir = os.path.abspath("./.logs")
    size = 0

    log_files = os.listdir(log_dir)
    n = len(log_files) - 1
    stack = []
    files = []

    while n >= 0:
        while stack and convert_date_str(log_files[n].split(".log")[0]) > stack[-1]:
            files = __sort_log_files(files, stack)

        stack.append(convert_date_str(log_files[n].split(".log")[0]))
        n -= 1

        while n < 0 and stack:
            #clean up remaining
            files = __sort_log_files(files, stack)

    def __build_log_file(file:datetime.datetime):
        return f'{os.path.join(log_dir, file.strftime("%m-%d-%Y"))}.log'

    files = list(map(__build_log_file, files))

    size = sum(list(map(os.path.getsize, files))) / 1024
    if size > 1024:
        # delete files until size < 1024
        f_loc = 0
        while size >= 1024:
            size -= os.path.getsize(files[f_loc]) / 1024
            os.remove(files[f_loc])
            f_loc += 1
