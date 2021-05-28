# -*- coding: utf-8 -*-
"""
Created on Fri May 28 14:35:01 2021

@author: jbardelli
"""

import pandas as pd
import numpy as np

def save_to_file (file, Swi, L, D, Vp, uo, uw, q, ko_Swi, Sor, Swf, krw_Sor, Wi, Np, deltaP, Sw2, kro, krw, Wiexp, Npexp, deltaPexp, degree):
    
    #--- WRITE TO EXCEL FILE ---
    writer = pd.ExcelWriter(file,engine="xlsxwriter" )
    workbook = writer.book
    worksheet = workbook.add_worksheet('KR')
    writer.sheets['KR'] = worksheet
    sat_format = workbook.add_format()
    sat_format.set_num_format('0.0')
    kr_format = workbook.add_format()
    kr_format.set_num_format('0.000')
    worksheet.write('A1', '--TEST DATA--')
    worksheet.write('A2', 'Swi[%]')
    worksheet.write('B2', Swi, sat_format)
    worksheet.write('A3', 'Longitude[cm]')
    worksheet.write('B3', L)
    worksheet.write('A4', 'Diameter [cm]')
    worksheet.write('B4', D)
    worksheet.write('A5', 'VP[cm3]')
    worksheet.write('B5', Vp)
    worksheet.write('A6', 'uo[cP]')
    worksheet.write('B6', uo)
    worksheet.write('A7', 'uw[cP]')
    worksheet.write('B7', uw)
    worksheet.write('A8','q[cm3/h]')
    worksheet.write('B8', q)
    worksheet.write('A9', 'Ko@Swi [mD]')
    worksheet.write('B9', ko_Swi)   
    worksheet.write('A10', '--RESULTS--')
    worksheet.write('A11', 'Sor[%]')
    worksheet.write('B11', Sor ,sat_format)
    worksheet.write('A12', 'Swf[%]')
    worksheet.write('B12', Swf, sat_format)
    worksheet.write('A13','Krw@Sor')
    worksheet.write('B13', krw_Sor, kr_format)
    worksheet.write('A14','Polinomial Degree')
    worksheet.write('B14', degree)
    
    worksheet.write('A16','--RELATIVE PERMEABILITY RESULTS TABLE--')
    df1 = pd.DataFrame(np.transpose([Sw2,kro,krw]), columns=['Sw','kro','krw'])
    df1.to_excel(writer, sheet_name='KR', startrow=17, startcol=0)
    
    worksheet.write('A41','--DATA TABLE USED IN CALCULATIONS--')    
    df2 = pd.DataFrame(np.transpose([Wi, Np, deltaP]), columns=['Wi (ml)', 'Np (ml)', 'deltaP (psi)'])
    df2.to_excel(writer, sheet_name='KR', startrow=42, startcol=0)
    
    worksheet.write('A66','--EXPERIMENTAL DATA TABLE--') 
    df3 = pd.DataFrame(np.transpose([Wiexp, Npexp, deltaPexp]), columns=['Wi exp (ml)', 'Np exp (ml)', 'deltaP exp (psi)'])
    df3.to_excel(writer, sheet_name='KR', startrow=67, startcol=0) 
    
    writer.save()  
      