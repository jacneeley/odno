import os

import spotipy

def auth_user() -> spotipy.Spotify:
    # path = os.path.abspath("some/path")
    creds = spotipy.CLIENT_CREDS_ENV_VARS
    creds["client_id"] = "7e0d5b6081474ed2b6e6fa8b6910add4"
    creds["client_secret"] = "5dd58b09f89f4821a03d001adfc23618"
    return spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        requests_session=True
    ))

if __name__ == "__main__":
    print("testing connection with supplied client_id & client_secret...")
    
    test = auth_user().search(
        q="daydream+nation+sonic+youth",
        limit=1,
        offset=0,
        type="album",
        market="US"
    )

    print(test)