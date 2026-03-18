from cd_ripper.handle_metadata import save_album_metadata

def app() -> None:
    '''
        driver code for the application.
    '''
    saved = save_album_metadata(False)
    if not saved:
        print("Exiting.")
    else:
        print("Complete!")

if __name__ == "__main__":
    app()