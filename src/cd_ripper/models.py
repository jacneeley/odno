import datetime

class Song:
    '''
        Model-Object representing audio file in an album.
    '''
    def __init__(self, title:str, artist:str, album_artist:str, album:str, cd:int, genre:str, year:datetime, track_num:int, cover:str):
        self.title = title
        self.artist = artist
        self.album_artist = album_artist
        self.album = album
        self.cd = cd
        self.genre = genre
        self.year = year
        self.track_num = track_num
        self.cover = cover

    def __str__(self):
        return f"{self.title} : [artist={self.artist}, album={self.album}, genre={self.genre}, cd={self.cd}, year={self.year}, track_num={self.track_num}, album_cover={self.cover}]"
    
    def __repr__(self):
        return self.__str__()
