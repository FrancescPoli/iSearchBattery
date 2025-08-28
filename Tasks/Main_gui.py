
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

################## Pop-up window to choose participant and task ########################

GUI_off = False
while GUI_off == False:
    myDlg = gui.Dlg(title="CEAL_Battery")
    #myDlg.addText('Subject info')
    myDlg.addField('Participant ID (Choose a number between 1 and 1000):')
    #myDlg.addText('Task Info')
    myDlg.addField('Task:', choices=["Doors", "Torchlight", "Planko", "InformationGain", "ActiveLearning", "Uncertainty", "PEM"])
    #myDlg.addText('Calibration Info')
    myDlg.addField('Calibration:', choices=["Yes", "No"])
    ok_data = myDlg.show()

    if myDlg.OK:
        try:
            Subject = int(ok_data[0])
            if 0 <= Subject <= 1000:
                Task = ok_data[1]
                Calibration = ok_data[2]
                GUI_off = True
            else:
                print('Select a number from 0 to 1000')

        except ValueError:
            print('Subject ID must be a number from 0 to 1000')

    else:
        print('You pressed Cancel!!\nI will close down!!!!!')
        GUI_off = True
        core.quit()


#################### Run the selected task script ########################

# Map task names to their folder and module names
task_paths = {
    "Doors": ("Doors", "Run_Doors"),
    "Torchlight": ("Torchlight", "Run_Torchlight"),
    "Planko": ("Planko", "Run_Planko"),
    "InformationGain": ("InformationGain", "Run_InformationGain"),
    "ActiveLearning": ("ActiveLearning", "Run_ActiveLearning"),
    "Uncertainty": ("Uncertainty", "Run_Uncertainty"),
    # If PEM has its own folder, add here:
    "PEM": ("PEM", "Run_PEM")
}

#if Calibration == "Yes":
#    os.chdir(r"C:\Users\itali\Documents\iSearchBattery\Tasks\psychopy_tobii_infant\\")
    # import Psychopy tobii infant
#    from psychopy_tobii_infant import TobiiInfantController

#    winsize = [1280, 720]
#    win = visual.Window(winsize, fullscr=True, allowGUI=False,screen = 1, color = "#a6a6a6", unit='pix')

    # visual stimuli
#    CALISTIMS = glob.glob("CalibrationStim\\*.png")

    # video
#    VideoGrabber = visual.MovieStim(win, "CalibrationStim\\Attentiongrabber.mp4", loop=True, size=[800,450],volume =0.4, unit = 'pix')  

    # sound
#    Sound = sound.Sound(directory + "CalibrationStim\\audio.wav")

#    EyeTracker = TobiiInfantController(win)


try:
    folder_name, module_name = task_paths[Task] 

    # Add the folder to sys.path if not already
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    if folder_path not in sys.path:
        sys.path.append(folder_path)

    # Import the task module
    task_module = importlib.import_module(module_name)

    # If the task has a run() function, call it
    if hasattr(task_module, 'run'):
        task_module.run(Subject=Subject, Calibration=Calibration)

except Exception as e:
    print(f"Error loading or running the task module '{Task}': {e}")
    core.quit()
    
