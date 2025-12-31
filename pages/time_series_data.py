import json, os, re
import pandas as pd
from pathlib import Path

import streamlit as st
#from streamlit.components.v1 import iframe

from MyTools import chart_tools as chart
from MyTools.chart_template.chart_frame_lines import line_frame
from MyTools.load_data import load_dataset
from MyTools.load_data import get_percentage_share_GDP
from MyTools.load_data import get_rgdp
from MyTools.frequency_conversion import convert_frequency
from MyTools.frequency_conversion import get_frequency
from MyTools.frequency_conversion import get_frequency_level
from MyTools.frequency_conversion import get_YoY_window


class Description:
    def percent():
        return 'Percent, %'

    def bn_seasonally_adj():
        return 'Billions of dollars; seasonally adjusted'

    def seasonally_adj():
        return 'Seasonally adjusted'

    def bn_chained_seasonally_adj():
        return 'Billions of chained (2017) dollars; seasonally adjusted'




def get_merge_data_name(fig_name, platform, frequency):
    """
    Use this function to form data_name when a dataset is a merged from multiple datasets that come 
    with different data frequency.
    """
    return f"{fig_name}-{platform}-{frequency}"


def get_indent_config_name(data_name):
    
    return '-'.join(data_name.split('-')[:2])


def get_heightest_frequency_level(data_name_list:list):
    """
    Get the highest frequency level.

    Frequency level from highest to lowest:
        "A" > "Q" > "M" > "W" > "D"
    """
    ###------Get the highest frequency level------###

    target_freq = get_frequency_level(
            freq_index = max(
                [get_frequency_level(freq = get_frequency(i)) for i in data_name_list]
                )
            )

    return target_freq


def merge_data_df(data_name_list:list, target_freq = 'D', return_freq = False):
    """
    For each data_name in data_name_list:
        1. Load corresponding df named <data_name.csv> in directory parse_data.
            -- Use "Time" column as index, and drop "Time" column.
        2. Merge all dfs.
            -- You must make sure that data in all dfs are measured in the same frequency, such as daily, monthly, quarterly...
    """
    highest_data_freq = get_heightest_frequency_level(data_name_list)
    data_freq = target_freq if get_frequency_level(freq = target_freq) > get_frequency_level(freq = highest_data_freq) else highest_data_freq


    result = pd.DataFrame()
    for data_name in data_name_list:
        df = pd.read_csv(os.path.join('data', 'parse_data', f'{data_name}.csv'), index_col = 'Time')

        ###------Convert frequency------###
        df['Time'] = df.index
        df = convert_frequency(df, data_freq, original_freq=get_frequency(data_name)).set_index('Time')
        ###------Merge dataset------###
        result = pd.concat([result, df], axis = 1)



    result = result.sort_index()
    df_t = pd.PeriodIndex(result.index, freq = data_freq).to_frame().reset_index(drop = True)
    result = pd.concat([df_t, result.reset_index(drop = True)], axis = 1)



    if return_freq:
        return result, highest_data_freq
    else:
        return result




#
#def merge_data_df(data_name_list:list, target_freq = ''):
#    """
#    For each data_name in data_name_list:
#        1. Load corresponding df named <data_name.csv> in directory parse_data.
#            -- Use "Time" column as index, and drop "Time" column.
#        2. Merge all dfs.
#            -- You must make sure that data in all dfs are measured in the same frequency, such as daily, monthly, quarterly...
#    """
#    result = pd.DataFrame()
#    for data_name in data_name_list:
#        df = pd.read_csv(os.path.join('data', 'parse_data', f'{data_name}.csv'), index_col = 'Time')
#        result = pd.concat([result, df], axis = 1)
#
#
#    # Convert "Time" index to datetime type, then sort value from past to the present.
#    result.index = pd.to_datetime(result.index)
#    result = result.sort_index()
#    result['Time'] = result.index
#
#    if target_freq:
#        result = convert_frequency(result, target_freq)
#    print(result)
#
#    return result
#



class show_chart():
    """
    Data Source:
        You must add source information to ./config/source_info.json. The key is the item that
        will show above the table/chart. They key must follows the format below:
            platform(source_name)
        For example: FRED(RGDP), FRED(CPI), BEA(RGDP), ...
    """
    def __init__(self):
        self.current_dir = Path.cwd()
        self.isRGDP = False
        self.percent_share_GDP = False
        self.data_source()

    def data_source(self):
        #with open('../config/source_info.json')
        with open(os.path.join(self.current_dir, 'config', 'source_info.json')) as f:
            self.data_source = json.load(f)


    def form_data_source(self, item_names:list):
        """
        item_names: a list of data source (keys in source_info).
        Output: "source1, source2, ..."
        """

        return ", ".join([f"[{i}]({self.data_source[i]})" for i in item_names])

        

    def show(self, fig_name, chart_config):
        """
        This function decides which chart to plot based on the fig_name chose by users.

        To show rgdp data, set self.isRGDP = True
        """
        self.chart_config = chart_config

        ###------National Income------###
        # NGDP
        if fig_name == "Gross domestic product (quarterly)":
            data_name = "NGDP-BEA-Q"
            #data_source = self.BEA_table_1_1_5
            data_source = self.form_data_source(["BEA(NGDP)"])
            description = 'Billions of dollars; seasonally adjusted'
            description = Description.bn_seasonally_adj()
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Gross domestic product (annual)":
            data_name = "NGDP-BEA-A"
            data_source = self.form_data_source(["BEA(NGDP)"])
            description = 'Billions of dollars; seasonally adjusted'
            description = Description.bn_seasonally_adj()
            self.show_GDP(data_source, description, data_name)

        # Percentage share of NGDP
        elif fig_name == "Percentage share of GDP (quarterly)":
            data_name = "NGDP-BEA-Q"
            self.percent_share_GDP = True
            data_source = self.form_data_source(["BEA(NGDP)"])
            description = 'Percent, %'
            description = Description.percent()
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Percentage share of GDP (annual)":
            data_name = "NGDP-BEA-A"
            self.percent_share_GDP = True
            data_source = self.form_data_source(["BEA(NGDP)"])
            description = 'Percent, %'
            description = Description.percent()
            self.show_GDP(data_source, description, data_name)

        # RGDP
        elif fig_name == "Real gross domestic product (quarterly)":
            data_name = "NGDP-BEA-Q"
            self.isRGDP = True
            data_source = self.form_data_source(["BEA(NGDP)", "BEA(GDP_Deflator)"])
            description = f'Billions of chained (2017) dollars; seasonally adjusted'
            description = Description.bn_chained_seasonally_adj()
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Real gross domestic product (annual)":
            data_name = "NGDP-BEA-A"
            self.isRGDP = True
            data_source = self.form_data_source(["BEA(NGDP)", "BEA(GDP_Deflator)"])
            description = f'Billions of chained (2017) dollars; seasonally adjusted'
            description = Description.bn_chained_seasonally_adj()
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Nominal vs. real GDP":
            src = "https://fred.stlouisfed.org/graph/graph-landing.php?g=1NOOf"
            ngdp_rgdp = chart.add_html_chart(src, border, hor_align, ver_align, chart_width, chart_height, iframe_height)

        # GDI
        elif fig_name == "Gross domestic income (quarterly)":
            data_name = "GDI-BEA-Q"
            data_source = self.form_data_source(["BEA(GDI)"])
            description = 'Billions of dollars; seasonally adjusted'
            description = Description.bn_seasonally_adj()
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Gross domestic income (annual)":
            data_name = "GDI-BEA-A"
            data_source = self.form_data_source(["BEA(GDI)"])
            description = 'Billions of dollars; seasonally adjusted'
            description = Description.bn_seasonally_adj()
            self.show_GDP(data_source, description, data_name)



        ###------Business cycle and AD-AS model------###
        elif fig_name == "Business cycle and AD/AS model":
            data_list = [
                    "RGDP-FRED-Q",      # rgdp
                    "FRGDP-FRED-Q",     # r potential gdp
                    "GDPDeflator-BEA-Q",# GDP deflator
                    "UNRATE-FRED-M",    # unemployment rate
                    "NRUNEM-FRED-M",    # natural rate
                    ]
            df0, freq = merge_data_df(data_list, return_freq = True)
            df0 = df0.dropna()
            df0.index = df0['Time']

            ###------Derive data series------###
            df = df0[['Time']]
            df['Output gap'] = (df0['Real Gross Domestic Product'] - df0['Real Potential Gross Domestic Product'])/df0['Real Potential Gross Domestic Product'] * 100
            df['Unemployment rate gap'] = df0['Unemployment Rate'] - df0['Natural Rate of Unemployment (Short-Term) (DISCONTINUED)']
            window = get_YoY_window(freq)
            df['Inflation'] = df0['Gross domestic product'].pct_change(periods = window) * 100

            data_name = get_merge_data_name(fig_name, 'FRED', freq)
            data_source = self.form_data_source([
                "FRED(RGDP)",
                "FRED(Real Potential GDP)",
                "FRED(CPI)",
                "FRED(Unemployment Rate)",
                "FRED(Natural Rate of Unemployment)"
                ])

            description = Description.percent()
            line_frame(data_name, df, indent_config = {}, description = description, source = data_source, show_zero = True).show(n_legend_cols = 4)


        ###------Monetary Policy------###
        # FFR, FFR target, IORB rate, ONRRP rate and other policy rates.
        elif fig_name == "Monetary Policy and Interest Rate (monthly)":
            data_list = [
                    'FFER-FRED-D',
                    'FFRTUPPER-FRED-D',
                    'FFRTLOWER-FRED-D',
                    'FFRT-FRED-D',
                    'DISCOUNTPRIMARY-FRED-D',
                    'SREPOMR-FRED-D',
                    'IORR-FRED-D',
                    'IORB-FRED-D',
                    'ONRRP-FRED-D',
                    ]
            df = merge_data_df(data_list, target_freq = 'M')
            data_source = self.form_data_source(["FRED(Monetary Policy Rates)"])
            description = 'Percent, %'
            data_name = f'{fig_name}-FRED-M'
            line_frame(data_name, df, indent_config = {}, description = description, source = data_source).show(n_legend_cols = 3)

        elif fig_name == "Monetary Policy and Interest Rate (daily)":
            data_list = [
                    'FFER-FRED-D',
                    'FFRTUPPER-FRED-D',
                    'FFRTLOWER-FRED-D',
                    'FFRT-FRED-D',
                    'DISCOUNTPRIMARY-FRED-D',
                    'SREPOMR-FRED-D',
                    'IORR-FRED-D',
                    'IORB-FRED-D',
                    'ONRRP-FRED-D',
                    ]
            df = merge_data_df(data_list, target_freq = 'D')
            data_source = self.form_data_source(["FRED(Monetary Policy Rates)"])
            description = 'Percent, %'
            data_name = f'{fig_name}-FRED-D'
            line_frame(data_name, df, indent_config = {}, description = description, source = data_source).show(n_legend_cols = 3)


    def get_df(self, data_name):

        path_data = os.path.join(self.current_dir, 'data', 'parse_data', f"{data_name}.csv")
        df = load_dataset(path_data)

        # If to display percentage share of NGDP
        if self.percent_share_GDP:
            data_name = f"{data_name}_share-{get_frequency(data_name)}"
            df = get_percentage_share_GDP(df, 'Gross domestic product')

        if self.isRGDP:

            df_GDPDeflator = load_dataset(
                    os.path.join(self.current_dir, 'data', 'parse_data', f'GDPDeflator-BEA-{get_frequency(data_name)}.csv')
                    )
            data_name = f'RGDP-{get_frequency(data_name)}'
            df = get_rgdp(df, df_GDPDeflator)

        return df, data_name


    def show_GDP(self, data_source, description, data_name):

        indent_config = self.chart_config[data_name[:-2]]
        df, data_name = self.get_df(data_name)

        line_frame(data_name, df, indent_config = indent_config, description = description, source = data_source).show()





# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Path
# ~~~~~~~~~~~~~~~~~~~~~~~
# Note your current_dir is the path of py file that you run streamlit. In this case, is app.py
# Hence, current_dir is /home/.../[python]streamlit/project/lecture_data
current_dir = Path.cwd()



# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Page Layout
# ~~~~~~~~~~~~~~~~~~~~~~~
# If show border. Set to True when design. Set to False when publish.
border = False 
# horizontal and vertical alignment in container.
hor_align, ver_align = 'center', 'center'



# ~~~~~~~~~~~~~~~~~~~~~~~
# Load Config Files
# ~~~~~~~~~~~~~~~~~~~~~~~
###------Chart config------###
with open(os.path.join(current_dir, 'config', 'chart_config.json')) as f:
    chart_config = json.load(f)

# Set the width and height of container used to present chart.
chart_width = chart_config['chart']['chart_width']
chart_height = chart.get_chart_height(chart_config['chart']['WHratio'], chart_width)
# I leave another 30px so it has enough space to show icons such as "Customize" and "Download Data".
iframe_height = chart_height + 30



##############################
# Main Content
##############################

# ~~~~~~~~~~~~~~~~~~~~~~~
# Figure name
# ~~~~~~~~~~~~~~~~~~~~~~~

fig_list = [
    ###------National Income------###
    # nominal gdp
    "Gross domestic product (quarterly)",
    "Gross domestic product (annual)",
    # % share of ngdp
    "Percentage share of GDP (quarterly)",
    "Percentage share of GDP (annual)",
    # real gdp
    "Real gross domestic product (quarterly)",
    "Real gross domestic product (annual)",
    # nominal vs. rgdp
    'Nominal vs. real GDP',
    # Gross domestic income (GDI)
    "Gross domestic income (quarterly)",
    "Gross domestic income (annual)",


    ###------AD/AS------###
    "Business cycle and AD/AS model",
    
    
    ###------Monetary Policy------###
    "Monetary Policy and Interest Rate (monthly)",
    "Monetary Policy and Interest Rate (daily)",
        ]


fig_name = st.selectbox('Choose a dataset to display:', fig_list)
st.divider()

show_chart().show(fig_name, chart_config)







