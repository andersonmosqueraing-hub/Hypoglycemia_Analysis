import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import ptitprince as pt
from pandas import to_datetime
from datetime import timedelta, date, datetime
import math
import pandas as pd


def Event(Data,glucose_threshold):
    'Data has to be type list'
    'Threshold should be an integer'
    C1 = 0
    C2 = 0
    for i in range(len(Data)) :
        if Data[i] < glucose_threshold:
            C1+=1
        if C1 == 3:
            C2+=1
        elif C1 >2:
            pass
        else:
            pass
    else:
        C1=0
    if C2 > 1:
        return 1
    else:
        return 0

# create a list for storing the data

def New_Sequences(data):
    sequences = []
    NotWorking = []
    minutes = 5
    Days_Week = 7 # this is the number of days to be considered i na week, can be changed
    glucose_threshold = 54
    # calculate the number of timestamps in one week
    sequence_length = int(Days_Week * 24 * 60 // minutes)
    for patient in data.id.unique():
        # Data = pd.DataFrame()
        if type(patient) == int:
            try:
                #Do preprocessing inside the function per patient
                Data = data[data['id'].isin([patient])]
                Data = data[data['gl'].between(40, 400)]
                # reshape the dataset from long to wide
                Data = Data.pivot(index='ts', columns=['id'], values=['gl'])
                Data.columns = Data.columns.get_level_values(level='id')
                Data.reset_index(inplace = True)
                Data['date'] = pd.to_datetime(Data['ts']).dt.date
                
                
                
                Data=Data[Data[patient].notnull()]
                #Per Patient
                min_Date = datetime.strptime(str(Data['ts'].min())[:-9], '%Y-%m-%d').date()
                # print(min_Date)
                max_Date = datetime.strptime(str(Data['ts'].max())[:-9], '%Y-%m-%d').date()
                # print(max_Date)
                Difference = abs(max_Date-min_Date).days #difference in days between the two dates  
                Sequences = math.ceil(Difference/Days_Week) # Define the number of 1 week sequences
                Result = pd.DataFrame()
                for i in range (1, Sequences, 1):
                    # generate the range
                    date_generated = pd.DataFrame()    
                    date_generated = [min_Date + timedelta(days=x) for x in range(0, (timedelta(days=Days_Week)).days)]
                    # print(len(date_generated))
                    min_Date = min_Date + timedelta(days=Days_Week+1)
                    df_Generated = pd.DataFrame(date_generated)
                    df_Generated = df_Generated.rename(columns={0:'date'})
                    df_Generated = pd.merge(df_Generated,Data,'left',left_on='date',right_on='date')
                    df_Generated['Sequence'] = i
                    Result = pd.concat([Result,df_Generated])
                Grouped = Result.groupby('Sequence').count()
                Grouped['Total_Readings_Sequence'] = sequence_length
                Grouped = Grouped[['ts','Total_Readings_Sequence']]
                Grouped['Time_Worn'] = Grouped['ts']/Grouped['Total_Readings_Sequence']
                Grouped['Criteria'] = np.where(Grouped['Time_Worn']>0.7, "Applicable", 'Not Applicable')
                Grouped = Grouped[Grouped['Criteria']=='Applicable']
                Result = Result[Result['Sequence'].isin(Grouped.index.to_series())]          
                for i in Grouped.index.to_series():
                    #Evaluate if next is applicable
                    try:
                        if Grouped.loc[i+1]['Criteria'] == 'Applicable':
                            X = Result[patient][Result['Sequence'] == i].dropna().to_list()
                            L = len(X)
                            Y = Result[patient][Result['Sequence'] == i+1].to_list()
                            Y = Event(Y, glucose_threshold)
                            #I need to determine the amount of consecutive data below the threshold and if it greater that 15 minutes (three readings) then Y = 1
                            # save the patient's data
                            sequences.append({
                            'patient': patient,
                            'Sequence': i,
                            'start': str(Result['ts'][Result['Sequence'] == i].min()),
                            'end': str(Result['ts'][Result['Sequence'] == i].max()),
                            'L': L,
                            'X': X,
                            'Y': Y
                            })
                        else:
                            pass
                    except:
                        pass
            except:
                NotWorking.append(patient)
        else:
            pass
    return sequences