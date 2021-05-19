# print(- coding: utf-8 -*-
"""
Created on Sun Apr 23 20:35:54 2017
@author: jbardelli
"""

import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
import PySimpleGUI as sg
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import JR_calculations as jr # Custom module with the calculations for Jones-Roszelle method
import JR_gui as gui         # Custom module for windows layouts and functions
import JR_plots as plots     # Custom module for varios types of predefined plots used in the main window

#---------------------------------
#--- TEST DATA Variables ---
Swi=Vp=uw=uo=L=D=ko_Swi=q=data=0.0
degree=2
file = " "

# # --- Beginning of GUI CODE ---
# Define plot
plt.ioff()  
fig_kr,ax1 = plt.subplots()
fig_fw,ax2 = plt.subplots()
fig_np,ax3 = plt.subplots()
fig_dp,ax4 = plt.subplots() 

# define the main window layout
layout_main = [[sg.Text('Jones-Roszelle Relative Permeability')],
              [sg.Canvas(key='-NP-'),sg.Canvas(key='-KR-')],
              [sg.Canvas(key='-DP-'),sg.Canvas(key='-FW-')],
              [sg.Button('Settings'),sg.Button('Clear'),sg.Button('Close'),sg.Button('Table'),sg.Button('Calculate')]]

# create the form and show it without the plot
window = sg.Window('Jones-Roszelle', layout_main, finalize=True, element_justification='center', font=("Arial", 10), location=(0,0))

# add the plots to the window
fig_canvas_agg_np = gui.draw_figure(window['-NP-'].TKCanvas, fig_np)
fig_canvas_agg_dp = gui.draw_figure(window['-DP-'].TKCanvas, fig_dp)
fig_canvas_agg_kr = gui.draw_figure(window['-KR-'].TKCanvas, fig_kr)
fig_canvas_agg_fw = gui.draw_figure(window['-FW-'].TKCanvas, fig_fw)

while(True):
    event, values = window.read()
    print(values)
     
    if event == "Close" or event == sg.WIN_CLOSED:
        break
    
    if event == "Settings":
        #--- Open Settings Window ---
        window_set = gui.settings_window(file, L, D, Vp, Swi, uo, uw, q, ko_Swi, degree)     
        while(True):                                                # Wait for events
            event_set, values_set = window_set.read()
            if event_set == "Done":                                 #If Done was pressed update all the variables
                print(values_set)
                file = values_set['-FILE-']
                L = float(values_set['-L-'])
                D = float(values_set['-D-'])
                Vp = float(values_set['-PV-'])
                Swi = float(values_set['-SWI-'])
                uo = float(values_set['-UO-'])
                uw = float(values_set['-UW-'])
                q = float(values_set['-RATE-'])
                ko_Swi = float(values_set['-KOSWI-'])
                degree = int(values_set['-DEGREE-'])
                Wi, Np, deltaP = Wio, Npo, dPo = jr.get_data_table (file)   
                window_set.close()
                break
            if event_set == sg.WIN_CLOSED:                              # If window was closed do nothing, ignore entries
                window_set.close()
                break
            else: 
                window_set['-FILE-'].update(values_set['Browse'])       # Update the box with the browsed file name
    
    if event == "Table":
        window_table = gui.table_window (Wi, Np, deltaP)
        while (True):
            event_table, values_table = window_table.read()
            if event_table == "Done" or event_table == sg.WIN_CLOSED:
                Wi, Np, deltaP = gui.extract_values(values_table, Wi, Np, deltaP)
                window_table.close()
                break
    
    if event == "Calculate":
        results=jr.calc_kr(Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, Wi, Np, deltaP)  # Calculate Kr curves
        Qi, Avg_Sw, Swm_calc, lambda2, kro, krw, kro_fit, krw_fit, Sw2, Sor, Swf, kro_Swi, krw_Sor, fw = results
        fig_canvas_agg_kr = plots.plot_kr(window, fig_canvas_agg_kr, fig_kr, ax1, Sw2, kro_fit, krw_fit, Swi, Swf, True)      #Plot Kr curves
        fig_canvas_agg_fw = plots.plot_fw(window, fig_canvas_agg_fw, fig_fw, ax2, Sw2, fw, Swi, Swf, True)                    #Plot fw curve
        fig_canvas_agg_np = plots.plot_np(window, fig_canvas_agg_np, fig_np, ax3, Qi, Avg_Sw, Swm_calc, True)                 #Plot fw curve
        fig_canvas_agg_dp = plots.plot_dp(window, fig_canvas_agg_dp, fig_dp, ax4, Qi, lambda2, True)                          #Plot lambda2 curve 
    if event == "Clear":
        fig_canvas_agg_kr = plots.plot_kr(window, fig_canvas_agg_kr, fig_kr, ax1, Sw2, kro_fit, krw_fit, Swi, Swf, False)     #Clear all plots
        fig_canvas_agg_fw = plots.plot_fw(window, fig_canvas_agg_fw, fig_fw, ax2, Sw2, fw, Swi, Swf, False)                   #Clear all plots
        fig_canvas_agg_np = plots.plot_np(window, fig_canvas_agg_np, fig_np, ax3, Qi, Avg_Sw, Swm_calc, False)                #Clear all plots
        fig_canvas_agg_dp = plots.plot_dp(window, fig_canvas_agg_dp, fig_dp, ax4, Qi, lambda2, False)                         #Clear all plots

window.close()

# #--- WRITE TO EXCEL FILE ---
# writer = pd.ExcelWriter("test_KR.xlsx",engine="xlsxwriter" )
# workbook = writer.book
# worksheet = workbook.add_worksheet('KR')
# writer.sheets['KR'] = worksheet
# sat_format = workbook.add_format()
# sat_format.set_num_format('0.0')
# kr_format = workbook.add_format()
# kr_format.set_num_format('0.000')
# worksheet.write('A1','--TEST DATA--')
# worksheet.write('A2','Swi[%]')
# worksheet.write('B2', Swi, sat_format)
# worksheet.write('A3','VP[cm3]')
# worksheet.write('B3',Vp)
# worksheet.write('A4','uo[cP]')
# worksheet.write('B4',uo)
# worksheet.write('A4','uw[cP]')
# worksheet.write('B4',uw)
# worksheet.write('A4','q[cm3/h]')
# worksheet.write('B4',q)
# worksheet.write('A5','--RESULTS--')
# worksheet.write('A6','Sor[%]')
# worksheet.write('B6', Sor ,sat_format)
# worksheet.write('A7','Swf[%]')
# worksheet.write('B7', Swf, sat_format)
# worksheet.write('A8','Krw@Sor')
# worksheet.write('B8', krw_Sor, kr_format)

# df.to_excel(writer, sheet_name='KR', startrow=10, startcol=0)

# worksheet = writer.book.add_worksheet('KR LET')
# writer.sheets['KR LET'] = worksheet
# worksheet.write(0,0,"LET RELATIVE PERMEABILITY TABLE")
# df_let.to_excel(writer, sheet_name='KR LET', startrow=4, startcol=0)
# writer.save()  
  
