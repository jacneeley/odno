from core.prompts import menu
from src.handle_metadata import do_process

def ui_driver() -> bool:
    menu()
    sel = int(input("Menu selection: "))
    return do_process(sel)
