'''views'''
from core.prompts import menu
from src.handle_metadata import do_process

def ui_driver() -> bool:
    '''TUI'''
    try:
        menu()
        sel = int(input("Menu selection: "))
        if not do_process(sel):
            ui_driver()
    except ValueError:
        print("\nMake a selection using one of the menu choices.\nTry again...\n\n")
        ui_driver()

    return True
