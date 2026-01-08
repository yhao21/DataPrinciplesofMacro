import pandas as pd
import os, glob, json
from pathlib import Path

from MyTools.frequency_conversion import get_frequency

def get_indent_config(data_name:str):
    """
    data_name: NGDP-BEA.
                If an dataset comes with indent config (data_name is a key in config_info),
                return indent_info, otherwise, return None.
    """
    with open(os.path.join(os.getcwd(), 'config', 'indent_config.json')) as f:
        config_info = json.load(f)
    try:
        return config_info[data_name]
    except:
        return None


def load_csv(path_csv):
    return pd.read_csv(path_csv)


def get_col_name(col_name, data_freq):
    return f"[{data_freq}] {col_name}"


def get_official_name_for_col_with_ident(indent_config, col_name):
    """
    Format: <variable A> UNDER <its upper class variable> IN <main variable of that dataset>.
            For example:
                <Durable goods> UNDER <Goods> IN <Gross domestic product>
    """
    main_variable = list(indent_config.keys())[0]
    indent_level = indent_config[col_name] # 0: no indent, 1: subgroup, 2: subsubgrpu, ...

    if indent_level != 0:
        parent_variable = find_parent_variable(indent_config, col_name)
        first_part_name = get_official_name_part_under_which_variable(parent_variable, col_name)
        return get_official_name_part_in_which_dataset(main_variable, first_part_name)
    else:
        return get_official_name_part_in_which_dataset(main_variable, col_name)


def find_parent_variable(indent_config, col_name):

    indent_level = indent_config[col_name] # 0: no indent, 1: subgroup, 2: subsubgrpu, ...
    parent_level = indent_level - 1
    var_list = list(indent_config.keys())   # Get the list of variable in dataframe
    index = var_list.index(col_name)        # Find position of current variable (col_nmae)
    # Slice list and reverse the order to let current var to be the first element
    var_list = var_list[:index+1][::-1]     
    parent_variable = None
    for i in var_list:
        if indent_config[i] == parent_level:
            parent_variable = i
            break

    return parent_variable



def get_official_name_part_under_which_variable(main_variable, col_name):
    return f"[{col_name}] UNDER [{main_variable}]"

def get_official_name_part_in_which_dataset(main_variable, col_name):
    return f"{col_name} IN DATASET [{main_variable}]"


class DataCollection:
    def __init__(self):
        self.data_info = pd.DataFrame()

    def update_data_series(self, root_dir, save_to = os.path.join(os.getcwd(), 'data', 'List_of_ALL_variables.csv')):
        """
        This function return a list of names of data series.

        Rule of naming: <freq> <col_name> <dataset_name>
        self.data_info is a df which contains
            1. human readable name of a data serie (index of df),
            2. start_period,
            3. end_period,
            4. col_name in the dataset,
            5. csv name (use os.path.join(data, parse_data, csv_name) to form path_to_csv)
        Save data_info to local computer.
        Users can only see 1-3.
        use "path_data" to find the dataset, and use "col_name" to extract data


        Note: 
            Save index as it reflects variable names.
            When you load 'List_of_ALL_variables.csv' through pd.read_csv(), set "index_col = 0" to
            get the index.
        """

        ###------Locate data dir------###
        datalist = glob.glob(os.path.join(root_dir, '*.csv'))
        ###------Read all csv and extract column names------###
        for path_dataset in datalist:
            df = load_csv(path_dataset)
            # extract data information
            self.get_data_info(df, path_dataset)


        self.data_info['Data Series'] = self.data_info.index.values
        self.data_info.to_csv(save_to, index = False)
        print(self.data_info)


    def get_data_info(self, df, path_dataset):

        csv_name = os.path.basename(path_dataset).split('.csv')[0]  # NGDP-BEA-Q
        data_freq = get_frequency(csv_name)

        start_period, end_period = df['Time'].values[0], df['Time'].values[-1]
        if data_freq == 'A':
            start_period, end_period = int(start_period), int(end_period)

        data_name = csv_name[:-2]   # Used to check if indent config exists for this dataset.
        col_names = df.columns.to_list()[1:] # ignore the first column (Time column)

    
        indent_config = get_indent_config(data_name)

        if indent_config:
            # form col name
            for col in col_names:
                col_name_offcial = get_official_name_for_col_with_ident(indent_config, col)
                col_name_offcial = get_col_name(col_name_offcial, data_freq)
                self.record_dataset_info(col_name_offcial, start_period, end_period, col, path_dataset)
        else:
            for col in col_names:
                col_name_offcial = get_col_name(col, data_freq)
                self.record_dataset_info(col_name_offcial, start_period, end_period, col, path_dataset)



    def record_dataset_info(self, col_name_offcial, start_period, end_period, col, path_dataset):
        self.data_info.loc[col_name_offcial, 'Start Period'] = start_period
        self.data_info.loc[col_name_offcial, 'End Period'] = end_period
        self.data_info.loc[col_name_offcial, 'col_name'] = col
        self.data_info.loc[col_name_offcial, 'csv_name'] = os.path.basename(path_dataset)










if __name__ == '__main__':
    #path_dir = '../data/parse_data/'
    path_dir = Path('..')/'data'/'parse_data'

    save_csv_to = os.path.join('../', 'List_of_ALL_variables.csv')
    DataCollection().update_data_series(path_dir, save_to=save_csv_to)


