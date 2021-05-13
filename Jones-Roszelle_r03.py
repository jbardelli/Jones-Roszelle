# print(- coding: utf-8 -*-
"""
Created on Sun Apr 23 20:35:54 2017

@author: jbardelli
"""
# Test Branch
import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import minimize
import PySimpleGUI as sg
from styleframe import StyleFrame, Styler, utils

#---- CALCULATION FUNCTIONS ----
def differ_sw (x):
    a, b = x
    Avg_Sw=(Swi/100+Np/Vp)*100          # Calculate average water saturation
    Pvi_Tr=(Qi+a)**b                      # Transfor axis
    Coef_Pol=poly.polyfit(Pvi_Tr, Avg_Sw, degree)
    Swm_calc=poly.polyval((Qi+a)**b, Coef_Pol)
    result=np.sum((Avg_Sw-Swm_calc)**2)
    return result

def differ_lambda (x):
    a, b = x
    lambda1=uw*(deltaP/q)/dpb_qb
    Pvi_L=(Qi+a)**b
    Coef_Pol=poly.polyfit(Pvi_L, lambda1, degree)
    lambda1_calc=poly.polyval((Qi+a)**b, Coef_Pol)
    result=np.sum((lambda1-lambda1_calc)**2)
    return result
    
def lsq_let_kro (x):
    L, E, T = x
    kro_let=((1-Swn)**L)/((1-Swn)**L+E*Swn**T)
    result=np.sum((kro-kro_let)**2)
    return result

def lsq_let_krw (x):
    L, E, T = x
    krw_let=(krw_Sor*(Swn**L))/((Swn**L)+E*((1-Swn)**T))
    result=np.sum((krw-krw_let)**2)
    return result

def kro_LET (Lo, Eo, To, Swn):
    kro_fit=((1-Swn)**Lo)/((1-Swn)**Lo+Eo*Swn**To)
    return kro_fit

def krw_LET (Lw, Ew, Tw, Swn):
    krw_fit=(krw_Sor*(Swn**Lw))/((Swn**Lw)+Ew*((1-Swn)**Tw))
    return krw_fit
#-------------------------------

# --- Beginning of Matplotlib helper code ---

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

#--- Clears or plots a specific curve ---

def plot_action (figure, fig_, axis, curvex, curvey, switch, color):
    figure.get_tk_widget().forget()
    if switch == True:
        axis.scatter (curvex, curvey,c=color)
    else:
        axis.clear()
    figure = draw_figure(window['-CANVAS-'].TKCanvas, fig_)
    return   figure
#-------------------------------------------

#--- TEST DATA ---
Swi=44
Vp=14.07
uw=0.97
uo=60
dpb_qb=0.9430
q=18
degree=2


#--- Import Data Table ---
data = pd.read_csv(r'C:\Users\jbardelli\Documents\Python\Jones Roszelle\Sample_MV.a-37-1-8-148.csv',index_col=0)
print("\nRAW EXPERIMENTAL DATA\n",data)

# BTpoint=0
# data=data.drop(data.index[[range(0,BTpoint)]])
#print("\nTabla de datos a partir del BT\n",data)

Widf = data['Wi (ml)']
Npdf = data['Np (ml)']
deltaPdf = data ['deltaP (psi)']

Wi=Widf.to_numpy()                  #Convert panda DataFrame to numpy array
Np=Npdf.to_numpy()
deltaP=deltaPdf.to_numpy()

Wi=np.delete (Wi,[0,1])             #Delete first position to avoid NaN
Np=np.delete (Np,[0,1])
deltaP=np.delete(deltaP,[0,1])

Qi=Wi/Vp                            #Calculate pore volumes injected

#------- Solve the a & b values that fit Avg_Sw curve ----
x0 = [1,1]
result = minimize(differ_sw,x0,bounds=((-0.2,100),(-100,100)) )
print("\nLeast square value for Sw: ", '%.3f' %differ_sw(result.x))
a, b = result.x
print("Values of a= ", '%.3f' %a, " and b= ", '%.3f' %b)

#--- Calculate Sw2 with the a & b values obtained before ---
Avg_Sw=(Swi/100+Np*Qi/Wi)*100          # Calculate average water saturation
Pvi_Tr=(Qi+a)**b                       # Transfor axis
Coef_Pol=poly.polyfit(Pvi_Tr,Avg_Sw,degree)
Swm_calc=poly.polyval((Qi+a)**b,Coef_Pol)
delta=(np.max(Qi)-np.min(Qi))/1000
Swm_plus=poly.polyval(((Qi+a+delta)**b),Coef_Pol)
Swm_minus=poly.polyval(((Qi+a-delta)**b),Coef_Pol)
deriv=(Swm_plus-Swm_minus)/(2*delta)
Sw2=Avg_Sw-Qi*deriv
fo2=(Avg_Sw-Sw2)/(Qi*100)
fw2=1-fo2

#------- Solve the a & b values that fit lambda1 curve ----
x0 = [0,0]
result = minimize(differ_lambda,x0,bounds=((-0.2,100),(-100,100)) )
print("\nLeast square value for Lambda1: ", '%.3f' %differ_lambda(result.x))
a, b = result.x
print("Values of a= ", '%.3f' %a, " and b= ", '%.3f' %b)

#--- Calculate lambda2 with the a & b values obtained before ---
lambda1=uw*(deltaP/q)/dpb_qb
Pvi_L=(Qi+a)**b
Coef_Pol=poly.polyfit(Pvi_L,lambda1,degree)
L_plus=poly.polyval(((Qi+a+delta)**b),Coef_Pol)
L_minus=poly.polyval(((Qi+a-delta)**b),Coef_Pol)
deriv=(L_plus-L_minus)/(2*delta)
lambda2=lambda1-Qi*(deriv)
 
fig, ax1 = plt.subplots()           # Plot Sw, Swm, lambda1 & 2 as func of Qi
ax1.scatter(Qi,Avg_Sw,c='orange')
ax1.scatter(Qi,Sw2,c='red')
ax1.scatter(Qi,Swm_calc, c='blue')
ax1.set_xlabel('Qi')
ax1.set_ylabel('Sw [%]')
ax2 = ax1.twinx()
ax2.scatter(Qi,lambda1,c='red')
ax2.scatter(Qi,lambda2,c='black')
ax2.set_ylabel('deltaP [psi]')

krw=uw*fw2/lambda2                  # Calculate both relative permeabilities
kro=uo*fo2/lambda2

#--- Extrapolate Sw to infinite pore volumes to calculate Sor ---
Sw_extrap=interpolate.interp1d(1/Qi,Sw2,kind='linear',fill_value='extrapolate')
Swf1=Sw_extrap(0)
Sw_extrap=interpolate.interp1d(1/Qi,Avg_Sw,kind='linear',fill_value='extrapolate')
Swf2=Sw_extrap(0)
Swf=Swf1                            # I use the extrapolation of Sw2
Sor=(100-Swf)                       # Calculate Sor

#--- Extrapolate krw to Sor to obtain krw at infinite pore volumes ---
krw_extrap=interpolate.interp1d(Sw2,krw,kind='linear',fill_value='extrapolate')
krw_Sor=krw_extrap(Swf)
fw=1/(1+(kro/krw)*(uw/uo))

Sw2=np.append(Sw2,Swf)              # Add the extrapolated values at Sor
kro=np.append(kro,0)
krw=np.append(krw,krw_Sor)
fw=np.append(fw,1)

Sw2=np.insert(Sw2,0,Swi)            # Add the values at Swi
krw=np.insert(krw,0,0)
kro=np.insert(kro,0,1)
fw=np.insert(fw,0,0)  

# Kr plot
plt.figure(4)
plt.plot ([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
plt.plot ([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
plt.scatter (Sw2,krw,c='b')
plt.scatter (Sw2,kro,c='r')
plt.plot (Sw2,krw,c='b')
plt.plot (Sw2,kro,c='r')
plt.xlim(0,100)
plt.ylim(0,1)
plt.xlabel('Sw [%]')
plt.ylabel('Relative Permeability')
plt.xticks(np.arange(0,100,10))

# Fractional flow of water plot
plt.figure(6)
plt.plot ([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
plt.plot ([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
plt.plot(Sw2,fw,c='b')
plt.scatter(Sw2,fw,c='b')
plt.xlim(0,100)
plt.ylim(0,1)
plt.xlabel('Sw [%]')
plt.ylabel('Fractional Flow of Water')


#------- Solve the LET for kro ----
Swn = (Sw2-Swi)/(Swf-Swi)                       #Swn is needed for the LET fitting to smooth the kr curves
x0 = [1,1,1]                                    #Initial guess for minimize function
result = minimize(lsq_let_kro,x0)               #minimize the least square func. using x0
Lo, Eo, To = result.x                           #minimize returns the L, E, and T parameters that best fit kro
kro_fit = kro_LET (Lo, Eo, To, Swn)             #Calculate kro array with the LET parameters

#------- Solve the LET for krw ----
result = minimize(lsq_let_krw,x0)               #minimize the least square func. using x0
Lw, Ew, Tw = result.x                           #minimize returns the L, E, and T parameters that best fit krw    
krw_fit = krw_LET (Lw, Ew, Tw, Swn)             #Calculate krw array with the LET parameters

#--- PRINT RESULTS ---
print("\n---- RESULTS ---")
print("\nIrreducible water saturation (Swi): ", '%.1f' %Swi)
print("Residual oil saturation (Sro): ", '%.1f' %Sor)
print("Final water saturation (Swf)",'%.1f' %Swf)
print("Kro@Swi: ", '%.3g' %kro[0])
print("Krw@Sor: ", '%.3g' %krw_Sor)
print("\nSwf calculated with Sw2: ", '%.1f' %Swf1)
print("Swf calculated with Swm: ", '%.1f' %Swf2)
print("\nLET parameters for kro, Lo= ",'%.2f' %Lo, " Eo= ", '%.2f' %Eo, ", To= ", '%.2f' %To)
print("LET parameters for krw, Lw= ",'%.2f' %Lw, " Ew= ", '%.2f' %Ew, ", Tw= ", '%.2f' %Tw)

print("\n--- TABLES ---")
print("\nRELATIVE PERMEABILITY CURVES")  
results=[Sw2,kro,krw]
results=np.transpose(results)
df=pd.DataFrame(results,columns=['Sw','kro','krw'])
df['Sw'] = df['Sw'].map("{:,.1f}".format).astype(float)
df['kro'] = df['kro'].map("{:,.3f}".format).astype(float)
df['krw'] = df['krw'].map("{:,.3f}".format).astype(float)
print(df)

print("\nRELATIVE PERMEABILITY CURVES with LET fitting")  
results_LET=[Sw2,kro_fit,krw_fit]
results_LET=np.transpose(results_LET)
df_let=pd.DataFrame(results_LET,columns=['Sw','kro','krw'])
df_let['Sw'] = df_let['Sw'].map("{:,.1f}".format).astype(float)
df_let['kro'] = df_let['kro'].map("{:,.3f}".format).astype(float)
df_let['krw'] = df_let['krw'].map("{:,.3f}".format).astype(float)
print(df_let) 

#--- WRITE TO EXCEL FILE ---
writer = pd.ExcelWriter("test_KR.xlsx",engine="xlsxwriter" )
workbook = writer.book
worksheet = workbook.add_worksheet('KR')
writer.sheets['KR'] = worksheet
sat_format = workbook.add_format()
sat_format.set_num_format('0.0')
kr_format = workbook.add_format()
kr_format.set_num_format('0.000')
worksheet.write('A1','--TEST DATA--')
worksheet.write('A2','Swi[%]')
worksheet.write('B2', Swi, sat_format)
worksheet.write('A3','VP[cm3]')
worksheet.write('B3',Vp)
worksheet.write('A4','uo[cP]')
worksheet.write('B4',uo)
worksheet.write('A4','uw[cP]')
worksheet.write('B4',uw)
worksheet.write('A4','q[cm3/h]')
worksheet.write('B4',q)
worksheet.write('A5','--RESULTS--')
worksheet.write('A6','Sor[%]')
worksheet.write('B6', Sor ,sat_format)
worksheet.write('A7','Swf[%]')
worksheet.write('B7', Swf, sat_format)
worksheet.write('A8','Krw@Sor')
worksheet.write('B8', krw_Sor, kr_format)

df.to_excel(writer, sheet_name='KR', startrow=10, startcol=0)

worksheet = writer.book.add_worksheet('KR LET')
writer.sheets['KR LET'] = worksheet
worksheet.write(0,0,"LET RELATIVE PERMEABILITY TABLE")
df_let.to_excel(writer, sheet_name='KR LET', startrow=4, startcol=0)
writer.save()  
  
# LET fitting plot
plt.figure(7)
plt.plot ([Swf,Swf],[0,100],c='black',ls='--',lw=0.5)
plt.plot ([Swi,Swi],[0,100],c='black',ls='--',lw=0.5)
plt.scatter (Sw2,kro_fit,c='black',s=1)
plt.scatter (Sw2,krw_fit,c='black',s=1)
plt.scatter (Sw2,kro,c='black',s=1)
plt.scatter (Sw2,krw,c='black',s=1)
plt.plot (Sw2,kro_fit,c='r',linewidth=0.5)
plt.plot (Sw2,krw_fit,c='b',linewidth=0.5)
plt.xlim(0,100)
plt.ylim(0,1)
plt.xlabel('Sw [%]')
plt.ylabel('Relative Permeability')
plt.xticks(np.arange(0,100,10))