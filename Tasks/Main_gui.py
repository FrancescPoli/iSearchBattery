from psychopy import core, gui 

################## Pop-up window to choose participant and task ########################

GUI_off = False
while GUI_off == False:
    myDlg = gui.Dlg(title="CEAL_Battery")
    myDlg.addText('Subject info')
    myDlg.addField('ID (Choose a number between 1 and 1000):')
    myDlg.addText('Task Info')
    myDlg.addField('Task:',choices=["Doors", "Torchlight", "Planko", "LearningProgress", "ALM", "Uncertainty"])
    myDlg.addText('Calibration Info')
    myDlg.addField('Calibration:',choices=["Yes", "No"])
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    
    
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
            print('Subject ID must be a number')
    else:
        print('You pressed Cancel!!\nI will close down!!!!!')
        GUI_off = True
        core.quit()