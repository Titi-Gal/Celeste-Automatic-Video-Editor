import os, subprocess

def main():

    # Aks input for the directory with the videos
    while True:
        main_dir = input("directory with videos to edit: ")
        if os.path.exists(main_dir):
            break
        else:
            print("path does not exist")

    # Build a list of ffmpeg supported input formats
    ffmpeg_capture_out = [line.strip() for line in ffmpeg_captureOut("ffmpeg -demuxers", capture="stdout")]
    ffmpeg_capture_out = ffmpeg_capture_out[ffmpeg_capture_out.index("--") + 1:]
    ffmpeg_supprted_video_formats = []
    for line in ffmpeg_capture_out:
        for format in line.split()[1].split(","):
            ffmpeg_supprted_video_formats.append(format)
    # Build a list of videos_file_paths in videos_directory_path supported by ffmpeg
    main_videos = only_supported_file_format_paths(main_dir, ffmpeg_supprted_video_formats)

    """
    TODO Expose these variables to be user defined
    """
    # Options
    speed = 2 #1 is normal speed, can't be 0 and too high damage audio and video quality max 2 recomended
    secs_before_transition = 5
    long_scroll_screen = False # Indented for screens like last sections of Core-C or last section of Moon, organize sections from short do long
    normal_speed_last_try = True # As you wish
    complete_last_try = True # As you wish

    # Crop variables
    w = 300 #width of rectangle to detect blackscreen
    h = 300 #height of rectangle to detect blackscreen
    x = '(iw/2)' #x center of rectangle, defautl is center of video
    y = '(ih/2)' #y center of rectangle, defautl is center of video

    # Blackdetect variables
    d = 0.15 #minimal duration to mark decection
    pix_th = 0.02 #theshhold of luminescence to considerer pixel black
    pic_th = 1 # % of screen that has to be below pix_th to consider blackscreen

    # The program will run for each supported video file in main directory, if no file is supported does nothing
    if main_videos == []:
        print("no supported video file formats in directory")
        
    for main_video in main_videos:
        
        # Variables
        main_video_format = main_video[main_video.rindex(".") + 1:]
        main_video_name = main_video[main_video.rindex(f"\\") + 1: main_video.rindex(".")]
        temp_dir = f'{main_dir}\\TEMP_FILES_CELESTE_DEATHS_AUTOMAIC_VIDEO_EDITOR'
        os.mkdir(temp_dir) #TODO it will become a class temp_dir = temp_directory(temp_dir) and that add and delete files from this folder will change
        ready_video = f'{main_dir}\\{main_video_name}_ready.{main_video_format}'

        #____________________________________________________________________________________
        # Build a list of sections of the video to cut by identifying blackscreen transitions
        print("detecting blackscreen transitions, this can take a while")

        
        # From ffmpeg stderrout only lines that contains "blackdetect"
        ffmpeg_command = f'ffmpeg -i "{main_video}" -vf crop={w}:{h}:{x}-{w/2}:{y}-{h/2},blackdetect=d={d}:pix_th={pix_th}:pic_th={pic_th} -f null -'
        ffmpeg_capture_out = [line for line in ffmpeg_captureOut(ffmpeg_command) if "blackdetect" in line]

        # Massagens bkackdetect strings from lines and format values into dict
        ffmpeg_blackdetect = []
        for blackdetect in ffmpeg_capture_out:
            start_end = {"black_start": 0, "black_end": 0}
            for se in start_end:
                lstrip = blackdetect.index(se) + len(se) + 1
                digits = blackdetect[lstrip:].split()[0]
                start_end[se] = float(digits)
            ffmpeg_blackdetect.append(start_end)
        
        # Build a list with all seconds to cut, which are in the middle of blacks transitions
        places_to_cut = [blackdetect["black_start"] + ((blackdetect["black_end"] - blackdetect["black_start"]) / 2) for blackdetect in ffmpeg_blackdetect]

        # Build a list sections of video to be cutted, with start and end seconds
        sections_to_cut = [{"section_start": places_to_cut[i], "section_end": places_to_cut[i + 1]} for i in range(len(places_to_cut) - 1)]
        
        if long_scroll_screen: # Short video sections means deaths at the beguining of long scroll level sections, list is sorted to short video sections first
            sections_to_cut.sort(key=lambda x: x["section_end"] - x["section_start"])
        del places_to_cut

        #___________________________
        # Create video section files eith speed change
        print(f"video sections detected: {len(sections_to_cut)}")

        for i, section in enumerate(sections_to_cut):
            print(f'creating video section {i + 1}:')

            start = section["section_end"] - secs_before_transition
            if start < 0:
                start = 0
            elif start < section["section_start"]:
                start = section["section_start"]
            end = section["section_end"]
            
            # Last section options: complete try/normal speed
            if i == len(sections_to_cut) - 1:
                if complete_last_try: # Starts from the beguining of section
                    start = section["section_start"]
                if normal_speed_last_try: # Change ffmpeg command to don't speed up
                    speed = 1
            
            # Create ffmpeg command and execute it
            ffmpeg_command = f'ffmpeg -v 24 -stats  -ss {start} -to {end} -i "{main_video}" -vf "setpts={1/speed}*PTS" -filter:a "atempo={1*speed}" "{temp_dir}\\section{i:0>6}.{main_video_format}"'   
            ffmpeg_execute(ffmpeg_command)
        
        #___________________________
        # Concatenate video sections 
        print("concatenanting video sections:")

        # List with video section paths
        temp_videos = only_supported_file_format_paths(temp_dir, ffmpeg_supprted_video_formats)
        
        # Saves a txt with videos paths needed for ffmpeg command
        txt_to_concatenate = f'{temp_dir}\\to_concatenate.txt' 
        with open(txt_to_concatenate, 'w') as file:
            for temp_video in temp_videos:
                file.write(f"file '{temp_video}'\n")
        
        # Create ffmpeg command and execute it
        ffmpeg_command = f'ffmpeg -v 24 -stats -f concat -safe 0 -i {txt_to_concatenate} "{ready_video}"'
        ffmpeg_execute(ffmpeg_command)

        #_________________________________________
        # Delete temporary files and paths created
        temp_videos = only_supported_file_format_paths(temp_dir, ffmpeg_supprted_video_formats)
        for temp_video in temp_videos:
            os.remove(temp_video)
        os.remove(txt_to_concatenate)
        os.rmdir(temp_dir)

def ffmpeg_captureOut(command, capture="stderr"):
    """ Runs ffmpeg command and returns captured output as a list, ffmpeg can still output files"""
    ffmpeg_run = subprocess.run(command, shell=True, capture_output=True, text=True)
    strerr = ffmpeg_run.stderr.splitlines()
    stdout = ffmpeg_run.stdout.splitlines()
    assert ffmpeg_run.returncode == 0, f"something went wrong: ffmpeg returncode should be 0 but is {ffmpeg_run.returncode}"
    if capture == "stderr":
        return strerr
    if capture == "stdout":
        return stdout

def ffmpeg_execute(command):
    """ Runs ffmpeg command without capture output for speed"""
    ffmpeg_run = subprocess.run(command, shell=True)
    assert ffmpeg_run.returncode == 0, f"something went wrong: ffmpeg returncode should be 0 but is {ffmpeg_run.returncode}"
    return None    

def only_supported_file_format_paths(videos_directory_path, ffmpeg_supprted_formats):
    """ Returns a list of paths for video files supported by ffmpeg"""
    supported_videos_file_paths = []
    for direntry in os.scandir(videos_directory_path):
        if direntry.is_file():
            file_name = direntry.name
            file_format = file_name[file_name.rindex(".") + 1: ]
            if file_format in ffmpeg_supprted_formats:
                supported_videos_file_paths.append(f"{videos_directory_path}\\{file_name}")
    return sorted(supported_videos_file_paths)

if __name__ == "__main__":
    main()