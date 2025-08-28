# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:46:21 2021

@author: U661121
"""
#################### Import #################################################
from psychopy import visual, core, event, sound, gui, prefs #clock
import pandas as pd
import numpy as np
import tobii_research as tr
import os
import csv

et_rate = 300
missing_seconds = 10

trigger = ''
def gaze_data_callback(gaze_data):
    global trigger
    global warn_count
    
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
            
    le = np.float(gaze_data.left_eye.gaze_point.position_on_display_area[0])
    re = np.float(gaze_data.right_eye.gaze_point.position_on_display_area[0])
    both_eyes = np.nanmean([le, re])
    if np.isnan(both_eyes):
        warn_count += 1
    else: 
        warn_count = 0
    if warn_count > et_rate * missing_seconds:
        print('\n\n\nWARNING:\n\nNO DATA WAS COLLECTED\n\n'+'IN THE LAST '+str(missing_seconds)+' SECONDS')
    return()

warn_count = 0

eyetrackers = tr.find_all_eyetrackers()
useEyetracker = True #TRUE WHEN AT THE LAB!

Path = r'C:\Users\itali\Documents\iSearchBattery\Tasks\InformationGain\\'
 
##################### Funtions ##############################################
# initialize some variables
track_time=list()
cancel_time=0
letsgo=0

# Function to collect when the spacebar has been pressed
def get_bar():
    global track_time, cancel_time
    keys = event.getKeys() #record whether a key is pressed
    if 'space' in keys: #if the key is 'space', get what the time is (and send a timestamp to eyetracker)
        track_time.append(core.getTime())
    if 'x' in keys: #if the key is 'x', get what the time is (and send a timestamp to eyetracker)
        cancel_time=core.getTime()  ########## now when bar is pressed goes to next. no good after 1 sec
    elif 'q' in keys: # if the key is q (for quit), end recording and stimulus presentation
        DlgQuit.show()  # show dialog and wait for OK or Cancel
        if DlgQuit.OK: 
            hothothot.stop()
            #Stop Eyetracker
            if useEyetracker:
                eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
            show_end()
            win.close()
            core.quit()
            print('Testing session ended')
        
# Function to check whether 1 second passes after spacebar is pressed
def goto_next():
    global track_time, cancel_time
    if not track_time: #skip the loop if spacebar hasn't been pressed
        letsgo=0
    elif cancel_time>0: # if x has been pressed 
        if track_time[0] < cancel_time < (track_time[0]+1):
            track_time=list()
        letsgo=0
        cancel_time=0
    elif core.getTime() > track_time[0]+1: #if more than 1 sec has passed from spacebar press, go to next sequence
        letsgo=1
        if cue_idx<30:
            print("look-away criterion met. Press space to start sequence " + str(int((cue_idx+4)/2)))
        else: 
            print('END OF THE STUDY! Press the bar to close')
        background.draw()
        win.flip()
        track_time=list()
        event.waitKeys(keyList='space')
    else:
        letsgo=0
    return letsgo # o if we stay with same sequence, 1 if we need to go to next one
     
#Create a function that shows a stimulus and gets the timestamp
def show_stimulus(stimulus,location,duration,background):
    global track_time, cancel_time, letsgo, trigger
    if useEyetracker:
        trigger = 'start_'+str(stimulus[0].image[:-6]) #or maybe: str(stimulus[0].image)
    for i in stimulus:
        i.pos=location
        background.draw()
        i.draw()
        core.wait(duration)
        win.flip()
        get_bar() 
        letsgo=goto_next() #keep checking whether spacebar is pressed
        if letsgo==1:
            break
    if useEyetracker:
        trigger = 'end_' + str(stimulus[0].image[:-6])
    
        
#Create a function that shows background only
def show_background(background,duration):
    global track_time, cancel_time, letsgo
    isi_start=core.getTime()
    while isi_start > core.getTime()-duration:
        background.draw()
        win.flip()
        get_bar() 
        letsgo=goto_next() #keep checking whether spacebar is pressed
        if letsgo==1:
            break
        
# create a funtion for when the end is reached
def show_end():
    the_end=visual.TextStim(win, text='The End!', color=(0, 0, 0), height=100)
    the_end.draw()
    win.flip()
    core.wait(10)
        
##################### GUI ##############################################
Dlg = gui.Dlg(title="StatLearning")
Dlg.addField('Participant Number:')
Dlg.addText('(Choose a number between 1 and 1000)')
selection = Dlg.show()  # show dialog and wait for OK or Cancel
if Dlg.OK:                                            
    subjnum = float(selection[0])
else:
    core.quit()


print('_____________________________________________________________')
print('Testing is starting for participant %d' % subjnum)
core.wait(2)
print('_____________________________________________________________')
print('Press the space bar when infant looks away')
print('Press x to cancel if space bar is pressed by mistake')
print('Press space bar again to start a new sequence')
print('Press q to quit the testing session')
print('_____________________________________________________________')
#Prepare a gui for starting the study
DlgStart = gui.Dlg(title="Press OK to start")
# prepare gui for quitting the study
DlgQuit = gui.Dlg(title="Press OK to quit")


##################### Settings ##############################################         
# Set window size [x,y]
winsize = 1280,720#[1920/2,1080/2] #Screen from the Tobii

win = visual.Window(winsize, screen=1, fullscr=True, color=(1,1,1), units = 'pix') #monitor="testMonitor" 

# set the target locations, pseudorandomized depending on participant number (location is expressed in a complicated manner just to match exactly the old matlab script)
targ_loc=np.array([[-(winsize[0]*.8-(winsize[0]/2)), winsize[1]*.8-(winsize[1]/2)],
                   [winsize[0]*.8-(winsize[0]/2), winsize[1]*.8-(winsize[1]/2)],
                   [-(winsize[0]*.8-(winsize[0]/2)), -(winsize[1]*.8-(winsize[1]/2))],
                   [winsize[0]*.8-(winsize[0]/2), -(winsize[1]*.8-(winsize[1]/2))]])
if subjnum in list(range(1,1000,4)):
    targ_loc=np.array([targ_loc[3],targ_loc[0],targ_loc[2],targ_loc[1]])
elif subjnum in list(range(2,1000,4)):
    targ_loc=np.array([targ_loc[1],targ_loc[2],targ_loc[3],targ_loc[0]])
elif subjnum in list(range(3,1000,4)):
    targ_loc=np.array([targ_loc[0],targ_loc[3],targ_loc[1],targ_loc[2]])
elif subjnum in list(range(4,1000,4)):
    targ_loc=np.array([targ_loc[2],targ_loc[1],targ_loc[0],targ_loc[3]])
    
# Load sequences
sequences= pd.read_csv(Path + 'sequences_t.csv', header=None).transpose()
#Load music
music=1 #set to zero to turn music off
if music==1:
    prefs.general['audioLib'] = ['pygame']
    hothothot = sound.Sound(Path +"hothothot_long.wav", stereo=False)
   # Load images
stimuli=np.zeros([32],dtype=object)
n=-1
for foldername in os.listdir(Path + '\Stimuli\\'):
    n+=1
    this_stim=list()
    for filename in os.listdir(Path + '\Stimuli\\' + foldername):
        os.chdir(Path + '\Stimuli\\' + foldername)
        #heartTarget.append(filename)
        this_stim.append(visual.ImageStim(win, units= 'pix', size = [200*winsize[0]/1920,200*winsize[0]/1920], image = filename))
    stimuli[n]=this_stim
    percentage = (n+1)/32*100
    print('Loading %d' % percentage +'%')
#Load background image
os.chdir(Path)
background=visual.ImageStim(win, units= 'pix', size = winsize, image = 'background.jpg')
       
cue_idx=0 #list(range(0,16,2)) #target idx = cue_idx+1
cue_loc=[0,0]
cue_time=0.0188
targ_time=0.0118 #this is how long each frame is flipped on the screen. Change these to change cue and target time
timing_issue=0 # can change to 1 during the study if timing is off
#cue_time=0.018
#targ_time=0.0085

##################### HERE STARTS THE RECORDING! ############################
print('_____________________________________________________________')
print("Ready. Check DATA pc and Record video.\nThen press space to start.")
event.waitKeys(keyList='space')

if useEyetracker:
    output_file = Path +'\Data\subj'+str(int(subjnum)) + '.csv'
    eyetrackers[0].subscribe_to(tr.EYETRACKER_GAZE_DATA,gaze_data_callback, as_dictionary=True)


# Play the music
if music==1:
    hothothot.play()
    sound_time=core.getTime()
    
if useEyetracker:
    trigger = 'START_n.' + selection[0]

# 1.5 sec of blanck screen at the start
show_background(background,1.5)
# loop over every sequence
for col in sequences:
    print("Started!")
    print('_____________________________________________________________')
    trial_count=0
    for trial in sequences[col]:
        # count trials
        trial_count+=1
        x= core.getTime() #uncomment if you want to check timing
        show_stimulus(stimuli[cue_idx],cue_loc,cue_time,background) #show cue
        print('c '+ str(core.getTime()-x)) #uncomment if you want to check timing
        
        if letsgo==1: # if infant looked away for 1 second
            letsgo=0
            break # stop the sequence
        
        # add ISI
        show_background(background,.75)
        if letsgo==1:
            letsgo=0
            break    
        
        
        this_targ_loc=targ_loc[trial-1]
        x= core.getTime() #uncomment if you want to check timing
        show_stimulus(stimuli[cue_idx+1],this_targ_loc,targ_time,background) #show target
        x=core.getTime()-x #uncomment if you want to check timing
        print('t ' + str(x)) #uncomment if you want to check timing
        if x<1.4 or x>1.6:
            timing_issue=1
            
        if letsgo==1:
            letsgo=0
            break
        
        # add ITI
        show_background(background,.75)
        if letsgo==1:
            letsgo=0
            break 
        
    if trial_count==15:
        if cue_idx<30:
            print('Sequence has ended. Press the bar to start next one')
        else:
            print('END OF THE STUDY! Press the bar to close')
        event.waitKeys(keyList='space')
    cue_idx+=2
        
     
#Stop Eyetracker
if useEyetracker:
    eyetrackers[0].unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    #CV_Stop()
    #CV_Close() 
        

hothothot.stop()
show_end()  


win.close()
core.quit()
print('Testing session ended')

if timing_issue==1:
    print('ATTENTION: there might be a timing issue. Contact Francesco!')