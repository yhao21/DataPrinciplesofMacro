import pandas as pd
from pathlib import Path
import streamlit as st

def frequency_dict():
    return {
            "D":"Daily",
            #"W": "Weekly",
            "M": "Monthly",
            "Q": "Quarterly",
            "A": "Annual"
            }

def frequency_mapping(freq):
    #mapping = {
    #        "D":"Daily",
    #        "W": "Weekly",
    #        "M": "Monthly",
    #        "Q": "Quarterly",
    #        "A": "Annual"
    #        }
    return frequency_dict()[freq]



def get_frequency_level(freq:str = None, freq_index:int = None):
    """
    If users pass a frequency (freq):
        Return the index of a frequency as a measure of frequency level. A larger index value 
        refers to a higher level of frequency.
        For example,
            Index for "A" is 4, and is 3 for "Q".
            "A" is a higher level since 4 > 3.
    If users pass an index of frequency (freq_index):
        return a frequency.
    """
    #frequency_level = ['D', 'W', 'M', 'Q', 'A']
    frequency_level = list(frequency_dict().keys())
    if freq:
        return frequency_level.index(freq)
    if freq_index != None:
        return frequency_level[freq_index]
    

def parse_BEA_month(time_col):
    """
    This function convert BEA month (e.g., 2025M08) to regular pandas datetime object (e.g., 2025-08).
    time_col: a pandas series, refers to the time column.
    """
    return [i.replace('M', '-') for i in time_col]


#=======================================================

def determine_frequency(path_data: str) -> str:
    """
    This function determines the type of time series data. It will be either monthly (M), quarterly (Q), or annual (A).
    How it works:
        This function will extract the last letter of file name. 

    If path_data = './PCE_M.csv'
    `Path().stem` returns PCE_M
    """

    return Path(path_data).stem.split('_')[1]


def get_frequency(data_name:str):

    return data_name.split('-')[-1]


def convert_frequency(raw_data, target_frequency:str, method = 'mean', original_freq = None):
    """
    This function can do the following conversion:
        1. from monthly to quarterly or anual data
        2. from quarterly to anual data.
    Then it return the new df in which Time is the first column.

    target_frequency:  Frequency you would like to convert the data to.
                        "M", "Q", 'A'

                        Not supported:
                        "MS", month start;
                        "ME", month end;
                        "QS",
                        "QE",
                        "AS",
                        "AE",...


    """

    raw_data['Time'] = pd.to_datetime(raw_data['Time'])
    # resample to target frequency
    df = raw_data.resample(target_frequency, on = 'Time')
    if method == 'mean':
        df = df.mean()

        if target_frequency != original_freq:
            # check if first and last period contains all obs in that period.
            first_period_is_full, last_period_is_full = check_full_period(raw_data, target_frequency, original_freq)
            if not first_period_is_full:
                df = df.drop(df.index[0])
            if not last_period_is_full:
                df = df.drop(df.index[-1])


    elif method == 'max':
        df = df.max()



    # If target_frequency = "QS", then freq = 'Q', etc.
    df_t = pd.PeriodIndex(df.index, freq = target_frequency[0]).to_frame().reset_index(drop = True)
    df = df.reset_index(drop = True)
    df = pd.concat([df_t, df], axis = 1).round(2)



    return df

def check_full_period(df, freq, original_freq):
    """
    Check if sample period is not full, drop it. 
    For example, given monthly data (df), user would like to convert it to quarterly (freq) data.
    If the first three obs. come from Feb. Mar. and Apr., then, the function will drop data from
    Feb. and Mar. since data from Jan. are missing, and it is unable to compute data in Q1.
    """

    df['test'] = pd.PeriodIndex(df['Time'], freq = freq)

    ###------Get first and last target period------###
    first_period = df['test'].unique()[0]
    last_period = df['test'].unique()[-1]

    ###------Generate full period------###
    first_period_start, first_period_end = get_start_end_period(first_period, original_freq)
    last_period_start, last_period_end = get_start_end_period(last_period, original_freq)

    # number of periods that the original dataset supposed to have.
    first_period_range = len(pd.period_range(first_period_start, first_period_end, freq = original_freq))
    last_period_range = len(pd.period_range(last_period_start, last_period_end, freq = original_freq))

    ###------Compare length------###
    actual_first_period_range = len(df[df['test'] == first_period])
    actual_last_period_range = len(df[df['test'] == last_period])

    first_period_is_full = (actual_first_period_range == first_period_range)
    last_period_is_full = (actual_last_period_range == last_period_range)


    return first_period_is_full, last_period_is_full



def get_start_end_period(one_time: pd.Period, freq):
    one_time = pd.Period(one_time)
    start = one_time.start_time.to_period(freq)
    end = one_time.end_time.to_period(freq)
    return start, end



def get_available_freq_list(data_name):
    # Frequency
    default_freq = get_frequency(data_name)
    freq_keys = list(frequency_dict().keys())
    default_index = freq_keys.index(default_freq)
    return [frequency_dict()[i] for i in freq_keys[default_index:]]



def get_YoY_window(freq:str):
    """
    This function compute the window for YoY change or percentage change.
    Example: given monthly data, window should be 12; given quarterly data, window should be 4.
    freq: M, Q, A, ...
    """
    return 12 if freq == 'M' else (4 if freq == 'Q' else 1)


if __name__ == '__main__':
    """
    Time column of raw dataframe must be named as "Time".
    Input: 
        1. path of dataset, the frequency of data is included at the end of file name.
        2. output frequency: str. Frequency of data that user want to receive, such as "M", "Q", "A".

    """

    #path_data = './PCE_M.csv'
    #path_data = '../data/parse_data/PCE-BEA-M.csv'
    path_data = '../data/parse_data/FFER-FRED-D.csv'
    df = pd.read_csv(path_data).head(100)
    print(df)

    df = convert_frequency(df, 'D', original_freq='D')







