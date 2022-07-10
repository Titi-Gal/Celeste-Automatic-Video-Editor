Celeste Automatic Video Editor:

Identifies the blackscreen transitiosn associated with deaths beginnings and endings in the game Celeste.
Creates video sections with speed change of the last moments berofe the transitions.
You can opt to have the last try in real time and/or complete.

Usage Exemples:
    python celeste_automatic_video_editor.py "path_with_videos"
    python celeste_automatic_video_editor.py "path_with_videos" --long_scroll_screen --last_try_normal_speed --last_try_complete
    python celeste_automatic_video_editor.py "path_with_videos" --speed_change  2.5 secs_before_cut 8
    python celeste_automatic_video_editor.py "path_with_videos" --debug_crop_black_screen
    python celeste_automatic_video_editor.py "path_with_videos" --crop_size 300 200 --crop_center 700 400
    python celeste_automatic_video_editor.py "path_with_videos" --blackdetect_duration 0.1 --blackdetect_pix_th 0.03 --blackdetect_pix_th 0.98
    python celeste_automatic_video_editor.py --help

    Only requiered argument is "path_with_videos", the others can be in any order and combination.
    Debug, Crop and Blackdetect arguments should be left alone unless you're having trouble detecting transitions

Dependencies:

ffmpeg on path, if you don't know to install it just search for install ffmpeg
python on path, if you don't know to install it download from official site and read install options carefully

References:

information on ffmpeg parameters: https://ffmpeg.org/ffmpeg-all.html
looked at this for speed change: https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
looked at this for black detect: https://blog.gdeltproject.org/using-ffmpegs-blackdetect-filter-to-identify-commercial-blocks/
took some inspiration from carykh jumpcutter https://github.com/carykh/jumpcutter
used this to ajust the filter to detect celeste transitions https://www.youtube.com/watch?v=qW4ErQXyWtI