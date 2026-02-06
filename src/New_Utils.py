import numpy as np
from datetime import datetime, timedelta
from pandas import to_datetime
from datetime import timedelta, date, datetime
import math
import pandas as pd


def Event(Data, glucose_threshold, minutes):
    C1 = 0
    C2 = 0
    if minutes == 5:
        for i in range(len(Data)):
            # Solo si el dato es válido (no NaN) y menor al umbral
            if Data[i] < glucose_threshold:
                C1 += 1
                if C1 == 3:
                    C2 += 1
            else:
                # Si el nivel sube del umbral, se rompe la racha
                C1 = 0
                
    else:
        for i in range(len(Data)):
            # Solo si el dato es válido (no NaN) y menor al umbral
            if Data[i] < glucose_threshold:
                C1 += 1
                if C1 == 2:
                    C2 += 1
            else:
                # Si el nivel sube del umbral, se rompe la racha
                C1 = 0
        #lo del Shanghai
    return 1 if C2 >= 1 else 0

# create a list for storing the data

def New_Sequences(data, glucose_threshold=54, days_week=7, minutes=5):
    sequences = []
    # 2016 lecturas para 7 días si es cada 5 min
    expected_readings = int(days_week * 24 * 60 // minutes)
    
    # Pre-procesamiento global
    data = data[(data['gl'] >= 40) & (data['gl'] <= 400)].copy()
    data['ts'] = pd.to_datetime(data['ts'])
    data['date'] = data['ts'].dt.date

    for patient, p_data in data.groupby('id'):
        p_data = p_data.dropna(subset=['ts', 'gl']).sort_values('ts')
        if p_data.empty:
            continue

        # 2. Asegurar que min y max sean fechas válidas
        min_date = p_data['date'].min()
        max_date = p_data['date'].max()

        # 3. Validación de tipo: Si max_date es NaN (float), saltar paciente
        if pd.isna(min_date) or pd.isna(max_date):
            continue
            
        current_start = min_date
        max_date = p_data['date'].max()

        
        # El bucle avanza en saltos de 14 días (7 para X + 7 para Y)
        # o 7 días si quieres que la 'Y' de una secuencia sea la 'X' de la siguiente
        while current_start + pd.Timedelta(days=days_week * 2) <= max_date:
            current_end = current_start + pd.Timedelta(days=days_week)
            next_end = current_end + pd.Timedelta(days=days_week)
            
            # Segmentación de ventanas
            mask_x = (p_data['date'] >= current_start) & (p_data['date'] < current_end)
            mask_y = (p_data['date'] >= current_end) & (p_data['date'] < next_end)
            
            week_x = p_data[mask_x]
            week_y = p_data[mask_y]
            
            # Verificación de calidad (Time Worn)
            if len(week_x) >= (expected_readings * 0.7) and len(week_y) >= (expected_readings * 0.7):
                
                # Cálculo de la etiqueta Y
                # Usamos la lógica de duraciones del código anterior si prefieres
                y_label = Event(week_y['gl'].tolist(), glucose_threshold, minutes)
                
                sequences.append({
                    'patient': patient,
                    'start_x': week_x['ts'].min(),
                    'end_x': week_x['ts'].max(),
                    'start_y': week_y['ts'].min(),
                    'Y': y_label,
                    'X': week_x['gl'].tolist(),
                    'L': len(week_x)
                })
            
            # --- EL CAMBIO CLAVE PARA VENTANA FIJA ---
            # Saltamos la semana completa para que no haya solapamiento
            current_start = current_end 
            
    return sequences