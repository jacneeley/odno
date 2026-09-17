'''views'''
from core.rip import rip
from core.utility import clean_input_int
from src.handle_metadata import do_process
from view.prompts import metadata_menu, main_menu, show_help, show_settings

def ui_driver() -> bool:
    '''TUI'''
    try:
        main_menu()
        sel = clean_input_int("Menu Selection: ")
        if sel == 1:
            show_help()
            return ui_driver()
        if sel == 2:
            rip()
            return ui_driver()
        if sel == 3:
            metadata_selection()
        if sel == 4:
            show_settings()
            return ui_driver()
        if sel > 4:
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
