from src.models import Song

def wow_niche() -> None:
    '''
        Inform the user the search could not find anything and restart.
    '''
    print("Wow, you are niche.\nThe album you are looking for could not be found on lastfm.\nTry refining your search.")


#####################
### unix commands ###
#####################
def save_metadata_ffmpeg(is_saved, og, parent_dir, song:Song, final_mp3_file) -> str:
    '''
        Build FFMPEG command for saving metadata to audio file.

        parameters:
            * is_saved -> bool to determine if an album cover image was saved
            * og -> str for the original file
            * parent_dir -> str for parent directory
            * song -> song object-model for the song (audio file) that ffmpeg will apply metadata to
            * final_mp3_final -> str final name the audio file with metadata will be saved as.

        returns:
            ffmpeg cmd as string

    '''

    if is_saved:
        return f'ffmpeg -i {og} -i {parent_dir}/cover.jpg -map 0 -map 1 -c copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -metadata:s:v title="{song.album} album cover" -metadata:s:v comment="{song.album} cover (front)" -disposition:v:1 attached_pic -codec copy {final_mp3_file} -hide_banner'.strip()

    return f'ffmpeg -i {og} -map_metadata -1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -codec copy {final_mp3_file} -hide_banner'.strip()

def convert_to_mp3_with_selected_bitrate(source_file:str, bit_rate:int, new_file:str) -> str:
    '''
        Use selected bit_rate from user input to convert original audio file to an mp3 with selected bit_rate.

        parameters:
            * source_file -> str path of the original audio file
            * bit_rate -> int selected bit rate
            * og_file -> path of the new mp3 file. 

        returns:
            FFMPEG cmd to convert audio file to mp3 with a target bit rate as string.
    '''

    return f'ffmpeg -i {source_file} -codec:a libmp3lame -b:a {bit_rate}k {new_file}'

def clean_up(og:str) -> str:
    '''
        clean up the temp directory by removing the mp3 copies. This will leave the new files with all the metadata alone.

        returns:
            unix rm commmand as string
    '''
    return f'{og}'

def copy_to_temp(source_file, dest_file) -> str:
    '''
        Copy original files to a temp directory for collecting metadata.
        FFMPEG cmds will be executed on files in this tmp directory.

        parameters:
            * source_file -> str source file
            * dest_file -> str destination path.

        returns:
            * unix cp command as string        
    '''

    return f"cp {source_file} {dest_file}"