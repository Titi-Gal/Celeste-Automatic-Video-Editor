Celeste Automatic Video Editor:

Identifies the blackscreen transitiosn associated with deaths and ends in the game.
Creates video sections with speed changes of the last moments berofe the deaths and join then togheter.
You can opt to have the last try in real time and/or complete.

Usability:

1. pré-cut your video
    I tested with videos cutted from the initial blackscreen in the beguinning of a level to the final blackscreen of the same level, it problably will work beyond these points
    Put all cutted videos in the same folder

2 Ajust variables if you want to
    As it is you can change the variables in lines 26-44
    Crop and Blackdetect are used to detect transitions, if you are having trouble with transitions you can ajust these
    I will shortly program all to be set in cmd line

3. Run the program with python celeste_deaths_automatic_video_editor.py and enter path for "directory with videos to edit: " when asked

4. Dependencies
    ffmpeg on path, if you don't know to do this just search for install ffmpeg
    better with python on path, if you don't have python you just have to install it and read the options carefully

5. References
    information on ffmpeg parameters: https://ffmpeg.org/ffmpeg-all.html
    looked at this for speed change: https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
    took some inspiration from carykh jumpcutter https://github.com/carykh/jumpcutter
    used these to ajust the filer to detect celeste transitions https://www.youtube.com/watch?v=qW4ErQXyWtI