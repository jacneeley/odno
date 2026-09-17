import subprocess

from src.models import Song
from core.odno_logging import odnologger

MODULE_NAME = "cmds"

def save_metadata_ffmpeg(is_saved:str, og:str, parent_dir:str, song:Song, final_file:str) -> str:
    '''Build ffmpeg cmd string using provided parameters.'''
    if is_saved and ".wav" not in final_file:
        return f'ffmpeg -i {og} -i {parent_dir}/cover.jpg -map 0 -map 1 -c copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -metadata:s:v title="{song.album} album cover" -metadata:s:v comment="{song.album} cover (front)" -disposition:v:1 attached_pic -codec copy {final_file} -hide_banner'.strip()

    if ".wav" not in final_file:
        return f'ffmpeg -i {og} -map_metadata -1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -codec copy {final_file} -hide_banner'.strip()

    return f'ffmpeg -i {og} -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata genre="{song.genre}" -codec copy {final_file} -hide_banner'.strip()

def convert_to_mp3_with_selected_bitrate(source_file:str, bit_rate:int, new_file:str) -> str:
    '''Build ffmpeg cmd string using provided parameters.'''
    return f'ffmpeg -i {source_file} -codec:a libmp3lame -b:a {bit_rate}k {new_file}'

def copy_to_temp(source_file, dest_file) -> str:
    '''Build copy cmd string using provided parameters.'''
    return f"cp {source_file} {dest_file}"

def cp_cmd(source_file, dest_file) -> None:
    '''
        Copy original files to a temp directory for collecting metadata.
        FFMPEG cmds will be executed on files in this tmp directory.

        parameters:
            * source_file -> str source file
            * dest_file -> str destination path.

        returns:
            * unix cp command as string        
    '''
    cpy_cmd = copy_to_temp(source_file, dest_file)

    odnologger.log(log_level="INFO",msg=cpy_cmd, module_name=f'{MODULE_NAME}.cp_cmd')

    subprocess.run([cpy_cmd], shell=True, check=False)

def convert_cmd(source_file, bit_rate, og) -> None:
    '''
        Use selected bit_rate from user input to convert original audio file to an mp3 with selected bit_rate.

        parameters:
            * source_file -> str path of the original audio file
            * bit_rate -> int selected bit rate
            * og_file -> path of the new mp3 file. 

        returns:
            FFMPEG cmd to convert audio file to mp3 with a target bit rate as string.
    '''
    convert = convert_to_mp3_with_selected_bitrate(source_file, bit_rate, og)

    odnologger.log(log_level="INFO",msg=convert, module_name=f'{MODULE_NAME}.convert_cmd')

    subprocess.run([convert], shell=True, check = False)

def add_meta_data_ffmpeg_cmd(is_saved:bool, og:str, parent_dir:str, song, final_file:str) -> None:
    '''
        Build FFMPEG command for saving metadata to audio file.

        parameters:
            * is_saved -> bool to determine if an album cover image was saved
            * og -> str for the original file
            * parent_dir -> str for parent directory
            * song -> song object-model for the song (audio file) that ffmpeg will apply metadata to
            * final_final -> str final name the audio file with metadata will be saved as.

        returns:
            ffmpeg cmd as string

    '''
    ffmpeg_meta_cmd = save_metadata_ffmpeg(is_saved, og, parent_dir, song, final_file)

    odnologger.log(log_level="INFO",
                   msg=ffmpeg_meta_cmd, module_name=f'{MODULE_NAME}.add_meta_data_ffmpeg_cmd')

    if ".wav" in final_file and is_saved:
        #show this to user
        print("\nCover art was downloaded, but .wav files do not fully support cover art.\n")

    subprocess.run([ffmpeg_meta_cmd], shell=True, check = False)

def clean_up_cmd(og:str) -> None:
    '''
        clean up the temp directory by removing the mp3 copies. This will leave the new files with all the metadata alone.

        returns:
            unix rm commmand as string
    '''
    rm_cmd = f'rm {og}'

    odnologger.log(log_level="INFO",msg=rm_cmd, module_name=f'{MODULE_NAME}.clean_up_cmd')

    subprocess.run([rm_cmd], shell=True, check=False)

def install_dependencies() -> None:
    '''do project setup and install dependencies'''
    __install_libcdio()
    __install_ffmpeg()
    #TODO: create env

def __install_ffmpeg(pkg_mngr:str = "") -> None:
    '''install ffmpeg to system'''
    try:
        out: subprocess.CompletedProcess = None
        if "" == pkg_mngr:
            out = subprocess.run(["bash", "./scripts/bash/install_ffmpeg.sh"], check=True)
        else:
            out = subprocess.run(["bash", "./scripts/bash/install_ffmpeg.sh", pkg_mngr], check=True)
        out.check_returncode()
    except (subprocess.CalledProcessError) as e:
        print("install failed.")
        raise e

def __install_libcdio(pkg_mngr:str="") -> None:
    '''install libcdio dependencies to system'''
    try:
        out: subprocess.CompletedProcess = None
        if "" == pkg_mngr:
            out = subprocess.run(["bash", "./scripts/bash/install_libcdio.sh"], check=True)
        else:
            out = subprocess.run(["bash", "./scripts/bash/install_libcdio.sh", pkg_mngr], check=True)
        out.check_returncode()
    except (subprocess.CalledProcessError) as e:
        print("install failed.")
        raise e

