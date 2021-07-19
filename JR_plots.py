# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:10:23 2021

@author: jbardelli
"""
import numpy as np
import JR_gui as gui         # Custom module for windows layouts and functions

#--- PLOT FUNCTIONS ---
def plot_np (window, figure, fig_, axis, Qi, Avg_Sw, Swm, switch):                      # Plot the average sw with calculated sw
    figure.get_tk_widget().forget()
    if switch == True:
        axis.set_xlabel('Qi')
        axis.set_ylabel('Average Water Saturation (Swm)')
        axis.scatter(Qi, Avg_Sw, c='b', s=12, label='Experimental Avg Sw')
        axis.scatter(Qi, Swm, c='r', s=12, label='Calculated Avg Sw')
        axis.legend(loc='center right')
    else:
        axis.clear()
    axis.set_yticks(np.arange(0,100,10))
    axis.set_ylim(0,100)
    axis.grid(True)
    figure = gui.draw_figure(window['-NP-'].TKCanvas, fig_)
    return   figure

def plot_dp (window, figure, fig_, axis, Qi, lambda2, switch):                          # Plot lambda2 calculated based on deltaP
    figure.get_tk_widget().forget()
    if switch == True:
        axis.set_xlabel('Qi')
        axis.set_ylabel('Lambda2')
        axis.scatter(Qi, lambda2, c='b', s=12, label='Lambda2')
        axis.legend(loc='center right')
    else:
        axis.clear()
    axis.grid(True)
    figure = gui.draw_figure(window['-DP-'].TKCanvas, fig_)
    return   figure

def plot_kr (window, figure, fig_, axis, Sw2, kro, krw, Swi, Swf, switch):
    figure.get_tk_widget().forget()
    if switch == True:
        axis.set_xlabel('Sw')
        axis.set_ylabel('Kr')
        axis.scatter(Sw2, krw,c='b', s=12)
        axis.plot(Sw2, krw, c='b', lw=0.5, label='Krw')
        axis.scatter(Sw2, kro,c='r', s=12)
        axis.plot(Sw2, kro, c='r', lw=0.5, label='Kro')
        axis.plot([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
        axis.plot([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
        axis.legend(loc='center right')
    else:
        axis.clear()
        axis.set_xticks(np.arange(0,101,10))
    axis.set_yticks(np.arange(0,1.1,0.1))
    axis.set_xlim(0,100)
    axis.set_ylim(0,1)
    axis.grid(True)
    figure = gui.draw_figure(window['-KR-'].TKCanvas, fig_)
    return   figure

def plot_fw (window, figure, fig_, axis, Sw2, fw, Swi, Swf, switch):
    figure.get_tk_widget().forget()
    if switch == True:
        axis.set_xlabel('Sw')
        axis.set_ylabel('Fractional flow of water (fw)')
        axis.scatter(Sw2, fw, c='b', s=12)
        axis.plot(Sw2, fw, c='b', lw=0.5, label='fw')
        axis.plot([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
        axis.plot([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
    else:
        axis.clear()
        axis.set_xticks(np.arange(0,101,10))
    axis.set_yticks(np.arange(0,1.1,0.1))
    axis.set_xlim(0,100)
    axis.set_ylim(0,1)
    axis.grid(True)
    figure = gui.draw_figure(window['-FW-'].TKCanvas, fig_)
    return   figure


def plot_exp (window, figure, fig_, axis1, axis2, Wi, Np, deltaP, degree, Use):      # Plot the experimental values of Np
    Wi = Wi[(Use == True)] 
    Np = Np[(Use == True)]
    deltaP = deltaP[(Use == True)]
    Coef = np.polyfit(Wi, Np, degree)
    fit1 = np.polyval(Coef, Wi)
    Coef = np.polyfit(Wi, deltaP, degree)
    fit2 = np.polyval(Coef, Wi)
    figure.get_tk_widget().forget()
    axis1.clear()
    axis2.clear()
    axis1.set_xlabel('Wi (ml)')
    axis1.set_ylabel('Np (ml)')
    axis2.set_ylabel('deltaP (psi)')
    axis1.scatter(Wi, Np, c='b', s=12, label='Experimental Np')
    axis2.scatter(Wi, deltaP, c='r', s=12, label='Experimental Delta P')
    axis1.plot(Wi, fit1, c='black', linewidth=0.5, linestyle='-.', marker='o', markersize=3, label='Fitted Np')
    axis2.plot(Wi, fit2, c='black', linewidth=0.5, linestyle='-.', marker='o', markersize=3, label='Fitted Delta P')
    lines1, labels1 = axis1.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines1 + lines2, labels1 + labels2, loc='center right')
    axis1.grid(True)
    figure = gui.draw_figure(window['-EX-'].TKCanvas, fig_)
    return   figure, fit1, fit2

