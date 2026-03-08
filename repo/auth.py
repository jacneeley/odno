import requests

import spotipy
import discogs_client

def auth_user() -> discogs_client.Client:
    d = discogs_client.Client("cdripper/0.1", user_token="IePlcbMaNoymidLnPHyiplctuYnaroffXRDKUWmB")
    return d

def get_album(query:str) -> dict:
    master_id = auth_user().search(query=query, type="release")[0].data['master_id']

    resp:requests.Response = requests.get(f"https://api.discogs.com/masters/{master_id}", timeout=20)
    return resp.json()

def auth_user_spotify() -> spotipy.Spotify:
    '''
        TODO: delete. Fuck you spotify.
    '''
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
    # test = auth_user().search("Daydream Nation by Sonic Youth", type="release")
    # results = test[0].data
    # print(results, results['master_id'])

    # r = auth_user().release(results['master_id'])
    print(get_album("daydream nation by sonic youth"))