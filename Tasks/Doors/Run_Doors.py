# -*- coding: utf-8 -*-
"""
Created on 24/10/2022

@author: Francesco Poli, Yilin Li
"""
from psychopy import visual, core, event, sound, gui, prefs
import sys, importlib
import math
import numpy as np
import pandas as pd
import tobii_research as tr
import glob, os
import csv
import random
import time

# CHANGE THE PATH!!!!
Path = r"C:\Users\itali\Documents\iSearchBattery\Tasks\Doors\\" 
################## Initial set up for stimuli #################################

screenx, screeny = 1280, 720

total_n_stimuli = 8 #old n_locations 
n_trials = 100
closed_time = 1
open_time = 3
max_for_lookaway = 6 #in seconds
last_appear = 1
stimuli_time = 7
wait_time_closed_door = 1
max_duration = 60*5


cond = [[1,total_n_stimuli], # 0 for 1 animal; 1 for many. # animal cond
        [1,total_n_stimuli]] #                             # toy cond

threshold_time = .5
animal_size = [250, 250]
feed_size = [200, 200]
# actual size = 881x1007
door_x = 600
door_size = [door_x,door_x]


#actual center coord (in px): 274, 505
door_center = (0,0)
center = (0,0)

# to find the positions of the aois, we set 4 corners and then we can look for 
# equidistant positions within these 4 corners (up left, up right, down left, down right)
n_x = 4
n_y = 2
corners = [[200,screenx-200],[160,screeny-160]]
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



start_trial_centers = equidistant_aois(n_x, n_y, corners)

# assuming door is in the centre, the limits of aoi are:
x_left = -door_size[0]/2*1.1 + screenx/2
x_right = door_size[0]/2*1.1 + screenx/2
y_down = door_size[1]/2*1.1 + screeny/2
y_up = -door_size[1]/2*1.1 + screeny/2



################## Initial set up for eye-tracker #############################
useEyetracker = True #TRUE WHEN AT THE LAB!
#eyeHz = 60 #eye-tracker sampling frequency (in Hz)
eyetrackers = tr.find_all_eyetrackers()
FilterSize = 2 # moving average of eye tracking samples
xs = [np.nan]*FilterSize
ys = [np.nan]*FilterSize


################## Pop-up window to choose participant ########################
counterbalance = pd.DataFrame({
    "order": [1,2,3,4,5,6,7,8],
    "block":   [1,1,1,1,2,2,2,2],
    "stimuli": [1,8,1,8,8,1,8,1],
    "animals": [0,0,1,1,1,1,0,0]
})

# =========================
# Ask subject & block
# =========================
GUI_off = False
while not GUI_off:
    Dlg = gui.Dlg(title="Doors")
    Dlg.addText('Subject info')
    Dlg.addField('ID (Choose a number between 1 and 1000):')
    Dlg.addField('Block (1 or 2):')
    selection = Dlg.show()
    if not Dlg.OK:
        core.quit()

    try:
        Subject = int(selection[0])
        n_block = int(selection[1])
        
        if n_block not in [1,2]:
            raise ValueError
        GUI_off = True
    except ValueError:
        print("⚠️ Enter valid numbers (block 1 or 2).")
        continue

subjnum = Subject
# =========================
# Assign condition from table
# =========================
# Cycle subject numbers through the 4 orders
order_index = (subjnum - 1) % 4   # 0..3
if n_block == 2:
    order_index += 4              # shift to second half of table

row = counterbalance.iloc[order_index]
n_stimuli = row["stimuli"]
toys_cond = row["animals"]



############################# Screen Settings #################################
#screenx, screeny = 1920, 1080
winsize = [screenx, screeny]

win = visual.Window(winsize, allowGUI=False,color = [-1,-1,-1], fullscr=True,
    screen=1,monitor='testMonitor',units='pix',waitBlanking=False)

################################ FUNCTIONS ####################################
# Function to detect when a key has been pressed
def get_bar():
    keys = event.getKeys() #record whether a key is pressed
    if 'q' in keys: # if the key is q (for quit), end recording and stimulus presentation
        if useEyetracker:
            eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
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
    # get eye data for gaze contingent commands
    newleft_x = gaze_data.get('left_gaze_point_on_display_area')[0]
    newleft_y = gaze_data.get('left_gaze_point_on_display_area')[1]
    newright_x = gaze_data.get('right_gaze_point_on_display_area')[0]
    newright_y = gaze_data.get('right_gaze_point_on_display_area')[1]
    
    
    # save data in csv file
    # Check if this file already exists. If not, write header in first row
    if len(trigger)==0:
        gaze_data['triggers']=' '
    else:
        gaze_data['triggers']=trigger
        trigger=[]
        
    if (not os.path.isfile(output_file)):
        with open(output_file,'w+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writeheader()
            w.writerow(gaze_data)
    else:  
        with open(output_file,'a+', newline='') as f:
            w = csv.DictWriter(f, gaze_data.keys())
            w.writerow(gaze_data)
    return()

############################## LOAD STIMULI ###################################
# sound
prefs.general['audioLib'] = ['pygame']
#music = sound.Sound(Path+"Stimuli\\hothothot.wav", stereo=True)
if toys_cond == 0:
    audio1=sound.Sound(Path+"Stimuli\Audios\\animal1it.wav", stereo=True)
    #audio2=sound.Sound(Path+"Stimuli\Audios\\Animal2.wav", stereo=True)
    audio3=sound.Sound(Path+"Stimuli\Audios\\animal2it.wav", stereo=True)

elif toys_cond == 1:
    audio1=sound.Sound(Path+"Stimuli\Audios\\toy1it.wav", stereo=True)
    #audio2=sound.Sound(Path+"Stimuli\Audios\\Toy2.wav", stereo=True)
    audio3=sound.Sound(Path+"Stimuli\Audios\\toy2it.wav", stereo=True)

feed_music=sound.Sound(Path+"Stimuli\Audios\\sound.wav", stereo=True)
#fixation
#fixation = visual.ShapeStim(win, 
    #vertices=((0, -2.0), (0, 2.0), (0,0), (-2.0,0), (2.0, 0)),
    #lineWidth=20,
    #closeShape=False,
    #lineColor="black")


#Load background image and door images
os.chdir(Path+"Stimuli")

background=visual.ImageStim(win, units= 'pix', size = winsize, image = 'background.png')

if toys_cond == 0:
    fixation = visual.ImageStim(win, units= 'pix', size = door_size, image = 'fix.png')
    closed_door=visual.ImageStim(win, units= 'pix', size = door_size, image = 'Doors\\closed_door.png')
    closed_door.pos = door_center

    open_door=visual.ImageStim(win, units= 'pix', size = door_size, image = 'Doors\\open_door.png')
    open_door.pos = door_center

elif toys_cond == 1:
    fixation = visual.ImageStim(win, units= 'pix', size = door_size, image = 'fix_toy.png')
    closed_door=visual.ImageStim(win, units= 'pix', size = door_size, image = 'Doors\\toy_closed_door.png')
    closed_door.pos = door_center

    open_door=visual.ImageStim(win, units= 'pix', size = door_size, image = 'Doors\\toy_open_door.png')
    open_door.pos = door_center



# import animals

# initialize array 
animal_stim=np.zeros(total_n_stimuli,dtype=object)
# initialize for second loop:
shuffle_idx = np.random.choice(range(0,total_n_stimuli), size = total_n_stimuli, replace=False)
# shuffle_idx contains numbers between 0 and 8 in random order

# import filenames animals
filename_list = []
for filename in os.listdir(Path+r"Stimuli\Animals\\"):  
    if 'png' in filename:
        filename_list.append(filename)

if toys_cond == 0:
    if n_stimuli == 1:
    # randomly select one number between 0 and 8    
        stimulus_idx = int(np.random.choice(range(0,len(filename_list)), size = 1))
    
    # import 8 times the same stimulus            
        for x in range(total_n_stimuli):
            animal_stim[x]=visual.ImageStim(win, units= 'pix', size = animal_size, image = r'Animals\\' + filename_list[stimulus_idx])
            animal_stim[x].pos = (start_trial_centers[x][0]-screenx/2, screeny/2 -start_trial_centers[x][1])
        
        animal_feed = visual.ImageStim(win, units= 'pix', size = feed_size, image = r'Animals\\' + filename_list[stimulus_idx])
        animal_feed.pos = center
        
    elif n_stimuli == 8: #if we start with 8 animals or 1 toy
        for filename, n in zip(filename_list, shuffle_idx):   
            animal_stim[n]=visual.ImageStim(win, units= 'pix', size = animal_size, image = r'Animals\\'+ filename)
            animal_stim[n].pos = (start_trial_centers[n][0]-screenx/2, screeny/2 -start_trial_centers[n][1])
        
        animal_feed = visual.ImageStim(win, units= 'pix', size = feed_size, image = r'Animals\\'+ filename)
        animal_feed.pos = center
    else:
        raise Exception('wrong number. Please insert a valid number')
        

# import toys
toy_stim=np.zeros(total_n_stimuli,dtype=object)
# initialize for second loop:
shuffle_idx = np.random.choice(range(0,total_n_stimuli), size = total_n_stimuli, replace=False)
# shuffle_idx contains numbers between 0 and 8 in random order
# import filenames toys
filename_list = []
for filename in os.listdir(Path+r"Stimuli\Toys\\"):  
    if 'png' in filename:
        filename_list.append(filename)

# decide whether to import one or eight animals
if toys_cond == 1: #if we start with one animal or 8 toys
    if n_stimuli == 1:
    # randomly select one number between 0 and 8    
        stimulus_idx = int(np.random.choice(range(0,len(filename_list)), size = 1))
    
    # import 8 times the same stimulus            
        for x in range(total_n_stimuli):
            toy_stim[x]=visual.ImageStim(win, units= 'pix', size = animal_size, image = r'Toys\\' + filename_list[stimulus_idx])
            toy_stim[x].pos = (start_trial_centers[x][0]-screenx/2, screeny/2 -start_trial_centers[x][1])
        
        toy_feed=visual.ImageStim(win, units= 'pix', size = feed_size, image = r'Toys\\' + filename_list[stimulus_idx])
        toy_feed.pos = center

    elif n_stimuli == 8:
        for filename, n in zip(filename_list, shuffle_idx):   
            toy_stim[n]=visual.ImageStim(win, units= 'pix', size = animal_size, image = r'Toys\\'+ filename)
            toy_stim[n].pos = (start_trial_centers[n][0]-screenx/2, screeny/2 -start_trial_centers[n][1])
        
        toy_feed=visual.ImageStim(win, units= 'pix', size = feed_size, image = r'Toys\\'+ filename)
        toy_feed.pos = center
    else:
        raise Exception('wrong number. Please insert a valid number')



    
######################## HERE STARTS THE RECORDING! ###########################
if useEyetracker:
    #CV_Start()
    output_file = Path+'Data\\infant' + str(int(subjnum)) + '_' + str(int(n_block)) + '_' + str(int(n_stimuli)) + '_' + str(int(toys_cond)) + '.csv'
    eyetrackers[0].subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback, as_dictionary=True)
    # FROM THIS MOMENT ON: newleft and newright are constantly updated

if toys_cond == 1:
    stimuli = toy_stim
elif toys_cond == 0:
    stimuli = animal_stim
    

if toys_cond == 1:
    feedback = toy_feed
elif toys_cond == 0:
    feedback = animal_feed


# show background:
background.draw()
win.flip()
#music.play()
print('\n\n=========================== Press SPACE to start ===========================')
event.waitKeys(keyList='space')

trigger = 'start_task_n_block' + str(n_block) + '_n_stimuli_' + str(n_stimuli) + '_condition_' + str(toys_cond)

# show 8 stimuli (either identical or different) for 3s
background.draw()
for this_stimulus in stimuli: # the fisrt set of stimuli (either toys or animals)
    this_stimulus.draw()
win.flip()
audio1.play()
core.wait(stimuli_time)
audio1.stop()
print('\n\n=========================== Press SPACE to continue ===========================')
event.waitKeys(keyList='space')
# 
background.draw()
closed_door.draw()
win.flip()
#audio2.play()
core.wait(8)
#audio2.stop()
print('\n\n=========================== Press SPACE to continue ===========================')
event.waitKeys(keyList='space')

# show backgroud for 1s
background.draw()
open_door.draw()
win.flip()
audio3.play()
core.wait(3.5)
audio3.stop()
print('\n\n=========================== Press SPACE to continue ===========================')
event.waitKeys(keyList='space')

# start showing door trials. The first trial is a familiarization trial.
start_time = core.getTime()
while core.getTime() - start_time < max_duration:
    for n in range(n_trials):
        threshold_reached = False
        end_study = False
        end_reached = False		
        track_time = None
        
        nan_time = None
        try:
            if useEyetracker:
                trigger = 'fixation_trial_'+str(n)
                fix_time = random.uniform(1.5,3)
                background.draw()
                fixation.draw()
                win.flip()
                core.wait(fix_time)
            #time_zero = core.getTime()
            while threshold_reached==False and end_study == False:
                
                
                trigger = 'closed_door_trial_'+str(n)
                background.draw()
                closed_door.draw()
                win.flip() # flip the window
                core.wait(wait_time_closed_door)
                get_bar()
                
                #if newright_x+newright_y>-1 or newleft_x+newleft_y>-1:

                    # add new gaze coordinates
                xs.append(np.nanmean([newleft_x, newright_x])*winsize[0])  # mean x coord
                ys.append(np.nanmean([newleft_y, newright_y])*winsize[1])  # mean y coord
                    # remove oldest gaze coordinates
                xs=xs[1:]
                ys=ys[1:]
                    # take average of gaze coordinates
                x=np.nanmean(xs) #a fixation filter will be used instead of this line
                y=np.nanmean(ys)
                                   
                    # check whether they are looking at the door
                if x_left < x < x_right and y_up < y < y_down: #check if gaze is in the aoi
                    if track_time is None: #if it's the first look in an aoi
                            track_time = core.getTime() # get the time of when that happens
                    else: # if there's already a look to aoi
                            if core.getTime() - track_time > threshold_time:# check if threshold time is reached
                                threshold_reached=True # if reached, stop the waiting and show the target
                
                else:				
                        if nan_time is None: #if it's the first look in an aoi
                            nan_time = core.getTime() # get the time of when that happens
                        else: # if there's already a look to aoi
                            if core.getTime() - nan_time > max_for_lookaway:# check if threshold time is reached
                                end_study = True  
                                
            if threshold_reached==True: 
                trigger = 'open_door_trial_'+str(n)                        
                # show open door
                background.draw()
                open_door.draw()
                win.flip()
                core.wait(open_time)

            elif end_study==True:
                trigger = 'end_task_at_trial_'+str(n)			
                background.draw()
                closed_door.draw()
                win.flip()
                feed_music.play()
                print('\n\n=========================== Press SPACE to show feedback ===========================')
                event.waitKeys(keyList='space')
				
                feed_music.stop()
                background.draw()
                open_door.draw()
                feedback.draw()
                win.flip()
                print('\n\n=========================== Press Q to quit ===========================')
                event.waitKeys(keyList='q')
   
                win.close()  
                print('\n\n=========================== Testing session ended ===========================')
                core.quit()              
        except KeyboardInterrupt:
                pass       

if end_study==False:
                trigger = 'end_task_at_trial_'+str(n)			
                background.draw()
                closed_door.draw()
                win.flip()
                core.wait(wait_time_closed_door)
                background.draw()
                open_door.draw()
                feedback.draw()
                win.flip()
                print('\n\n=========================== Press Q to quit ===========================')
                event.waitKeys(keyList='q')
   
                win.close()
                print('\n\n=========================== Testing session ended ===========================')
                core.quit()    
			
#Stop Eyetracker
if useEyetracker:
    eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
