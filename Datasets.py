#Importar librerias
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import ptitprince as pt
pd.options.display.max_rows = 999
import warnings
warnings.filterwarnings("ignore")
import sys
sys.dont_write_bytecode = True
# Replace
path = r"C:\Users\Mosqu\universidadean.edu.co\MAIRA ALEJANDRA GARCIA JARAMILLO - ML_Analitica_Diabetes\REPLACE-BG Dataset-79f6bdc8-3c51-4736-a39f-c4c0f71d45e5\Data Tables\HDeviceCGM.txt"
def Loading_File(file_path):
    MasterDF = pd.read_csv(file_path, sep='|', header=0, low_memory = False)
    MasterDF = MasterDF[MasterDF['RecordType'] == 'CGM']
    #Creating a date time column
    MasterDF['Today'] = datetime.today().date()
    MasterDF['Date'] = MasterDF['Today'] + pd.to_timedelta(MasterDF['DeviceDtTmDaysFromEnroll'], unit='d')
    MasterDF['DeviceTm'] = MasterDF.DeviceTm.astype('str')
    MasterDF['DeviceTm'] = MasterDF['DeviceTm'].str[:-2]+ '00'
    MasterDF['DateTime'] = MasterDF.Date.astype('str')+ ' '+ MasterDF.DeviceTm
    MasterDF['DateTime'] = pd.to_datetime(MasterDF.DateTime, format='%Y-%m-%d %H:%M:%S')
    #selecting just the columns for Giammarino's code to run
    MasterDF = MasterDF[['PtID','DateTime','GlucoseValue']]
    MasterDF = MasterDF.rename(columns={'DateTime':'ts','PtID':'id','GlucoseValue':'gl'})
    MasterDF= MasterDF.reset_index(drop=True)
    MasterDF = MasterDF.drop_duplicates(subset=['ts','id'])
    return MasterDF
Replace = Loading_File(path)
# AIDE
path = r"C:\Users\Mosqu\universidadean.edu.co\MAIRA ALEJANDRA GARCIA JARAMILLO - ML_Analitica_Diabetes\AIDE T1D\Data Tables\AIDEDeviceCGM.txt"
def Loading_File(file_path):
    MasterDF = pd.read_csv(file_path, sep='|', header=0, low_memory = False)
    MasterDF = MasterDF[MasterDF['RecordType'] == 'CGM']
    #Creating a date time column
    MasterDF['DateTime'] = MasterDF['DataDtTm']
    MasterDF['DateTime'] = pd.to_datetime(MasterDF.DateTime, errors='coerce', infer_datetime_format=True)
    #selecting just the columns for Giammarino's code to run
    MasterDF = MasterDF[['PtID','DateTime','GlucValue']]
    MasterDF = MasterDF.rename(columns={'DateTime':'ts','PtID':'id','GlucValue':'gl'})
    MasterDF= MasterDF.reset_index(drop=True)
    MasterDF = MasterDF.drop_duplicates(subset=['ts','id'])
    return MasterDF
AIDE = Loading_File(path)
# Shanghai
from pathlib import Path
T1D = r"C:\Users\Mosqu\universidadean.edu.co\MAIRA ALEJANDRA GARCIA JARAMILLO - ML_Analitica_Diabetes\Dataset Shangai\Shanghai_T1DM"
T2D = r"C:\Users\Mosqu\universidadean.edu.co\MAIRA ALEJANDRA GARCIA JARAMILLO - ML_Analitica_Diabetes\Dataset Shangai\Shanghai_T2DM"
def Loading_File(file_path):
    files = list(Path(file_path).glob('*.xls*'))
    folder_dfs = pd.DataFrame()
    # print(files[0])
    for file in files:
        try:
            pti = str(file)[124:128]
            df_temp = pd.read_excel(str(file))
            df_temp = df_temp.iloc[:,0:2]
            df_temp = df_temp.rename(columns={df_temp.columns[0]: 'DateTime'})
            df_temp = df_temp.rename(columns={df_temp.columns[1]: 'GlucValue'})
            df_temp['PtID'] = pti
            df_temp['DateTime'] = pd.to_datetime(df_temp.DateTime, errors='coerce', infer_datetime_format=True)
            df_temp = df_temp[['PtID','DateTime','GlucValue']]
            df_temp = df_temp.rename(columns={'DateTime':'ts','PtID':'id','GlucValue':'gl'})
            df_temp= df_temp.reset_index(drop=True)
            df_temp = df_temp.drop_duplicates(subset=['ts','id'])
        except Exception as e:
            print(f"Error al leer {file.name}: {e}")
        folder_dfs = pd.concat([folder_dfs, df_temp])
    return folder_dfs
Shanghai_T1D = Loading_File(T1D)
Shanghai_T2D = Loading_File(T2D)
Shanghai = pd.concat([Shanghai_T1D, Shanghai_T2D])
