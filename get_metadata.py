import datetime

from auth import auth_user
from song import Song



def check_album(album:dict) -> dict:
    '''
        Helper function to get album metadata from Spotify.search() and display album, artist, & release date.

        parameters:
            * album -> JSON object from Spotify.search()
    '''

    tmp = {
        "album" : "",
        "artist": "",
        "release_date": ""
    }

    tmp["album"] = album['albums']['items'][0]['name']
    tmp['artist'] = album['albums']['items'][0]['artists'][0]['name']
    tmp["release_date"] = album['albums']['items'][0]['release_date']

    print(
        "album:",   tmp['album']           +"\n",
        "artist:",  tmp['artist']          +"\n",
        "release:", tmp['release_date']    +"\n"
    )

    return tmp

def convert_date_str(date_time:str):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''

    return datetime.datetime.strptime(date_time, "%Y-%m-%d")

def get_album_from_spotify(album_name:str) -> list[Song]:
    '''
        search for an album using the spotify api and get the metadata for each track.

        returns a list of Songs -> list[Song]

        parameters:
            * album_name: name of the album used to search for.
    '''

    resp:dict = auth_user().search(
        q=album_name,
        limit=5,
        offset=0,
        type="album",
        market="US"
    )

    tracks:list[Song] = []

    album = check_album(resp)

    q:str = input("is the above correct (y/n)? ")
    if q.lower() == "y":
        album_id = resp['albums']['items'][0]['id']

        album_tracks = auth_user().album_tracks(
            album_id=album_id,
            market="US"
        )

        print("getting album metadata...\n")
 
        for t in album_tracks['items']:
            song = Song(
                t['name'],
                album['artist'],
                album['artist'],
                album['album'],
                int(t['disc_number']),
                convert_date_str(album['release_date']),
                int(t['track_number'])
            )

            tracks.append(song)
        
        return tracks

    else:
        print("done.")
        quit()

if __name__ == "__main__":
    query:str = "daydream+nation+sonic+youth"

    print("testing with", query.replace("+", " "))

    tracks:list[Song] = get_album_from_spotify(query)

    for t in tracks:
        print(t)