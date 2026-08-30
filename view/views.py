'''views'''
from core.rip import rip
from view.prompts import metadata_menu, main_menu, show_help, show_settings
from exceptions.odno_exceptions import OdnoException
from src.handle_metadata import do_process

from core.utility import clean_input_int

def ui_driver() -> bool:
    '''TUI'''
    try:
        main_menu()
        sel = clean_input_int("Menu Selection: ")
        if sel == 1:
            show_help()
            return ui_driver()
        elif sel == 2:
            try:
                rip()
            except OdnoException as oe:
                OdnoException.handle_exception(oe, "Disk path could not be constructed, could not be found, or there was nothing on the disk.\nLikely cause: Disc drive could not be accessed.")
                return False
        elif sel == 3:
            metadata_selection()
        elif sel == 4:
            show_settings()
            return ui_driver()
        else:
            print("\ninvalid selection. try again...")
            return ui_driver()
    except ValueError:
        print("\ninvalid selection. try again...")
        return ui_driver()

    return True

def metadata_selection() -> bool:
    '''metadata selection TUI'''
    try:
        metadata_menu()
        _sel = clean_input_int("Selection: ")
        if not do_process(_sel):
            metadata_selection()
    except ValueError:
        print("\nMake a selection using one of the menu choices.\nTry again...\n\n")
        metadata_selection()

    return True
