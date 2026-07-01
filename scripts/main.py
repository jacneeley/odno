'''Main'''
from src.handle_metadata import save_album_metadata

def app() -> None:
    '''
        driver code for the application.
    '''
    try:
        saved = save_album_metadata()
        if not saved:
            print("Exiting.")
        else:
            print("Complete!")
    except KeyboardInterrupt:
        print("\nQuit.")

if __name__ == "__main__":
    app()