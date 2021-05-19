# -*- coding: utf-8 -*-
"""
Created on Tue May 18 09:32:50 2021

@author: jbardelli
"""
import PySimpleGUI as sg
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# # --- GUI FUNCTIONS ---

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

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
                   [sg.Text('Polinomial degree:',size=(15,1)),sg.InputText(str(degree),size=(10,1),key='-DEGREE-')],
                   [sg.Button('Done')]]
    return sg.Window('Test Settings', layout_settings, finalize=True, element_justification='left', font=("Arial", 10))

def table_window (Wi, Np, deltaP):
    data = np.column_stack((Wi,Np, deltaP))
    MAX_ROWS = 20
    MAX_COL = 3
    
    columm_layout =  [[sg.Text(str(i), size=(4, 1), justification='right')] + [sg.InputText(size=(11, 1), pad=(1,1),border_width=0, justification='right', key=(i, j)) for j in range(MAX_COL)] for i in range(MAX_ROWS)]
    
    layout_table = [[sg.Text(' ',size=(4,1)),sg.Text('Wi [ml]',size=(9,1)), sg.Text('Np [ml]',size=(9,1)), sg.Text('deltaP [psi]',size=(9,1))],
                    [sg.Col(columm_layout, scrollable=False,)],
                    [sg.Button('Done')]]
    
    window = sg.Window('Experimental Data',layout_table, finalize=True, element_justification='left', font=("Arial", 10))
    
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            location = (i, j)
            try:            # try the best we can at reading and filling the table
                target_element = window[location]
                new_value = item
                if target_element is not None and new_value != '':
                    target_element.update(new_value)
            except:
                pass
    
    return window

def extract_values(table, Wi, Np, deltaP):
    data = np.column_stack((Wi,Np, deltaP))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
                data[i][j]=table[(i,j)]
        Wi=data[:,0]
        Np=data[:,1]
        deltaP=data[:,2]
    return Wi, Np, deltaP