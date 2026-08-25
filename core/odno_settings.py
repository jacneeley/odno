'''user settings for odno'''
import os
import sys
import string

from core.load_pref import update_prefs
from core.odno_cache import odno_cache

def __list_drives() -> None:
    '''List Drives'''
    if sys.platform.startswith(('linux', 'darwin')):
        print("--- Listing Possible Drives (mounts) ---")

        root_content = os.listdir('/')

        for i,item in enumerate(root_content):
            if item not in ['proc', 'sys', 'dev', 'run']:
                print(f"{i+1} - /{item}")

    elif sys.platform.startswith('win'):
        #windows
        print("--- Listing Drives on Windows")

        drives = [f'{letter}:\\' for letter in string.ascii_uppercase]

        accessible_drives = [drive for drive in drives if os.path.exists(drive)]

        if accessible_drives:
            print("Drives found:")
            for i,drive in enumerate(accessible_drives):
                print(f"{i+1} -{drive}")
        else:
            print("None found...")
    else:
        print("You must be on freeBSD or something. Idk what to do about that...")
        sys.exit()


def sel_setting(sel: int = 0) -> bool:
    '''Setting Selection'''
    sel = int(input("\nMake Selection: ")) if sel == 0 else sel
    if sel == -1:
        return True
    elif sel == 1:
        __list_drives()
    elif sel == 2:
        curr = odno_cache["MUSIC_PATH"]
        print(f"Current Directory: {curr}")
        save_location = input("\nEnter new save location (directory): ")

        if (save_location == "-1" or save_location == "" or save_location == " "):
            return True

        if not os.path.isdir(save_location):
            print("Not a valid directory!\nTry again...")
            return sel_setting(2)

        odno_cache["MUSIC_PATH"] = save_location
    else:
        print("Not a valid selection. Try again.")
        return sel_setting()

    __update_prefs(odno_cache)

    return True

def __update_prefs(cache = None) -> None:
    if cache:
        update_prefs(cache)