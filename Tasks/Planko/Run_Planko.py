# Import some libraries from PsychoPy and others
import os
from pathlib import Path
from psychopy import core, event, visual,sound
from psychopy.visual import TextStim

# Winsize
winsize = (960, 540)

# create a window
win = visual.Window(size = winsize, fullscr=False, units="pix", pos =(0,30), screen=0)



TextStim(win, text="iSearch", color="white", height=60).draw()
win.flip()
core.wait(1.0)
win.flip()  # nothing drawn -> clears to background
win.close()
core.quit()
