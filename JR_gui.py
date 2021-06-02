# -*- coding: utf-8 -*-
"""
Created on Tue May 18 09:32:50 2021

@author: jbardelli
"""
import PySimpleGUI as sg
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from os import path

# # --- GUI FUNCTIONS ---

def draw_figure(canvas, figure):                                    # Draws a figure in the window canvas
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def save_window (file, folder):                                     # Dialog window used to save results to a file
    layout_save = [[sg.Text('Destination Folder',size=(13,1)), sg.InputText(folder,size=(40,1),key='-FOLDER-'), sg.FolderBrowse()],
                   [sg.Text('File Name', size=(13,1)), sg.InputText(file,size=(40,1),key='-FILE-')],
                   [sg.Button('Save'), sg.Button('Cancel')]]
    return sg.Window('Save Results', layout_save, finalize=True, element_justification='left', font=("Arial", 10))

def settings_window (file, L, D, Vp, Swi, uo, uw, q, ko_Swi, degree):
    # define the settings window layout
    layout_settings = [[sg.Text('Data File:',size=(15,1)),sg.InputText(file,size=(40,1),key='-FILE-'),sg.FileBrowse()],
                   [sg.Text('Longitude[cm]:',size=(15,1)),sg.InputText(str(L),size=(10,1),key='-L-')],
                   [sg.Text('Diameter[cm]:',size=(15,1)),sg.InputText(str(D),size=(10,1),key='-D-')],
                   [sg.Text('Pore Volume[cm3]:',size=(15,1)),sg.InputText(str(Vp),size=(10,1),key='-PV-')],
                   [sg.Text('Swi[%]:',size=(15,1)),sg.InputText(str(Swi),size=(10,1),key='-SWI-')],
                   [sg.Text('Oil Viscosity[cP]:',size=(15,1)),sg.InputText(str(uo),size=(10,1),key='-UO-')],
                   [sg.Text('Water Viscosity[cP]:',size=(15,1)),sg.InputText(str(uw),size=(10,1),key='-UW-')],
                   [sg.Text('Flow Rate[ml/h]:',size=(15,1)),sg.InputText(str(q),size=(10,1),key='-RATE-')],
                   [sg.Text('Ko@Swi[mD]:',size=(15,1)),sg.InputText(str(ko_Swi),size=(10,1),key='-KOSWI-')],
                   [sg.Text('Polinomial degree:',size=(15,1)),sg.Combo(['1','2','3'],default_value=str(degree), key='-DEGREE-')],
                   # [sg.Text('Polinomial degree:',size=(15,1)),sg.InputText(str(degree),size=(10,1),key='-DEGREE-')],
                   [sg.Button('Done')]]
    return sg.Window('Test Settings', layout_settings, finalize=True, element_justification='left', font=("Arial", 10))

def table_window (Wi, Np, deltaP, Use, fig_ex, degree):             # Shows table window and populates table with experiment data
    MAX_ROWS = 20
    MAX_COL = 3
    
    columm_layout =  [[sg.Text(str(i), size=(4, 1), justification='right')] + [sg.Input(size=(11, 1), pad=(1,1),border_width=0, justification='right', enable_events=True, key=(i, j)) for j in range(MAX_COL)] + [sg.Checkbox('', default=True, enable_events=True, key=(i,3))] for i in range(MAX_ROWS)]
    
    layout_table = [[sg.Text(' ',size=(4,1)),sg.Text('Wi [ml]',size=(9,1)), sg.Text('Np [ml]',size=(9,1)), sg.Text('deltaP [psi]',size=(9,1))],
                    [sg.Col(columm_layout, scrollable=False,)]]
 
    layout_plot = [[sg.Canvas(key='-EX-')],
                   [sg.Button('Use Table'),sg.Button('Use Fit'),sg.Button('Read from File'),sg.Text('Polynomic Degree'),sg.Combo(['1','2','3','4','5','6'],default_value=str(degree), key='-DEG-', enable_events=True)]]
   
    layout = [[sg.Frame('Table', layout_table), sg.Frame('Plot', layout_plot)]]    
        
    window = sg.Window('Experimental Data',layout, finalize=True, element_justification='left', font=("Arial", 10))
    fig_canvas_agg_ex = draw_figure(window['-EX-'].TKCanvas, fig_ex)
    populate_table (window, Wi, Np, deltaP, Use)
    
    return window, fig_canvas_agg_ex

def populate_table (window, Wi, Np, deltaP, Use):                   # Populates the table with data expressed as np.array
    print(Wi, Np, deltaP, Use)
    data = np.column_stack((Wi, Np, deltaP, Use))
    
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            location = (i, j)
            try:            # try the best we can at reading and filling the table
                target_element = window[location]
                new_value = np.round_(item, 2)
                if target_element is not None and new_value != '':
                    target_element.update(new_value)
            except:
                pass
    return

def extract_values(table, Wi, Np, deltaP, Use):                     # Gets the values from the table and forms arrays
    data = np.column_stack((Wi,Np, deltaP, Use))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
                data[i][j]=table[(i,j)]
    Wi=data[:,0]
    Np=data[:,1]
    deltaP=data[:,2]
    Use=data[:,3]
    return Wi, Np, deltaP, Use

def input_error (message):                                          # Show a window with the specified message return window descriptor
    layout = [[sg.Text(message)],
              [sg.Button('OK')]]
    window = sg.Window('ERROR',layout, finalize=False, element_justification='center', font=("Arial", 10))
    return window

def calc_input_validation (Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, Wi, Np, deltaP, Use):      # Validates all the parameters and tables to avoid errors in the calculations
    Wi = Wi[(Use == True)] 
    Np = Np[(Use == True)] 
    deltaP = deltaP[(Use == True)] 
    if Vp == 0 or Swi == 0 or q == 0 or L == 0 or D == 0 or uo == 0 or uw == 0 or ko_Swi == 0 or degree == 0 or np.any(Np==0) or np.any(Wi==0) or np.any(deltaP==0):
        window = input_error ('One or more values are zero \nCheck Settings and Table')
        while True:
            event, values = window.read()
            if event == 'OK':
                window.close()
                break
        return False
    else:
        return True

def table_input_validation (Wi, Np, deltaP):                        # Validates the data in the Table window (experimental data cannot be all zero)
    if np.all(Np==0) or np.all(Wi==0) or np.all(deltaP==0):
        window = input_error ('All values are zero in one or more data arrays \nCheck Settings File')
        while True:
            event, values = window.read()
            if event == 'OK':
                window.close()
                break
        return False
    else:
        return True

def file_open_check (file_n):                                       # Checks if target file is open
    try:
        myfile = open (file_n, "r+")
        myfile.close()
        return False   
    except IOError:    
        window = input_error ('File is already open')               # Show error if file already open
        event, values = window.read()
        if event == 'OK':
            window.close()
            return True

def file_exists_check (file_n):                                     # Checks if target file exists, returns TRUE (open or non existent) and FALSE (closed or Overwrite)
    layout = [[sg.Text('File already exists, overwrite?')],
              [sg.Button('YES'), sg.Button('NO')]]
    
    if path.isfile(file_n):                                         # Check if file exists
        window = sg.Window('WARNING',layout, finalize=False, element_justification='center', font=("Arial", 10))
        event, values = window.read()
        if event == 'YES':                                          # If it exists, ask if Overwrite or not
            if file_open_check(file_n):                             # If user chooses overwrite, then check if file is open
                window.close()
                return False                                        # If file is not open, return False
            else: 
                window.close()
                return True                                         # If file is open, return True
        if event == 'NO':                                           # If user choses not to overwrite, return False
            window.close()
            return False
    else:
        return True                                                 # If file does not exists return True

def populate_results (window, Swi, Sor, krw_Sor, ko_Swi, degree):   # Populates results on the right side of the main window
    window['-SWI-'].update(np.round(Swi,1))                         # Results are populated after the rel. perm calculation
    window['-SOR-'].update(np.round(Sor,1))
    window['-KRW-'].update(np.round(krw_Sor,3))
    window['-KRO-'].update(np.round(1,3))
    window['-KW-'].update(float('%.3g' %(krw_Sor*ko_Swi)))
    window['-KO-'].update(float('%.3g' %ko_Swi))
    window['-POLDEG-'].update(degree)
    return