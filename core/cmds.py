import subprocess

import core.prompts as prompts
from core.odnologging import odnologger

MODULE_NAME = "cmds"

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
    cpy_cmd = prompts.copy_to_temp(source_file, dest_file)

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
    convert = prompts.convert_to_mp3_with_selected_bitrate(source_file, bit_rate, og)

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
    ffmpeg_meta_cmd = prompts.save_metadata_ffmpeg(is_saved, og, parent_dir, song, final_file)

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
