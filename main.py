from repo.get_metadata import save_album_metadata

def app() -> None:
    save_album_metadata(False)

if __name__ == "__main__":
    app()