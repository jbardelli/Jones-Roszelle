# print(- coding: utf-8 -*-
"""
Created on Sun Apr 23 20:35:54 2017

@author: jbardelli
"""

import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import minimize
import PySimpleGUI as sg
from styleframe import StyleFrame, Styler, utils
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import JR_calculations as jr # Custom module with the calculations for Jones-Roszelle method

# # --- GUI FUNCTIONS ---

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

#--- Clears or plots the relative permeability curves ---

def plot_kr (figure, fig_, axis, Sw2, kro, krw, Swi, Swf, switch):
    figure.get_tk_widget().forget()
    if switch == True:
        axis.set_xlabel('Sw')
        axis.set_ylabel('Kr')
        axis.scatter(Sw2, krw,c='b', s=12)
        axis.scatter(Sw2, kro,c='r', s=12)
        axis.plot([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
        axis.plot([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
    else:
        axis.clear()
        ax1.set_xticks(np.arange(0,101,10))
    axis.set_yticks(np.arange(0,1.1,0.1))
    axis.set_xlim(0,100)
    axis.set_ylim(0,1)
    axis.grid(True)
    figure = draw_figure(window['-CANVAS-'].TKCanvas, fig_)
    return   figure

#---------------------------------
#--- TEST DATA Variables ---
Swi=Vp=uw=uo=L=D=ko_Swi=q=0.0
degree=2
file = " "

# # --- Beginning of GUI CODE ---
# Define plot
plt.ioff()  
plt.figure()
fig=plt.gcf()
fig,ax1 = plt.subplots()


# define the main window layout
layout_main = [[sg.Text('Plot test')],
              [sg.Canvas(key='-CANVAS-')],
              [sg.Button('Settings'),sg.Button('Clear'),sg.Button('Close'),sg.Button('Calculate')]]


# create the form and show it without the plot
window = sg.Window('Jones-Roszelle', layout_main, finalize=True, element_justification='center', font=("Bahnschrift", 11))

# add the plot to the window
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

while(True):

    event, values = window.read()
    print(values)
     
    if event == "Close" or event == sg.WIN_CLOSED:
        break
    if event == "Settings":
        #--- Open Settings Window ---
        layout_settings = [[sg.Text('Data File:',size=(20,1)),sg.InputText(file,size=(40,1),key='-FILE-'),sg.FileBrowse()],
                           [sg.Text('Longitude[cm]:',size=(20,1)),sg.InputText(str(L),size=(10,1),key='-L-')],
                           [sg.Text('Diameter[cm]:',size=(20,1)),sg.InputText(str(D),size=(10,1),key='-D-')],
                           [sg.Text('Pore Volume[cm3]:',size=(20,1)),sg.InputText(str(Vp),size=(10,1),key='-PV-')],
                           [sg.Text('Swi[%]:',size=(20,1)),sg.InputText(str(Swi),size=(10,1),key='-SWI-')],
                           [sg.Text('Oil Viscosity[cP]:',size=(20,1)),sg.InputText(str(uo),size=(10,1),key='-UO-')],
                           [sg.Text('Water Viscosity[cP]:',size=(20,1)),sg.InputText(str(uw),size=(10,1),key='-UW-')],
                           [sg.Text('Flow Rate[ml/h]:',size=(20,1)),sg.InputText(str(q),size=(10,1),key='-RATE-')],
                           [sg.Text('Ko@Swi[mD]:',size=(20,1)),sg.InputText(str(ko_Swi),size=(10,1),key='-KOSWI-')],
                           [sg.Text('Polinomial degree:',size=(20,1)),sg.InputText(str(degree),size=(10,1),key='-DEGREE-')],
                           [sg.Button('Done')]]
        window_set = sg.Window('Test Settings', layout_settings, finalize=True, element_justification='left', font=("Bahnschrift", 11))
         
        while(True):                                                # Wait for events
            event_set, values_set = window_set.read()
            window_set['-FILE-'].update(values_set['Browse'])       # Update the box with the browsed file name
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
                window_set.close()
                break
            if event == sg.WINDOW_CLOSED:                           #If window was closed do nothing, ignore entries
                window_set.close()
                break
    if event == "Calculate":
        results=jr.calc_kr(Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, file)                              #Calculate Kr curves
        Qi, Avg_Sw, Swm_calc, lambda2, kro, krw, kro_fit, krw_fit, Sw2, Sor, Swf, kro_Swi, krw_Sor = results
        fig_canvas_agg = plot_kr(fig_canvas_agg, fig, ax1, Sw2, kro_fit, krw_fit, Swi, Swf, True)       #Plot Kr curves

    if event == "Clear":
        fig_canvas_agg = plot_kr(fig_canvas_agg, fig, ax1, Sw2, kro_fit, krw_fit, Swi, Swf, False)      #Clear all plots
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
  
