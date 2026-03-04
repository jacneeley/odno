import datetime
import subprocess

def convert_date_str(date_time:str):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''

    return datetime.datetime.strptime(date_time, "%Y-%m-%d")

def sort_tracks(track_list:list[str]) -> None:
    n = len(track_list)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            curr = int(track_list[j].split(".")[0].replace("track",""))
            next = int(track_list[j + 1].split(".")[0].replace("track",""))
            if curr > next:
                track_list[j], track_list[j + 1] = track_list[j + 1].strip() , track_list[j].strip()
                swapped = True
        if not swapped:
            break

def get_bit_rate() -> int:
    print("Select an mp3 bit rate:")
    print("Smaller bit rate = less fidelity but smaller file size.\n192kb is recommended")
    print("1. 64\n2. `128\n,3. 192\n,4. 256\n5. 320")
    
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
    
def remove_wavs(path:str) -> None:
    rm_wav = input("remove duplicate .wavs?\nthis will remove WAVs in the tmp 'album' folder only. Original WAVs from will be preserved.\nremove(y/n)? ")
    if rm_wav == "y":
        subprocess.call(f"rm {path}/*.wav" , shell=True)
        # subprocess.call("rm *.mp3", shell=debug)