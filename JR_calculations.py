# -*- coding: utf-8 -*-
"""
Created on Fri May 14 11:17:20 2021

@author: jbardelli
"""
#--- Jones and Roszelle calculation functions as well as LET fitting functions ---
import numpy as np
import numpy.polynomial.polynomial as poly
import math as m
import pandas as pd
from scipy import interpolate
from scipy.optimize import minimize

def get_data_table (file):
    data = pd.read_csv(file, index_col=0)    # Import Data Table
    
    # print("\nRAW EXPERIMENTAL DATA\n",data)
    # BTpoint=0
    # data=data.drop(data.index[[range(0,BTpoint)]])
    #print("\nTabla de datos a partir del BT\n",data)
    
    Widf = data['Wi (ml)']              #Get the panda data frames from the file
    Npdf = data['Np (ml)']
    deltaPdf = data ['deltaP (psi)']
    
    Wi=Widf.to_numpy()                  #Convert panda DataFrame to numpy array for calculations
    Np=Npdf.to_numpy()
    deltaP=deltaPdf.to_numpy()
               
    Wi=np.delete (Wi,[0,1])             #Delete first position to avoid NaN error in optimization functions
    Np=np.delete (Np,[0,1])
    deltaP=np.delete(deltaP,[0,1])
    result = (Wi, Np, deltaP)
    return result

def differ_sw (x, Swi, Np, Vp, Qi, degree):
    a, b = x
    Avg_Sw=(Swi/100+Np/Vp)*100          # Calculate average water saturation
    Pvi_Tr=(Qi+a)**b                      # Transfor axis
    Coef_Pol=poly.polyfit(Pvi_Tr, Avg_Sw, degree)
    Swm_calc=poly.polyval((Qi+a)**b, Coef_Pol)
    result=np.sum((Avg_Sw-Swm_calc)**2)
    return result

def differ_lambda (x, deltaP, q, dpb_qb, Qi, uw, degree):
    a, b = x
    lambda1=uw*(deltaP/q)/dpb_qb
    Pvi_L=(Qi+a)**b
    Coef_Pol=poly.polyfit(Pvi_L, lambda1, degree)
    lambda1_calc=poly.polyval((Qi+a)**b, Coef_Pol)
    result=np.sum((lambda1-lambda1_calc)**2)
    return result

def lsq_let_kro (x, Swn, kro):
    L, E, T = x
    kro_let=((1-Swn)**L)/((1-Swn)**L+E*Swn**T)
    result=np.sum((kro-kro_let)**2)
    return result

def lsq_let_krw (x, Swn, krw, krw_Sor):
    L, E, T = x
    krw_let=(krw_Sor*(Swn**L))/((Swn**L)+E*((1-Swn)**T))
    result=np.sum((krw-krw_let)**2)
    return result

def kro_LET (Lo, Eo, To, Swn):
    kro_fit=((1-Swn)**Lo)/((1-Swn)**Lo+Eo*Swn**To)
    return kro_fit

def krw_LET (Lw, Ew, Tw, Swn, krw_Sor):
    krw_fit=(krw_Sor*(Swn**Lw))/((Swn**Lw)+Ew*((1-Swn)**Tw))
    return krw_fit

def calc_kr (Vp, Swi, q, L, D, uw, uo, ko_Swi, degree, Wi, Np, deltaP):
    
    Qi=Wi/Vp                            #Calculate pore volumes injected
    dpb_qb = uw*(L/(m.pi*D**2/4))*(1/ko_Swi)*14.69/3600*1000    #Calculate deltapb/qb (see Jones paper)
    
    #------- Solve the a & b values that fit Avg_Sw curve ----
    x0 = [1,1]
    result = minimize(differ_sw,x0, args=(Swi, Np, Vp, Qi, degree), bounds=((-0.2,100),(-100,100)))
    print("\nLeast square value for Sw: ", '%.3f' %differ_sw(result.x, Swi, Np, Vp, Qi, degree))
    a, b = result.x
    print("Values of a= ", '%.3f' %a, " and b= ", '%.3f' %b)
    
    #--- Calculate Sw2 with the a & b values obtained before ---
    Avg_Sw=(Swi/100+Np*Qi/Wi)*100                       #Calculate average water saturation
    Pvi_Tr=(Qi+a)**b                                    #Transform axis
    Coef_Pol=poly.polyfit(Pvi_Tr,Avg_Sw,degree)         #Calculate polinomial coefficientes that fit the Pvi_Tr curve
    Swm_calc=poly.polyval((Qi+a)**b,Coef_Pol)           #Calculate Average water sat with the coefficients obtained
    delta=(np.max(Qi)-np.min(Qi))/1000
    Swm_plus=poly.polyval(((Qi+a+delta)**b),Coef_Pol)
    Swm_minus=poly.polyval(((Qi+a-delta)**b),Coef_Pol)
    deriv=(Swm_plus-Swm_minus)/(2*delta)                #Calculate the derivative using deltas
    Sw2=Avg_Sw-Qi*deriv                                 #Calculate the saturation at the outlet face Sw2
    fo2=(Avg_Sw-Sw2)/(Qi*100)                           #Calculate fractional flow of oil
    fw2=1-fo2                                           #Fractional flow of water
    
    #------- Solve the a & b values that fit lambda1 curve ----
    x0 = [0,0]
    result = minimize(differ_lambda,x0, args=(deltaP, q, dpb_qb, Qi, uw, degree), bounds=((-0.2,100),(-100,100)))
    print("\nLeast square value for Lambda1: ", '%.3f' %differ_lambda(result.x, deltaP, q, dpb_qb, Qi, uw, degree))
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

    #--- Calculate both relative permeabilities ---
    krw=uw*fw2/lambda2                  
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
     
    #------- Solve the LET for kro ----
    Swn = (Sw2-Swi)/(Swf-Swi)                               #Swn is needed for the LET fitting to smooth the kr curves
    x0 = [1,1,1]                                            #Initial guess for minimize function
    result = minimize(lsq_let_kro, x0, args=(Swn, kro))     #minimize the least square func. using x0
    Lo, Eo, To = result.x                                   #minimize returns the L, E, and T parameters that best fit kro
    kro_fit = kro_LET (Lo, Eo, To, Swn)                     #Calculate kro array with the LET parameters
    
    #------- Solve the LET for krw ----
    result = minimize(lsq_let_krw, x0, args=(Swn, krw, krw_Sor))    #minimize the least square func. using x0
    Lw, Ew, Tw = result.x                                           #minimize returns the L, E, and T parameters that best fit krw    
    krw_fit = krw_LET (Lw, Ew, Tw, Swn, krw_Sor)                    #Calculate krw array with the LET parameters
    
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
  
    result = (Qi, Avg_Sw, Swm_calc, lambda2, kro, krw, kro_fit, krw_fit, Sw2, Sor, Swf, kro[0], krw_Sor, fw)
    
    return result

#-------------------------------