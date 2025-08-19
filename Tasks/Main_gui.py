
from psychopy import visual, core, event, sound, gui, prefs
import importlib
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
    myDlg.addText('Subject info')
    myDlg.addField('ID (Choose a number between 1 and 1000):')
    myDlg.addText('Task Info')
    myDlg.addField('Task:',choices=["Doors", "Torchlight", "Planko", "LearningProgress", "ALM", "Uncertainty", 'PEM'])
    myDlg.addText('Calibration Info')
    myDlg.addField('Calibration:',choices=["Yes", "No"])
    ok_data = myDlg.show() # show dialog and wait for OK or Cancel


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
        



#################### Run the selected task script ########################

# Map task names to script module names (case-insensitive)
task_modules = {
    "Doors": "doors",
    "Torchlight": "torchlight",
    "Planko": "planko",
    "LearningProgress": "learningprogress",
    "ALM": "alm",
    "Uncertainty": "uncertainty"
    "PEM": "PEM"
}

try:
    task_module_name = task_modules[Task]
    task_module = importlib.import_module(task_module_name)
    # Optional: if the module uses a `run()` function, you can do:
    if hasattr(task_module, 'run'):
        task_module.run(Subject=Subject, Calibration=Calibration)
except Exception as e:
    print(f"Error loading or running the task module '{Task}': {e}")
    core.quit()
    
