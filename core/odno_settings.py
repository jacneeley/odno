'''user settings for odno'''
import os
import sys
import string

from models.odno_cache import odno_cache

cache = odno_cache.get_cache()

def __list_drives() -> None:
    '''List Drives'''
    if sys.platform.startswith(('linux', 'darwin')):
        import pycdio
        import cdio

        drives = {}

        try:
            d = cdio.Device(driver_id=pycdio.DRIVER_UNKNOWN)
            drive_name = d.get_device()
            info = d.get_hwinfo()
            # cap_info = d.get_drive_cap()

            print("--- Listing Possible Drives (mounts) ---")

            opt_mounts = os.listdir('/dev')

            if "sr0" not in opt_mounts or "cdrom" not in opt_mounts:
                print("no optical drives found")
                input("press any key to continue: ")
                return

            i = 0
            for _,item in enumerate(opt_mounts):
                if item in drive_name:
                    i += 1
                    print(f"{i} - /{item} ({info[1].strip()} - {info[2].strip()})")
                    drives[i] = f"/dev/{item}"

            sel = int(input("select an optical drive: "))
            if 'disk' not in cache or cache['disk'] != drives[sel]:
                cache['disk'] = drives.get(sel, "None")

            print("\nDriver Availability...")
            seen = {}
            for dn in cdio.drivers.keys():
                driver_id = cdio.drivers[dn]
                if cdio.have_driver(dn) and not driver_id in seen:
                    print(f"\tDriver {dn} ({driver_id}) is installed.")
                    seen[driver_id] = True
                    if "linux" in dn.lower():
                        cache['driver'] = pycdio.DRIVER_LINUX
                        print(f"\nSetting default driver to {dn}\n")
                        break
            d.close()

        except (OSError) as e:
            raise IOError("failed to read Device") from e


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
    changed = False

    print("Settings Menu: (Enter \"-1\" to go back)\n\t1.) Select CDROM - this will become the default CDROM Odno searches for.\n\t2.) Update save location - this is where Odno will save converted tracks.") 

    sel = int(input("\nMake Selection: ")) if sel == 0 else sel
    if sel == -1:
        return True

    if sel == 1:
        __list_drives()
    elif sel == 2:
        curr = cache["MUSIC_PATH"]
        print(f"Current Directory: {curr}")
        save_location = input("\nEnter new save location (directory): ")

        if(save_location == "-1"):
            print("canceled\n")
            return True

        if (save_location == "" or save_location == " "):
            print("nothing to save...\n")
            return sel_setting()

        if not os.path.isdir(save_location):
            print("Not a valid directory!\nTry again...")
            return sel_setting(2)

        cache["MUSIC_PATH"] = save_location
        changed = True
    else:
        print("Not a valid selection. Try again.")
        return sel_setting()

    if changed:
        __update_prefs(cache)

    return sel_setting()

def __update_prefs(_cache = cache) -> None:
    if _cache:
        odno_cache.update_cache(_cache)