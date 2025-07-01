# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 15:54:37 2020

@author: Francesco Poli, Hubert Voogd
"""

from psychopy import visual, core, event, sound, gui, prefs
import numpy as np
import pandas as pd
import tobii_research as tr
import win32con
import pywintypes
import os
import csv

active_condition = 1 
yoked_condition = 1

#remember to change the path!!!
#Path = r"C:\Users\Experiment\Documents\Infant_Torchlight\py36_tobii\A_InfantActiveLearn\\"

################## Initial set up for stimuli #################################
n_locations = 6
total_n_stimuli = 24
threshold_time_show = .5 # seconds in AOI before the gaze contingent stimulus appears
threshold_time_change = .2
minimum_time_targetonscreen = 0.5
duration_phase1 = 60
box_size = 300/1920*1280
stimulus_size = 200/1920*1280

# to find the positions of the aois, we set 4 corners and then we can look for 
# equidistant positions within these 4 corners (up left, up right, down left, down right)
n_x = 3
n_y = 2
corners = [[300/1920*1280,(1920-300)/1920*1280],[250/1080*720,(1080-250)/1080*720]]
## this function starts from number of corners and number of aois required to 
## return equidistant aois:
def equidistant_aois(n_x, n_y, corners):
    aois=[]
    proportion_x = np.linspace(corners[0][0],corners[0][1],n_x)
    proportion_y = np.linspace(corners[1][0],corners[1][1],n_y)
    for this_n_y in range(n_y):
        for this_n_x in range(n_x):
            aois.append([proportion_x[this_n_x], proportion_y[this_n_y]])
    return(aois)
    
aoi_centers = equidistant_aois(n_x, n_y, corners)
#aoi_centers = [[300,250],[920,250],[1920-300,250],[300,1080-250],[920,1080-250],[1920-300,1080-250]] #[[440,540],[1920-440,540]]
aoi_centers_phase2 = [[400/1920*1280,540/1080*720],[(1920-400)/1920*1280,540/1080*720]]
aoi_side_length = 200/1920*1280
ntrials=1000
ntrials_phase2 = 1000


# retrieve and use yoked data from previous participant
yoked_ones = os.listdir(Path+r"yoked_data\\")
yoked = pd.read_csv(Path + r"yoked_data\\" + yoked_ones[-1])
yoked_stamp = Path + r"yoked_data\\" + yoked_ones[-1]
yoked_stamp = yoked_stamp[-3:]

aois_yoked = []
start_stamp_yoked = []
end_stamp_yoked = []
for n,t in zip(yoked['triggers'],yoked['device_time_stamp']):
    if 'start_stimulus' in n:
        aois_yoked.append(int(n[15])) # this only works if N locations is less than 10
        start_stamp_yoked.append(t)
        # now it includes the static-torch time (500ms)
    elif 'stop_stimulus' in n:
        start_stamp_yoked.append(t)
        #aois.append(-1)
    elif 'start_trial' in n:
        start_stamp_yoked.append(t)
        aois_yoked.append(-1)

stamps_yoked = np.array(start_stamp_yoked)
stamps_yoked = np.diff(stamps_yoked)/1000000

#print(len(stamps_yoked), len(aois_yoked))
yoked = pd.DataFrame({'time' : stamps_yoked, 'aoi' : aois_yoked})

################## Initial set up for eye-tracker #############################
useEyetracker = True #TRUE WHEN AT THE LAB!
eyeHz = 60 #eye-tracker sampling frequency (in Hz)
eyetrackers = tr.find_all_eyetrackers()
FilterSize = 2 # moving average of eye tracking samples
xs = [np.nan]*FilterSize
ys = [np.nan]*FilterSize

################## Pop-up window to choose participant ########################
Dlg = gui.Dlg(title="ActiveLearning")
Dlg.addField('Participant Number:')
Dlg.addText('(Choose a number between 1 and 1000)')
selection = Dlg.show()  # show dialog and wait for OK or Cancel
if Dlg.OK:                                            
    subjnum = float(selection[0])
else:
    core.quit()
    

############################# Screen Settings #################################

devmode = pywintypes.DEVMODEType()

screenx, screeny = 1280, 720 # screen size
devmode.PelsWidth = screenx
devmode.PelsHeight = screeny

devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

winsize = [screenx,screeny] 
win = visual.Window(winsize, screen=0, fullscr=True, monitor="testMonitor", units='cm', allowStencil = True) #change screen to 0

################################ FUNCTIONS ####################################
# Function to detect when a key has been pressed
keepitoff=0
def get_bar():
    global keepitoff
    keys = event.getKeys() #record whether a key is pressed
    if 'f' in keys: #o for off. turns off the torchlight
        keepitoff=1
    elif 'n' in keys:
        keepitoff=0
    elif 'q' in keys: # if the key is q (for quit), end recording and stimulus presentation
        if useEyetracker:
            eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
            #CV_Stop()
            #CV_Close()
        win.close()
        core.quit()
        print('Testing session ended')
        
# Function to determine where participant is looking and save eye tracking data
newleft_x=-1
newleft_y=-1
newright_x=-1
newright_y=-1
trigger=[]
def gaze_data_callback(gaze_data):
    global newleft_x, newleft_y, newright_x, newright_y, trigger
    #startT = time.time()
    newleft_x = gaze_data.get('left_gaze_point_on_display_area')[0]
    newleft_y = gaze_data.get('left_gaze_point_on_display_area')[1]
    newright_x = gaze_data.get('right_gaze_point_on_display_area')[0]
    newright_y = gaze_data.get('right_gaze_point_on_display_area')[1]
    # Check if this file already exists. If not, write header in first row
    if len(trigger)==0:
        gaze_data['triggers']=' '
    else:
        gaze_data['triggers']=trigger
        trigger=[]
    #print(gaze_data)
    if (not os.path.isfile(output_file)):
        with open(output_file,'w+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writeheader()
            w.writerow(gaze_data)
    else:  
        #print(gaze_data)
        with open(output_file,'a+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writerow(gaze_data)
    return()

# Function to set the limits on an area of interest (aoi)
def square_aoi(center_x, center_y, side):
    x_left = center_x - side/2
    x_right = center_x + side/2
    y_up = center_y - side/2
    y_down = center_y + side/2
    return(x_left,x_right,y_up,y_down)

# Function to wait for n seconds before doing something else
def show_for(stimulus, sec):
    start_waiting = core.getTime()
    while core.getTime() - start_waiting > sec:
        stimulus.draw()
        win.flip()
        pass

############################## LOAD STIMULI ###################################
# sound
prefs.general['audioLib'] = ['pygame']
music = sound.Sound(Path+"Stimuli\\hothothot.wav", stereo=True)


#Load background image
os.chdir(Path+"Stimuli")
background=visual.ImageStim(win, units= 'pix', size = winsize, image = 'background.png')

box=np.zeros([n_locations],dtype=object)
for x in range(n_locations):
    box[x]=visual.ImageStim(win, units= 'pix', size = [box_size,box_size], image = 'box.png')
    box[x].pos = (aoi_centers[x][0]-screenx/2, screeny/2 -aoi_centers[x][1])

box_light = visual.ImageStim(win, units= 'pix', size = [box_size,box_size], image = 'box_light.png')

stimulus=np.zeros(total_n_stimuli,dtype=object)
# shuffle stimuli
shuffle_idx = np.random.choice(range(0,total_n_stimuli), size = total_n_stimuli, replace=False)
shuffle_idx.tofile(Path+r"Data_rand\rand_infant" + str(int(subjnum)) + '.csv',sep = ',')

n=-1
for filename in os.listdir(Path+r"Stimuli\Objects\\"):  
    if 'png' in filename:
        n+=1
        n2 = shuffle_idx[n]
        stimulus[n2]=visual.ImageStim(win, units= 'pix', size = [stimulus_size,stimulus_size], image = r'Objects\\'+ filename)

#save randomization
#np.savetxt(Path+'Data_rand\rand_infant' + str(int(subjnum)) + '.csv', shuffle_idx, delimiter = ",")
#pd.DataFrame(shuffle_idx).to_csv(Path+'Data\rand_infant' + str(int(subjnum)) + '.csv') 
#shuffle_idx.tofile('rand.csv',sep = ',') 
# pick N for each condition and N novel ones
train_stimuli_n = total_n_stimuli/4
novel_stimuli_n = total_n_stimuli/2

######################## HERE STARTS THE RECORDING! ###########################
if useEyetracker:
    #CV_Start()
    output_file = Path+'Data\infant' + str(int(subjnum)) + '.csv'
    eyetrackers[0].subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback, as_dictionary=True)
    # FROM THIS MOMENT ON: newleft and newright are constantly updated

    

background.draw()
for this_box in box:
    this_box.draw()
win.flip()
event.waitKeys(keyList='space')
music.play()
if  active_condition == 1:
    time_zero = core.getTime()
    trial_count=0
    #for n in range(ntrials): #for every block
    while core.getTime() - time_zero < duration_phase1:
        trial_count+=1
        show_light = 0 
        threshold_reached = False
        track_time = None
        tracked_aoi=-1
        try:
            if useEyetracker:
                trigger = 'start_trial_'+str(trial_count)
            while threshold_reached==False:
                background.draw()
                for this_box in box:
                    this_box.draw()
                if show_light == 1:
                    box_light.draw()
                win.flip() # flip the window
                get_bar()
                if newright_x+newright_y>-1 or newleft_x+newleft_y>-1:
                    xs.append(np.nanmean([newleft_x, newright_x])*winsize[0])  # get x value (get it from gazedata!!)
                    ys.append(np.nanmean([newleft_y, newright_y])*winsize[1])  # get y value (get it from gazedata!!)
                    xs=xs[1:]
                    ys=ys[1:]
                    x=np.nanmean(xs) #a fixation filter will be used instead of this line
                    y=np.nanmean(ys)
                    for n in range(len(aoi_centers)): #for every aoi
                        x_left, x_right, y_up, y_down = square_aoi(aoi_centers[n][0],aoi_centers[n][1],aoi_side_length)
                        if x_left < x < x_right and y_up < y < y_down: #check if gaze is in the aoi
                            if track_time is None: #if it's the first look in an aoi
                                track_time = core.getTime() # get the time of when that happens
                                tracked_aoi = n #and remember what aoi
                            else: # if there's already a look to aoi
                                if tracked_aoi == n: # if the look is in the same aoi
                                    if core.getTime() - track_time > .2:
                                        box_light.pos = (aoi_centers[n][0]-screenx/2, screeny/2 -aoi_centers[n][1])
                                        show_light = 1
                                    if core.getTime() - track_time > threshold_time_show:# check if threshold time is reached
                                        threshold_reached=True # if reached, stop the waiting and show the target
                                        break #stop the for-loop
                                else: #if it's another aoi, restart counting from zero
                                    track_time = core.getTime() #reset time
                                    tracked_aoi = n #reset aoi
            # show stimulus in correct location
            stimulus[n].pos = (aoi_centers[n][0]-screenx/2,(screeny/2-aoi_centers[n][1]))
            trigger = 'start_stimulus_'+str(n)+'_trial_'+str(trial_count)
            track_time = None
            start_time = core.getTime()
            while threshold_reached:
                background.draw()
                for this_box in box:
                    this_box.draw()
                box_light.draw()
                stimulus[n].draw()  
                if newright_x+newright_y>-1 or newleft_x+newleft_y>-1:
                    xs.append(np.nanmean([newleft_x, newright_x])*winsize[0])  # get x value (get it from gazedata!!)
                    ys.append(np.nanmean([newleft_y, newright_y])*winsize[1])  # get y value (get it from gazedata!!)
                    xs=xs[1:]
                    ys=ys[1:]
                    x=np.nanmean(xs) #a fixation filter will be used instead of this line
                    y=np.nanmean(ys)
                    if (x < x_left or x > x_right or y < y_up or y > y_down) and core.getTime() - start_time > minimum_time_targetonscreen:# or math.isnan(x) or math.isnan(y): #check if gaze is outside of the aoi         
                        print(track_time,)                    
                        if track_time is None: #if it's the first look outside aoi
                            track_time = core.getTime() # get the time of when that happens
                        else: # if there's already a look outside aoi
                            if core.getTime() - track_time > threshold_time_change:# check if threshold time is reached
                                threshold_reached=False # if reached, stop the waiting and show the target
                win.flip()
                get_bar()
            trigger = 'stop_stimulus_'+str(n)+'_trial_'+str(trial_count)
        except KeyboardInterrupt:
            pass



if yoked_condition == 1:   
    music.pause()
    background.draw() 
    win.flip()
    event.waitKeys(keyList='space')
    music.play()
    trigger = 'beginning_yoked_to_'+yoked_stamp
    for t,aoi_n in zip(yoked['time'],yoked['aoi']): 
        if aoi_n>=0:
            if t <= .6:
                start_time = core.getTime()
                while core.getTime() - start_time < t:
                    background.draw()
                    for this_box in box:
                        this_box.draw()
                    box_light.pos = (aoi_centers[aoi_n][0]-screenx/2,(screeny/2-aoi_centers[aoi_n][1]))
                    box_light.draw()
                    win.flip()
            else:
                background.draw()
                for this_box in box:
                    this_box.draw()
                box_light.pos = (aoi_centers[aoi_n][0]-screenx/2,(screeny/2-aoi_centers[aoi_n][1]))
                box_light.draw()
                win.flip()
                core.wait(.6)
                start_time = core.getTime()
                while core.getTime() - start_time < t:
                    background.draw()
                    for this_box in box:
                        this_box.draw()
                    box_light.draw()
                    stimulus[int(aoi_n + train_stimuli_n)].pos = (aoi_centers[aoi_n][0]-screenx/2,(screeny/2-aoi_centers[aoi_n][1]))
                    stimulus[int(aoi_n + train_stimuli_n)].draw()  
                    win.flip()
        else:
            start_time = core.getTime()
            while core.getTime() - start_time < t:
                background.draw()
                for this_box in box:
                    this_box.draw()
                win.flip()

# randomize presentation for active and yoked data
rand_n = [0,6,1,7,2,8,3,9,4,10,5,11]

music.stop()
background.draw()
win.flip()
event.waitKeys(keyList='space') 
for m, n in zip(range(int(total_n_stimuli/2), total_n_stimuli), rand_n):
    targetsound = sound.Sound(Path+"Stimuli\\targetsound.wav", stereo=True)
    # choose familiar item location at random (0 or 1)
    familiar_location = int(np.random.binomial(1, .5, 1))
    novel_location = 0
    if familiar_location == 0:
        novel_location=1
    trigger = 'familiar_number_'+str(m)+'_location_'+str(familiar_location)
    print(n,m)
    stimulus[n].pos = (aoi_centers_phase2[familiar_location][0]-screenx/2,0)
    stimulus[m].pos = (aoi_centers_phase2[novel_location][0]-screenx/2,0)
    stimulus[n].size = (350/1920*1280,350/1920*1280)
    stimulus[m].size = (350/1920*1280,350/1920*1280) 
    background.draw()
    stimulus[n].draw()
    stimulus[m].draw()
    targetsound.play()
    win.flip()
    core.wait(5)
    background.draw()
    win.flip()
    core.wait(1)
    get_bar()
    

#Stop Eyetracker
if useEyetracker:
    eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    #CV_Stop()
    #CV_Close() 
        
win.close()
core.quit()

#print("do you want to yoke next participant to this one? [y/n]")
# y, n
#event.waitKeys(keyList=['y','n'])


#randomize conditions in test trials