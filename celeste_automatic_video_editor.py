import os, sys, subprocess, argparse

def main():

    #Arguments parsing, help, usage
    parser = argparse.ArgumentParser(description="""identifies the blackscreen transitiosn associated with deaths, beginnings and ends in the game.
creates video sections with speed changes of the last moments berofe transitions and join then togheter.
you can opt to have the last try/section in real time and/or complete.""", epilog="Mess with crop and blacdetect if you're having trouble with detecting transitions. blackdetect is used in the cropped video")
    parser.add_argument('path_with_videos', type=str, help="path with videos to edit")
    parser.add_argument('--last_try_complete', type=bool, default=False, help="pass true if you want the last try complete", metavar="")
    parser.add_argument('--last_try_normal_speed', type=bool, default=False, help="", metavar="pass true if you want last try in normal speed")
    parser.add_argument('--long_scroll_screen', type=bool, default=False, help="intended for long scroll screen like last fro 8C or last from Moon, it will edit tries from short to long", metavar="")
    parser.add_argument('--secs_before_cut', type=float, default=5, help="hou much video to keep before each cut, this is before speed change", metavar="")
    parser.add_argument('--speed_change', type=float, default=2, help="by how much to change the speed. 1 is no change, can't be 0 and to hight will affect video/audio quality", metavar="")
    parser.add_argument('--crop_size', type=int, nargs=2, default=[300,300], help="rectangular area to cut in pixels", metavar="")
    parser.add_argument('--crop_center', type=int, nargs=2, default=['(iw/2)','(ih/2)'], help="center of the rectangular area", metavar="")
    parser.add_argument('--blackdetect_duration', type=float, default=0.15, help="min duration for a screen to be considered black", metavar="")
    parser.add_argument('--blackdetect_pix_th', type=float, default=0.02, help="pixel threshold: max luminescence for a pixel to be considered black", metavar="")
    parser.add_argument('--blackdetect_pic_th', type=float, default=1, help="picture threshold: percentage of the screen that has to be <= pix_th to be considered black", metavar="")
    args = parser.parse_args()
    
    main_dir = args.path_with_videos # Path with videos
    # Options
    secs_before_cut = args.secs_before_cut
    speed_change = args.speed_change
    last_try_complete = args.last_try_complete
    last_try_normal_speed = args.last_try_normal_speed
    long_scroll_screen = args.long_scroll_screen
    # Crop variables
    w = args.crop_size[0]
    h = args.crop_size[1]
    x = args.crop_center[0]
    y = args.crop_center[1]
    # Blackdetect variables
    duration = args.blackdetect_duration
    pix_th = args.blackdetect_pix_th
    pic_th = args.blackdetect_pic_th
    # List of video paths in main_dir supported by ffmpeg
    ffmpeg_capture_out = [line.strip() for line in ffmpeg_captureOut("ffmpeg -demuxers", capture="stdout")]
    ffmpeg_capture_out = ffmpeg_capture_out[ffmpeg_capture_out.index("--") + 1:]
    ffmpeg_supprted_video_formats = []
    for line in ffmpeg_capture_out:
        for format in line.split()[1].split(","):
            ffmpeg_supprted_video_formats.append(format) # List of ffmpeg supported input formats
    main_videos = only_supported_file_format_paths(main_dir, ffmpeg_supprted_video_formats)

    # The program will run for each supported video file in main directory, if no file is supported quits
    if main_videos == []:
        print("no supported video file formats in directory")
        sys.exit(1)

    for main_video in main_videos:
        
        # Variables
        main_video_format = main_video[main_video.rindex(".") + 1:]
        main_video_name = main_video[main_video.rindex(f"\\") + 1: main_video.rindex(".")]
        ready_video = f'{main_dir}\\{main_video_name}_ready.{main_video_format}'
        temp_dir = f'{main_dir}\\TEMP_FILES_CELESTE_DEATHS_AUTOMAIC_VIDEO_EDITOR'
        os.mkdir(temp_dir)
        #____________________________________________________________________________________
        # Build a list of sections of the video to cut by identifying blackscreen transitions
        print("detecting blackscreen transitions, this can take a while")

        # From ffmpeg stderrout only lines that contains "blackdetect"
        ffmpeg_command = f'ffmpeg -i "{main_video}" -vf crop={w}:{h}:{x}-{w/2}:{y}-{h/2},blackdetect=d={duration}:pix_th={pix_th}:pic_th={pic_th} -f null -'
        ffmpeg_capture_out = [line for line in ffmpeg_captureOut(ffmpeg_command) if "blackdetect" in line]

        # Format bkackdetect lines into dict
        ffmpeg_blackdetect = []
        for blackdetect in ffmpeg_capture_out:
            start_end = {"black_start": 0, "black_end": 0}
            for se in start_end:
                lstrip = blackdetect.index(se) + len(se) + 1
                digits = blackdetect[lstrip:].split()[0]
                start_end[se] = float(digits)
            ffmpeg_blackdetect.append(start_end)
        
        # Build a list with all places to cut, which are in the middle of blacks transitions
        places_to_cut = [blackdetect["black_start"] + ((blackdetect["black_end"] - blackdetect["black_start"]) / 2) for blackdetect in ffmpeg_blackdetect]
        # Build a list with sections of video to be cutted, with start and end places for each section
        sections_to_cut = [{"section_start": places_to_cut[i], "section_end": places_to_cut[i + 1]} for i in range(len(places_to_cut) - 1)]
        # If long scroll screen list is sorted to short video sections first
        if long_scroll_screen:
            sections_to_cut.sort(key=lambda x: x["section_end"] - x["section_start"])
        del places_to_cut

        # If no transition was detected quit
        if sections_to_cut == []:
            print("no transitions detected, check your video or try ajusting crop and blackdetect")
            sys.exit(1)

        #_____________________________________________
        # Create video section files eith speed change
        print(f"video sections detected: {len(sections_to_cut)}")

        for i, section in enumerate(sections_to_cut):
            print(f'creating video section {i + 1}:')

            start = section["section_end"] - secs_before_cut
            if start < 0:
                start = 0
            elif start < section["section_start"]:
                start = section["section_start"]
            end = section["section_end"]
            
            # Last section options: complete try/normal speed
            if i == len(sections_to_cut) - 1:
                if last_try_complete: # Starts from the beguining of section
                    start = section["section_start"]
                if last_try_normal_speed: # Change ffmpeg command to normal speed
                    speed_change = 1
            
            # Create ffmpeg command and execute it
            ffmpeg_command = f'ffmpeg -v 24 -stats  -ss {start} -to {end} -i "{main_video}" -vf "setpts={1/speed_change}*PTS" -filter:a "atempo={1*speed_change}" "{temp_dir}\\section{i:0>6}.{main_video_format}"'   
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