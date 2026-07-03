from src.models import Song
from src.globalconstants import __yes__

def wow_niche() -> None:
    '''
        Inform the user the search could not find anything and restart.
    '''
    print("Wow, you are niche.\nThe album you are looking for could not be found on lastfm.\nTry refining your search.")

def rm_wav_prompt():
    '''Ask user if they wish to delete wavs in the tmp directory.'''
    return input("remove duplicate .wavs?\nthis will remove WAVs in the tmp 'album' folder only. Original WAVs from will be preserved.\nremove(y/n)? ")

def do_convert() -> bool:
    '''Prompt user to make a conversion decision'''
    print("Convert ripped .WAVs to .MP3?")
    q = input("y/n? ")
    return True if q.lower() == __yes__() else False

def get_bit_rate() -> int:
    '''
        prompt user to make a bit rate selection.
    '''

    print("Select an mp3 bit rate:")
    print("Smaller bit rate = less fidelity but smaller file size.\n192kb is recommended")
    print("1. 64\n2. 128\n3. 192\n4. 256\n5. 320")
    
    selection = int(input("make a selection: "))
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

def menu() -> int:
    '''Start Menu'''
    print("ODNO - An all-in-one tool for ripping CDs and collecting metadata.")
    print("For best results, make sure album folders match the following: album_name-artist_name.\n\nUse ctrl-c to quit.\n")
    print("\nMenu:\n\t1.) Help\n\t2.) Auto Web Search - Uses the folder name to search.\n\t3.) Manual Search - Provide a target folder and enter Artist namd & Album name.\n\t4.) Manual Entry - Enter metadata ; works offline")

#####################
### unix commands ###
#####################
def save_metadata_ffmpeg(is_saved:str, og:str, parent_dir:str, song:Song, final_file:str) -> str:
    '''Build ffmpeg cmd string using provided parameters.'''
    if is_saved and ".wav" not in final_file:
        return f'ffmpeg -i {og} -i {parent_dir}/cover.jpg -map 0 -map 1 -c copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -metadata:s:v title="{song.album} album cover" -metadata:s:v comment="{song.album} cover (front)" -disposition:v:1 attached_pic -codec copy {final_file} -hide_banner'.strip()

    if ".wav" not in final_file:
        return f'ffmpeg -i {og} -map_metadata -1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -codec copy {final_file} -hide_banner'.strip()

    return f'ffmpeg -i {og} -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -codec copy {final_file} -hide_banner'.strip()

def convert_to_mp3_with_selected_bitrate(source_file:str, bit_rate:int, new_file:str) -> str:
    '''Build ffmpeg cmd string using provided parameters.'''
    return f'ffmpeg -i {source_file} -codec:a libmp3lame -b:a {bit_rate}k {new_file}'

def copy_to_temp(source_file, dest_file) -> str:
    '''Build copy cmd string using provided parameters.'''
    return f"cp {source_file} {dest_file}"