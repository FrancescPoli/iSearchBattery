# video_diag.py
from psychopy import prefs, logging

# 1) Hard reset prefs and force ONLY moviepy (so ffpyplayer/VLC/OpenCV are NOT probed)
prefs.resetPrefs()
prefs.general['movieLib'] = ['moviepy']
prefs.hardware['audioLib'] = ['pygame']   # avoid sound backends probing
logging.console.setLevel(logging.DEBUG)

# 2) Import AFTER prefs are set
from psychopy import visual, core
import os, imageio_ffmpeg

print("Using movieLib prefs:", prefs.general['movieLib'])
print("FFmpeg exe used by imageio-ffmpeg:", imageio_ffmpeg.get_ffmpeg_exe())

# 3) Make sure the file exists
path = r"C:\Users\itali\Documents\iSearchBattery\Tasks\Torchlight\Stimuli\Stimuli1\elephant\elephant0a.mp4"
print("Exists:", os.path.exists(path), path)

# 4) Play
win = visual.Window([640, 480], units='pix')
mov = visual.MovieStim(win, path, noAudio=True, movieLib='moviepy')
while mov.status != visual.FINISHED:
    mov.draw()
    win.flip()
win.close(); core.quit()
