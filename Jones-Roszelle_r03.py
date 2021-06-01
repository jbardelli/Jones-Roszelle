# print(- coding: utf-8 -*-
"""
Created on Sun Apr 23 20:35:54 2017
@author: jbardelli
"""

import numpy as np
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import JR_calculations as jr # Custom module with the calculations for Jones-Roszelle method
import JR_gui as gui         # Custom module for windows layouts and functions
import JR_plots as plots     # Custom module for varios types of predefined plots used in the main window
import JR_save as jrsave     # Custom module for saving results to Excel file
from os import path

#---------------------------------
#--- Variables ---
Wi=Np=deltaP=Swi=Sor=Vp=uw=uo=L=D=ko_Swi=krw_Sor=q=data=0.0
Use=True
degree = 2
data_file       = ""
report_folder   = ""
report_file     = ""

# # --- Beginning of GUI CODE ---
# Define plots
plt.ioff()  
fig_kr, ax1 = plt.subplots()
fig_fw, ax2 = plt.subplots()
fig_np, ax3 = plt.subplots()
fig_dp, ax4 = plt.subplots() 
fig_ex, bx1 = plt.subplots()
bx2 = bx1.twinx()
   
# define the main window layout
column_layout = [[sg.Text('Swi (%) =', size=(15,1)), sg.Text(Swi, key='-SWI-',size=(10,1))],
                 [sg.Text('Sro (%) =', size=(15,1)), sg.Text(Sor, key='-SOR-',size=(10,1))],
                 [sg.Text('Krw@Sor =', size=(15,1)), sg.Text(krw_Sor, key='-KRW-',size=(10,1))],
                 [sg.Text('Kro@Swi =', size=(15,1)), sg.Text(str(1) , key='-KRO-',size=(10,1))],
                 [sg.Text('Kw@Sor (mD) =', size=(15,1)), sg.Text(krw_Sor*ko_Swi, key='-KW-',size=(10,1))],
                 [sg.Text('Ko@Swi (mD) =', size=(15,1)), sg.Text(ko_Swi, key='-KO-',size=(10,1))],
                 [sg.Text('Pol. degree =', size=(15,1)), sg.Text(degree, key='-POLDEG-',size=(10,1))]]
                 
layout_main = [[sg.Text('Jones-Roszelle Relative Permeability')],
              [sg.Canvas(key='-NP-'),sg.Canvas(key='-KR-'),sg.Column(column_layout)],
              [sg.Canvas(key='-DP-'),sg.Canvas(key='-FW-'),sg.Text('', size=(28,1))],
              [sg.Button('Settings'),sg.Button('Table'),sg.Button('Clear'),sg.Button('Close'),sg.Button('Calculate'),sg.Button('Save Results')]]

# create the form and show it without the plot
window = sg.Window('Jones-Roszelle', layout_main, finalize=True, element_justification='center', font=("Arial", 10), location=(0,0))

# add the plots to the windows
fig_canvas_agg_np = gui.draw_figure(window['-NP-'].TKCanvas, fig_np)
fig_canvas_agg_dp = gui.draw_figure(window['-DP-'].TKCanvas, fig_dp)
fig_canvas_agg_kr = gui.draw_figure(window['-KR-'].TKCanvas, fig_kr)
fig_canvas_agg_fw = gui.draw_figure(window['-FW-'].TKCanvas, fig_fw)
fit_degree = 2

while(True):
    event, values = window.read()
    print(values)
     
    if event == "Close" or event == sg.WIN_CLOSED:                  # Close the Main window
        break
    
    if event == "Settings":                                         # Settings Button pressed (opens wdw to set the data_file and all the experiment parameters)
        #--- Open Settings Window ---
        window_set = gui.settings_window(data_file, L, D, Vp, Swi, uo, uw, q, ko_Swi, degree)     
        while(True):                                                # Wait for events
            event_set, values_set = window_set.read()
            if event_set == "Done":                                 #If Done was pressed update all the variables
                print(values_set)
                data_file = values_set['-FILE-']
                L = float(values_set['-L-'])
                D = float(values_set['-D-'])
                Vp = float(values_set['-PV-'])
                Swi = float(values_set['-SWI-'])
                uo = float(values_set['-UO-'])
                uw = float(values_set['-UW-'])
                q = float(values_set['-RATE-'])
                ko_Swi = float(values_set['-KOSWI-'])
                degree = int(values_set['-DEGREE-'])
                if path.isfile(data_file): Wi, Np, deltaP, Use = Wio, Npo, dPo, Use = jr.get_data_table (data_file)
                window_set.close()
                break
            if event_set == sg.WIN_CLOSED:                              # If window was closed do nothing, ignore entries
                window_set.close()
                break
            else: 
                window_set['-FILE-'].update(values_set['Browse'])       # Update the box with the browsed file name
    
    if event == "Table":                                                # Table Button pressed (Opens table to review or modify experimental data)
        if gui.table_input_validation (Wi, Np, deltaP):
            window_table, fig_canvas_agg_ex = gui.table_window (Wi, Np, deltaP, Use, fig_ex, fit_degree)
            while (True):
                fig_canvas_agg_ex, fit_np, fit_dp = plots.plot_exp (window_table, fig_canvas_agg_ex, fig_ex, bx1, bx2, Wi, Np, deltaP, fit_degree, Use)
                event_table, values_table = window_table.read()            
                if event_table == "Use Table" or event_table == sg.WIN_CLOSED:
                    window_table.close()
                    break
                else: 
                    fit_degree = int(values_table['-DEG-'])
                    Wi, Np, deltaP, Use = gui.extract_values(values_table, Wi, Np, deltaP, Use)
                if event_table == "Use Fit":
                    Wi = Wi[(Use == True)] 
                    Use = np.ones(Wi.size, dtype=bool)
                    Np = np.round_(fit_np, 2)
                    deltaP = np.round_(fit_dp, 2)
                    window_table.close()
                    break
                if event_table == "Read from File":
                    Wi, Np, deltaP, Use = Wio, Npo, dPo, Use = jr.get_data_table (data_file)
                    gui.populate_table (window_table, Wi, Np, deltaP, Use)
            
    if event == "Calculate":                                        # Calculate Button pressed
        if gui.calc_input_validation (Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, Wi, Np, deltaP, Use):
            results=jr.calc_kr(Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, Wi, Np, deltaP, Use)  # Calculate Kr curves
            Qi, Avg_Sw, Swm_calc, lambda2, kro, krw, kro_fit, krw_fit, Sw2, Sor, Swf, kro_Swi, krw_Sor, fw = results
            fig_canvas_agg_kr = plots.plot_kr(window, fig_canvas_agg_kr, fig_kr, ax1, Sw2, kro, krw, Swi, Swf, True)        #Plot Kr curves
            fig_canvas_agg_fw = plots.plot_fw(window, fig_canvas_agg_fw, fig_fw, ax2, Sw2, fw, Swi, Swf, True)              #Plot fw curve
            fig_canvas_agg_np = plots.plot_np(window, fig_canvas_agg_np, fig_np, ax3, Qi, Avg_Sw, Swm_calc, True)           #Plot fw curve
            fig_canvas_agg_dp = plots.plot_dp(window, fig_canvas_agg_dp, fig_dp, ax4, Qi, lambda2, True)                    #Plot lambda2 curve  
            gui.populate_results(window, Swi, Sor, krw_Sor, ko_Swi, degree)
            
    if event == "Clear":                                            # Clear Button pressed
        fig_canvas_agg_kr = plots.plot_kr(window, fig_canvas_agg_kr, fig_kr, ax1, Sw2, kro_fit, krw_fit, Swi, Swf, False)     #Clear all plots
        fig_canvas_agg_fw = plots.plot_fw(window, fig_canvas_agg_fw, fig_fw, ax2, Sw2, fw, Swi, Swf, False)                   #Clear all plots
        fig_canvas_agg_np = plots.plot_np(window, fig_canvas_agg_np, fig_np, ax3, Qi, Avg_Sw, Swm_calc, False)                #Clear all plots
        fig_canvas_agg_dp = plots.plot_dp(window, fig_canvas_agg_dp, fig_dp, ax4, Qi, lambda2, False)                         #Clear all plots
    
    if event == "Save Results":                                     # Save Results Button pressed
        if Sor==0 or krw_Sor==0 or not path.isfile(data_file):      # Check if there are results to be saved or if the data file exists (it's needed to get original values)
            window_err = gui.input_error('No results to save or data file is non existent')
            while True:                                             # Show error and wait for OK button
                event, values = window_err.read()
                if event == 'OK':
                    window_err.close()
                    break
        else:                                                       # if there are results and data file, the open the save dialog window
            window_save = gui.save_window(report_file, report_folder)
            while True:
                event_save, values_save = window_save.read()
                if event_save == "Cancel" or event_save == sg.WIN_CLOSED:
                    window_save.close()
                    break
                if event_save == "Save":                            # If Save is pressed, get original values from data_file             
                    Wiexp, Npexp, deltaPexp, Use = Wio, Npo, dPo, Use = jr.get_data_table (data_file)
                    report_path = values_save['-FOLDER-'] + '/' + values_save['-FILE-'] + '.xls'    # Format the complete report file PATH
                    if gui.file_exists_check(report_path):                      # If file does not exists, then save
                        print('Saving to ', report_path)
                        jrsave.save_to_file(report_path, Swi, L, D, Vp, uo, uw, q, ko_Swi, Sor, Swf, krw_Sor, Wi, Np, deltaP, Sw2, kro, krw, Wiexp, Npexp, deltaPexp, degree)     
                        window_save.close()
                        break
                    else:
                        print('File exists or already open...')
window.close()

