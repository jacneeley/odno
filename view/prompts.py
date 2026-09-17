from core.odno_settings import sel_setting
from src.global_constants import __yes__

import core.utility as util

def wow_niche() -> None:
    '''
        Inform the user the search could not find anything and restart.
    '''
    print("Wow, you are niche.\nThe album you are looking for could not be found on lastfm.\nTry refining your search.")

def rm_wav_prompt():
    '''Ask user if they wish to delete wavs in the tmp directory.'''
    return util.clean_input_str("remove duplicate .wavs?\nthis will remove WAVs in the tmp 'album' folder only. Original WAVs from will be preserved.\nremove(y/n)? ", True)

def do_convert() -> bool:
    '''Prompt user to make a conversion decision'''
    print("Convert ripped .WAVs to .MP3?")
    q = util.clean_input_str("y/n? ", True)
    return True if q.lower() == __yes__() else False

def get_bit_rate() -> int:
    '''
        prompt user to make a bit rate selection.
    '''

    print("Select an mp3 bit rate:")
    print("Smaller bit rate = less fidelity but smaller file size.\n192kb is recommended")
    print("1. 64\n2. 128\n3. 192\n4. 256\n5. 320")

    selection = util.clean_input_int("make a selection: ")
    if selection == 1:
        return 64
    elif selection == 2:
        return 128
    elif selection == 3:
        return 192
    elif selection == 4:
        return 256
    elif selection == 5:
        return 320
    else:
        print("invalid selection.\nTry again.")
        return get_bit_rate()

def bad_file_names() -> str:
    '''Show error file names are bad.'''
    msg = "Error: Files in track list need to have a numeric order.\n\nRecommended file name format: <tracknum>_<filename>.<filetype>\nor\n<track><tracknum>.<filetype>\n\nexample:\n6_MyFriendGoo.mp3\nOR\ntrack1.wav"
    print(msg)
    return msg

def unexpected():
    '''Unexpected.'''
    msg = "An expected error has occurred..."
    print(msg)
    return msg

def retry_choice_prompt(failed:bool) -> None:
    '''Display Retry Choices'''
    if failed:
        print("Try the following:\n1.) Manual Search - Enter Album name and Artist Name and search\n2.) Manual Entry - Enter album metadata yourself; works offline.")
    else:
        print("\nTry the following:\n1.) Retry - Search again.\n2.) Manual Search - Enter Album name and Artist Name and search\n3.)Manual Entry - Enter album metadata yourself; works offline.")

def main_menu() -> None:
    '''Main Menu'''
    print("ODNO - An all-in-one tool for ripping CDs and collecting metadata.")
    print("\nMenu: \n\t1.) Help\n\t2.) Rip tracks from CD/DVD drive\n\t3.) Metadata Search\n\t4.) Settings\n")

def metadata_menu() -> None:
    '''Start Menu'''
    print("For best results, make sure album folders match the following: album_name-artist_name.\n\nUse ctrl-c to quit.\n")
    print("\nChoose a collection method:\n\t1.) Auto Web Search - Uses the folder name to search.\n\t2.) Manual Search - Provide a target folder and enter Artist namd & Album name.\n\t3.) Manual Entry - Enter metadata ; works offline")

def show_help() -> None:
    '''help'''
    desc = '''
        ODNO can be used to: 
            * rip CDs and collect metadata for audio files given that the correct album name & artist name is provided
            * convert .wav files to .mp3 files at various bit rates
            * download misssing album art for albums give the correct info is provided
    '''

    tips = '''
        Tips:
            * Make sure album name & artist name is accurate. Don't forget to include special characters -> [~`!@#$%^&*()_+[]\\;',./{}|:"<>?]
            * Use the following naming convention for your albums -> album_name-artist_name. Example /music/some_folder/goo-sonic_youth. Replace "/" with "\\" if on windows. 
    '''

    print(desc)
    print(tips)
    input("press any key to continue: ")

def show_settings() -> None:
    '''settings menu'''
    sel_setting()
