# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 15:54:37 2020

@author: Hubert Voogd, based on Pillow (PIL) documentation
"""
from PIL import Image, ImageDraw, ImageEnhance  # ,ImageFilter
import math
from psychopy import visual, core, event, sound, gui, prefs  # ,  clock
# from random import shuffle, randint
import numpy as np
import tobii_research as tr
# import time
# import win32api
# import win32con
# import pywintypes
import os
import csv

useEyetracker = True  # TRUE WHEN AT THE LAB!

Path = r"C:\Users\itali\Documents\iSearchBattery\Tasks\Torchlight\\"
################## Initial set up for stimuli #################################

set_duration = 3.5  # inter stimulus interval (between cue and target)
set_test_duration = 10
threshold_reaching_time = 0.2  # seconds of continuous looking to correct location
trampoline_reaching_time = 0.150
fixation_torch = 0.5  # How long the torch appears for before subject has control on it
# in skewed condition, when infants look at target location the target is shown
# in uniform codnition, when infants look at correct trampoline location AND then at correct target location, target is shown
# specify darkness of each trial
dark = [1, 0.3, 0.2, 0.15, 0.12, 0.09, 0.06, 0.03, 0, 0, 0, 0]
dark = [0.3, 0.25, 0.2, 0.15, 0.12, 0.09, 0.06, 0.03, 0, 0, 0, 0]
trials = 12
test_trials = 4

Dlg = gui.Dlg(title="Torchlight")
Dlg.addField('Participant Number')
Dlg.addText('(Choose a number between 1 and 1000)')
selection = Dlg.show()  # show dialog and wait for OK or Cancel
if Dlg.OK:
    subjnum = float(selection["Participant Number"])
else:
    core.quit()

# specify target position for each trial (remove if statement if randomization by subject is not needed)
if subjnum % 2 == 1:  # if odd, skewed condition first
    target_pos = np.array([
        [1] * trials,  # in skewed: ALL in same location?
        [4] * trials,
        [2, 4, 3, 1, 3, 4, 2, 1, 4, 2, 3, 1],
        [3, 2, 4, 1, 2, 4, 3, 1, 3, 4, 2, 1]]) - 1
    skewed = [1, 1, 0, 0]
elif subjnum % 2 == 0:  # if even, uniform condition first
    target_pos = np.array([[2, 4, 3, 1, 3, 4, 2, 1, 4, 2, 3, 1],
                           [3, 2, 4, 1, 2, 4, 3, 1, 3, 4, 2, 1],
                           [1] * trials,
                           [4] * trials]) - 1
    skewed = [0, 0, 1, 1]

target_pos_pixels = [[[0, 450], [-100, 375]],
                     [[678 - 225, 678 + 225], [-100, 375]],
                     [[1242 - 225, 1242 + 225], [-100, 375]],
                     [[1920 - 450, 1920], [-100, 375]]]

################################################################################

screenx, screeny = 1280, 720  # int(1920/2), int(1080/2)
winsize = [screenx, screeny]

# prefer ffpyplayer first (helps on Windows)
prefs.general['movieLib'] = ['ffpyplayer', 'opencv']

win = visual.Window(winsize, allowGUI=False, color=[-1, -1, -1], fullscr=True,
                    screen=1, monitor='testMonitor', units='pix', waitBlanking=False)

# FUNCTIONS
# Function to collect when the spacebar has been pressed
keepitoff = 0
def get_bar():
    global keepitoff
    keys = event.getKeys()  # record whether a key is pressed
    if 'f' in keys:  # f for off. turns off the torchlight
        keepitoff = 1
    elif 'n' in keys:
        keepitoff = 0
    elif 'q' in keys:  # if the key is q (for quit), end recording and stimulus presentation
        if useEyetracker:
            eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
            # CV_Stop()
            # CV_Close()
        win.close()
        core.quit()
        print('Testing session ended')

# Function to determine where participant is looking
newleft_x = -1
newleft_y = -1
newright_x = -1
newright_y = -1
trigger = []
def gaze_data_callback(gaze_data):
    global newleft_x, newleft_y, newright_x, newright_y, trigger
    # startT = time.time()
    newleft_x = gaze_data.get('left_gaze_point_on_display_area')[0]
    newleft_y = gaze_data.get('left_gaze_point_on_display_area')[1]
    newright_x = gaze_data.get('right_gaze_point_on_display_area')[0]
    newright_y = gaze_data.get('right_gaze_point_on_display_area')[1]
    # Check if this file already exists. If not, write header in first row
    if len(trigger) == 0:
        gaze_data['triggers'] = ' '
    else:
        gaze_data['triggers'] = trigger
        trigger = []
    if (not os.path.isfile(output_file)):
        with open(output_file, 'w+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writeheader()
            w.writerow(gaze_data)
    else:
        with open(output_file, 'a+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writerow(gaze_data)
    return ()

eyetrackers = tr.find_all_eyetrackers()

# (your original PIL surfaces; kept as requested)
blackForeground = Image.new("RGB", (screenx, screeny), (1, 1, 1))
mask = Image.new("L", (screenx, screeny), 0)
draw = ImageDraw.Draw(mask)
imageStim = visual.ImageStim(win, blackForeground)

radius = 180  # circle radius

i = 0
x = 960
y = 540
TwoPi360 = 2 * math.pi / 360
TwoAndAHalfPi360 = 2.5 * math.pi / 360
width = ((winsize[0] / 2) - radius)
xOffset = (winsize[0] / 2)
height = (winsize[1] / 2) - radius
yOffset = winsize[1] / 2

# make interface where you choose whether to use only one eye or two
xs = [np.nan, np.nan]  # initialize vector for x
ys = [np.nan, np.nan]  # initialize vector for y

# load sounds
prefs.general['audioLib'] = ['pygame']
sounds = np.zeros(4, dtype=object)
sounds[0] = Path + 'Stimuli\woopey_elephant.wav'
sounds[1] = Path + 'Stimuli\woopey_giraffe.wav'
sounds[2] = Path + 'Stimuli\woopey_lion.wav'
sounds[3] = Path + 'Stimuli\woopey_zebra.wav'

# Load videos
stimuli = np.zeros([4, trials, 2], dtype=object)  # there are 12 trials for each of the 4 animals, 2 videos for each trial
n = -1
for foldername in os.listdir(Path + 'Stimuli\Stimuli1'):
    n += 1  # animal count
    m = -1  # location count
    for t_pos in target_pos[n, :]:
        for filename in os.listdir(Path + 'Stimuli\Stimuli1\\' + foldername):
            if str(t_pos) in filename:
                m += 1
                stimuli[n, m, 0] = Path + 'Stimuli\Stimuli1\\' + foldername + '\\' + filename
                stimuli[n, m, 1] = Path + 'Stimuli\Stimuli2\\' + foldername + '\\' + filename[0:-5] + 'b.mp4'

# Load background image
os.chdir(Path + "Stimuli")
background = visual.ImageStim(win, units='pix', size=winsize, image='background.jpg')
fixpoints = visual.ImageStim(win, units='pix', size=winsize, image='fixpoint.png')

iti = np.zeros(4, dtype=object)
iti[0] = visual.ImageStim(win, units='pix', size=winsize, image='background1.jpg')
iti[1] = visual.ImageStim(win, units='pix', size=winsize, image='background2.jpg')
iti[2] = visual.ImageStim(win, units='pix', size=winsize, image='background3.jpg')
iti[3] = visual.ImageStim(win, units='pix', size=winsize, image='background4.jpg')
isi = np.zeros(4, dtype=object)
isi[0] = visual.ImageStim(win, units='pix', size=winsize, image='background_open1.jpg')
isi[1] = visual.ImageStim(win, units='pix', size=winsize, image='background_open2.jpg')
isi[2] = visual.ImageStim(win, units='pix', size=winsize, image='background_open3.jpg')
isi[3] = visual.ImageStim(win, units='pix', size=winsize, image='background_open4.jpg')

# HERE STARTS THE RECORDING!
if useEyetracker:
    # CV_Start()
    output_file = Path + 'Data\infant' + str(int(subjnum)) + '.csv'
    eyetrackers[0].subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    # FROM THIS MOMENT ON: newleft and newright are constantly updated
core.wait(1)

for n in range(target_pos.shape[0]):  # for every sequence
    for m in range(trials):  # for every trial
        i = 0
        torch_on = 0
        if m >= trials - test_trials:  # only for the test trials
            duration = set_test_duration
        else:
            duration = set_duration
        target_predict_time = []
        threshold_reached = False
        trampoline_reached = False
        # area of interest of the target in pixels
        x_target_left = target_pos_pixels[target_pos[n, m]][0][0]
        x_target_right = target_pos_pixels[target_pos[n, m]][0][1]
        y_target_up = target_pos_pixels[target_pos[n, m]][1][0]
        y_target_down = target_pos_pixels[target_pos[n, m]][1][1]
        # show background until they watch at the screen properly
        iti[target_pos[n, m]].draw()
        im1 = win.getMovieFrame(buffer='back')
        enhancer = ImageEnhance.Brightness(im1)
        factor = dark[m]  # this will change across trials
        im2 = enhancer.enhance(factor)
        imageStim.image = im2  # set the resulting image in the visual.ImageStim
        imageStim.draw()
        fixpoints.draw()
        win.flip()
        print('_____________________________________________________________')

        # --- create MovieStims with audio disabled; fallback for older PsychoPy
        try:
            stimulus1 = visual.MovieStim(
                win, stimuli[n, m, 0], size=(screenx, screeny),
                flipVert=False, flipHoriz=False, loop=False, noAudio=True
            )
        except TypeError:
            stimulus1 = visual.MovieStim(
                win, stimuli[n, m, 0], size=(screenx, screeny),
                flipVert=False, flipHoriz=False, loop=False, audio=False
            )

        try:
            stimulus2 = visual.MovieStim(
                win, stimuli[n, m, 1], size=(screenx, screeny),
                flipVert=False, flipHoriz=False, loop=False, noAudio=True
            )
        except TypeError:
            stimulus2 = visual.MovieStim(
                win, stimuli[n, m, 1], size=(screenx, screeny),
                flipVert=False, flipHoriz=False, loop=False, audio=False
            )

        print("Ready for next trial. Press space when the child is looking")
        core.wait(1)
        event.waitKeys(keyList='space')
        try:
            ## character jumps ###############################################
            torch_on = 0
            if useEyetracker:
                trigger = b'start_' + stimuli[n, m, 0].encode('ascii')
                print(trigger)

            clk = core.getTime()
            played1 = 0
            played2 = 0

            # explicitly play and use FINISHED, with a timeout guard
            stimulus1.play()
            t_start_jump = core.getTime()
            dur1 = stimulus1.duration or 0.0
            timeout1 = max(dur1 + 2.0, 15.0)

            while (stimulus1.status != visual.FINISHED) and (core.getTime() - t_start_jump < timeout1):
                i += 1
                stimulus1.draw()
                im1 = win.getMovieFrame(buffer='back')
                enhancer = ImageEnhance.Brightness(im1)
                factor = dark[m]
                im2 = enhancer.enhance(factor)
                imageStim.image = im2
                imageStim.draw()
                fixpoints.draw()
                win.flip()
                get_bar()
                if i == 1:
                    boing = sound.Sound(Path + "Stimuli\\treasure.wav", stereo=True)
                    boing.play()
                if core.getTime() - clk >= 1.3 and played1 == 0:
                    boing = sound.Sound(Path + "Stimuli\\bounce1.wav", stereo=True)
                    boing.play()
                    played1 = 1
                if core.getTime() - clk >= 2.9 and played2 == 0:
                    boing = sound.Sound(Path + "Stimuli\\bounce2.wav", stereo=True)
                    boing.play()
                    played2 = 1

            if stimulus1.status != visual.FINISHED:
                print("WARNING: jump movie timed out; continuing.")
            stimulus1.stop()
            i = 0

            ## Interval between jump and reappearance ########################
            if keepitoff == 0:
                torch_on = 1
            if useEyetracker:
                if torch_on == 1:
                    trigger = b'torch_' + stimuli[n, m, 0].encode('ascii')
                else:
                    trigger = b'no-torch_' + stimuli[n, m, 0].encode('ascii')
            isi_start = core.getTime()
            while isi_start > core.getTime() - duration and not threshold_reached:
                # add circle to bg
                isi[target_pos[n, m]].draw()
                im1 = win.getMovieFrame(buffer='back')
                enhancer = ImageEnhance.Brightness(im1)
                factor = dark[m]
                im2 = enhancer.enhance(factor)
                draw.bitmap((0, 0), mask)  # clear the circle (kept as in your code)
                xs = [np.nan, np.nan]  # initialize vector for x
                ys = [np.nan, np.nan]  # initialize vector for y
                if newright_x + newright_y > -1 or newleft_x + newleft_y > -1:
                    xs.append(np.nanmean([newleft_x, newright_x]) * winsize[0])
                    ys.append(np.nanmean([newleft_y, newright_y]) * winsize[1])
                    xs = xs[1:]
                    ys = ys[1:]
                    x = np.nanmean(xs)  # a fixation filter will be used instead of this line
                    y = np.nanmean(ys)

                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)  # draw the circle
                get_bar()
                if torch_on:
                    im = Image.composite(im1, im2, mask)  # spotlight composite
                else:
                    im = im1

                if core.getTime() >= isi_start + fixation_torch and torch_on:
                    # ADD here that character appears only when looking at correct spot:
                    if m >= trials - test_trials:  # only for the test trials
                        # if they look at correct location
                        if skewed[n] == 1 or trampoline_reached:  # comment out trampoline_reached==True if trampoline threshold is enough for uniform
                            if x_target_left < x < x_target_right and y_target_up < y < y_target_down:
                                target_predict_time.append(core.getTime())  # get the time whet that happens
                                if len(target_predict_time) > 1:
                                    if target_predict_time[-1] - target_predict_time[0] > threshold_reaching_time:  # at least 500ms
                                        threshold_reached = True  # stop the waiting and show the target
                        else:  # in the uniform condition, they have to find the trampoline
                            if x_target_left < x < x_target_right and y_target_up + 750 < y < y_target_down + 705:  # trampoline location
                                target_predict_time.append(core.getTime())
                                if len(target_predict_time) > 1:
                                    if target_predict_time[-1] - target_predict_time[0] > trampoline_reaching_time:
                                        trampoline_reached = True  # found trampoline; ISI continues as in skewed
                                        target_predict_time = []

                imageStim.image = im  # set the resulting image in the visual.ImageStim
                imageStim.draw()      # draw to the window
                fixpoints.draw()
                win.flip()

            if m < trials - test_trials:  # in familiarization trials, always show the target
                threshold_reached = True
            if torch_on == 0:
                threshold_reached = True

            ## character reappears ############################################
            if useEyetracker:
                trigger = b'wave_' + stimuli[n, m, 0].encode('ascii')

            stimulus2.play()
            t_start_wave = core.getTime()
            dur2 = stimulus2.duration or 0.0
            timeout2 = max(dur2 + 2.0, 15.0)

            while (stimulus2.status != visual.FINISHED) and (core.getTime() - t_start_wave < timeout2):  # otherwise add time here
                i += 1
                if threshold_reached:
                    stimulus2.draw()
                else:
                    stimulus2.draw()
                    isi[target_pos[n, m]].draw()

                im1 = win.getMovieFrame(buffer='back')
                enhancer = ImageEnhance.Brightness(im1)
                factor = dark[m]
                im2 = enhancer.enhance(factor)
                draw.bitmap((0, 0), mask)  # clear the circle
                if newright_x + newright_y > -1 or newleft_x + newleft_y > -1:
                    xs.append(np.nanmean([newleft_x, newright_x]) * winsize[0])
                    ys.append(np.nanmean([newleft_y, newright_y]) * winsize[1])
                    xs = xs[1:]
                    ys = ys[1:]
                    x = np.nanmean(xs)
                    y = np.nanmean(ys)

                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
                get_bar()
                if torch_on:
                    imageStim.image = Image.composite(im1, im2, mask)
                else:
                    imageStim.image = im1
                imageStim.draw()
                fixpoints.draw()
                if i == 1:
                    boing = sound.Sound(sounds[n], stereo=True)
                    boing.play()
                win.flip()

            if stimulus2.status != visual.FINISHED:
                print("WARNING: wave movie timed out; continuing.")
            stimulus2.stop()

            if useEyetracker:
                trigger = b'end_wave_' + stimuli[n, m, 0].encode('ascii')
        except KeyboardInterrupt:
            pass

# Stop Eyetracker
if useEyetracker:
    eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    # CV_Stop()
    # CV_Close()

win.close()
core.quit()

# add sounds at right moments
# AFTER AUDIO: gaze contingent only in SEARCH phase + att getter and sound when torchlight starts

# now it collects coords at 300Hz BUT updates just every frame
