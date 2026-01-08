import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import json, os, warnings
import vl_convert as vlc

from MyTools.frequency_conversion import get_available_freq_list
from MyTools.frequency_conversion import frequency_dict
from MyTools.frequency_conversion import get_frequency
from MyTools.frequency_conversion import convert_frequency
from MyTools.frequency_conversion import get_frequency_level
from MyTools.frequency_conversion import frequency_mapping
from MyTools.frequency_conversion import get_YoY_window

from MyTools.load_data import get_percentage_share_GDP

from MyTools.message import get_hint_message
from MyTools.message import Message
from MyTools.message import list_message


# ~~~~~~~~~~~~~~~~~~~~~
# Formatting related functions
# ~~~~~~~~~~~~~~~~~~~~~

###------Description Format------###
def format_description(unit, source):
    return f"""
            Unit: {unit}

            Source: {source}
            """





###------Line Format------###
def get_format_module_title(txt_input):
    """
    Format the title for each sub module in "Format" dialog.
    """
    return f"### {txt_input}"


def default_line_format():
    return {
            "line_width": 3.0,
            "line_style":[1,0] # solid line
            }


def init_line_format(col_selected):
    """
    This function save format information for each line in a dictionary.
    {
        <line_name>:{
                        "line_style":[],
                        "line_width":float,
                        "line_color":string
                    }
    }
    """
    format_info = {}
    for i in col_selected:
        format_info[i] = default_line_format()
        format_info[i]['line_color'] = get_a_color()

    return format_info


def builtin_line_styles():
    """
    Return a dictionary contains built-in line styles (strokeDash).
    """
    return {
            "Solid":[1,0],
            "Dash":[10,7.5],
            "Short Dash":[5,3.5],
            "Long Dash":[20,15],
            "Dot":[2,10],
            "Short Dot":[2,3],
            "Dash Dot":[10,7,2,7],
            "Dash Dot Dot": [10,7,2,7,2,7],
            }


def line_style_mapping(value):
    """
    Given value is a list, return the name of corresponding line style defined in function <builtin_line_styles>.
    Given value is a name of line style, return the corresponding list used to specify altair line style (strkeDash).
    """
    line_style_dic = builtin_line_styles()
    return line_style_dic[value] if type(value) is str else list(line_style_dic.keys())[list(line_style_dic.values()).index(value)]


def standardize_col_name(col_name:list):
    """
    Format column name of df for plotting.
    """
    # format column names with :
    col_name = [
            i.replace('.', '').replace(':', '').replace("'", "")
            for i in col_name
            ]
    return col_name


def get_a_color():
    """
    Generate a hex code.
    """
    color_code = np.random.randint(0, 0xFFFFFF)
    hex_code = f"#{color_code:06x}"
    return hex_code


# ~~~~~~~~~~~~~~~~~~~~~
# Data format
# ~~~~~~~~~~~~~~~~~~~~~

def format_time_column_to_str(df):

    time_col = df['Time'].astype('string')
    return time_col





def get_chart_padding():
    return {"top": 5, "bottom":5, "left":50, "right":5}


def get_table_widget_info(table_name:str) -> dict:
    """
    This function returns a dict cotaining information for buttons.
    """
    widget_info = {
            "modify_button":{
                "label":"Modify",
                "key":f"{table_name}_modify_button"
                },
            "table_button":{
                "label":"Table",
                "key":f"{table_name}_table_button"
                },
            "chart_button":{
                "label":"Chart",
                "key":f"{table_name}_chart_button"
                },
            "format_button":{
                "label":"Format",
                "key":f"{table_name}_format_button"
                },
            "download_button":{
                "label":"Download Data",
                "key":f"{table_name}_download_button"
                },
            }
    return widget_info


def adjust_table_indent(df_show_index, indent_step:int = 4):
    """
    This function returns a df index that is indent-adjusted.
    """
    indent_config = st.session_state['indent_config']
    index = [f"{' ' * indent_config[i] * indent_step}{i}" for i in df_show_index]

    return index


def format_tooltip(cols):
    result = ['Time']
    for col in cols:
        result.append(alt.Tooltip(f"{col}:Q", format = ',.2f'))

    return result



def NumCol_accounting_format(cols:list) -> dict:
    """
    This function return a column format dict that let the number column take acounting form.
    """
    col_format = {}
    for col in cols:
        col_format[col] = st.column_config.NumberColumn(format = 'accounting')
    return col_format




def update_table_indent(state_name_df, state_name_adj_indent):
    """
    Adjust table indent.
    """
    st.session_state[state_name_df].index = adjust_table_indent(st.session_state[state_name_df].index)
    # Turn adjust indent signal to False
    st.session_state[state_name_adj_indent] = False


# ~~~~~~~~~~~~~~~~~~~~~~~
# Error messages
# ~~~~~~~~~~~~~~~~~~~~~~~

def show_warning_message(message:list):
    st.warning(list_message(message))


@st.dialog("Message", width = 'large')
def pop_up_message_window(message:list):
    st.warning(list_message(message))



# ~~~~~~~~~~~~~~~~~~~~~
# Condition
# ~~~~~~~~~~~~~~~~~~~~~




# ~~~~~~~~~~~~~~~~~~~~~
# Performance functions
# ~~~~~~~~~~~~~~~~~~~~~


def get_unit_info(current_dir):
    """
    Get unit info from ./config/unit_info.json
    """

    with open(os.path.join(current_dir, 'config', 'unit_info.json')) as f:
        unit_info = json.load(f)
    return unit_info

    






def check_modify_info(first_period, last_period, qrts_list:list, max_obs_to_show:int, table_mode:bool, selected_items:list, target_freq, raw_freq, is_all_period:bool):
    """
    df_periods: a list of all time periods in the raw df.
    """

    valid_modify_info = True
    error_message = []

    if is_all_period:
        first_period, last_period = qrts_list[0], qrts_list[-1]

    ###------Check validity of period selection------###
    if first_period > last_period:
        valid_modify_info = False
        error_message.append("Last Period cannot be smaller than the First Period")


    ###------Check if selected periods surpass the limit------###
    update_time_list = pd.period_range(first_period, last_period, freq = target_freq).to_list()



    ###------Check if selected periods surpass the limit------###
    # Only check maximum obs under "Chart" mode.
    if not table_mode:
        n_items = len(selected_items) if len(selected_items) > 0 else 1
        max_periods_each_item = max_obs_to_show // n_items
        n_periods = len(update_time_list)

        if n_periods > max_periods_each_item:
            recommend_first_period = update_time_list[(n_periods-1) - max_periods_each_item + 1]
            recommend_first_period = recommend_first_period.start_time.to_period(raw_freq)

            recommend_last_period = update_time_list[0 + max_periods_each_item - 1]
            recommend_last_period = recommend_last_period.end_time.to_period(raw_freq)


            valid_modify_info = False
            error_message.append(Message.n_obs_surpass_the_limit(max_obs_to_show))
            error_message.append(Message.get_recommend_first_period(recommend_first_period, last_period))
            error_message.append(Message.get_recommend_last_period(first_period, recommend_last_period))





    return valid_modify_info, error_message









def get_indexed_df(df):
    """
    This function return a df contains transformed indexed data, in which the the value for obs
    in the first period (first row) will be set to 100.

    Restriction: 
        The first column must be Time.
        Each row refers to obs from a period.
    Example of return df:

           Gross domestic product    ...  Nondefense  State and local
        0              100.000000    ...  100.000000       100.000000
        1              101.153131    ...  127.676428       102.973419
    """
    # Drop Time column
    df = df.drop('Time', axis = 1)
    indexed_first_row = df.iloc[0, :].values
    df = df/indexed_first_row * 100

    return df



def get_default_period(time_list:list, default_obs):
    """
    Return the first and last period given the value of prefered number of observations (default_obs).
    If default_obs = n > 0, return the begin and end period for the FIRST n obs.
    If default_obs = n <= 0, return the begin and end period for the LAST n obs.
    """
    if default_obs > 0:
        time_hor = time_list[:default_obs]
    else:
        time_hor = time_list[default_obs:]
    first_period, last_period = time_hor[0], time_hor[-1]


    return first_period, last_period



def get_table_df(df):
    """
    df: 
               Time  Gross domestic product  ...  Nondefense  State and local
        0    1947Q1                 243.164  ...       4.166           13.318
        1    1947Q2                 245.968  ...       5.319           13.714


    df.transpose() is the following:
                                                   0        1    ...        312        313
        Time                                    1947Q1   1947Q2  ...     2025Q1     2025Q2
        Gross domestic product                 243.164  245.968  ...  30042.113  30485.729
        Personal consumption expenditures      156.161  160.031  ...  20554.984  20789.926

    Returned df:
                                                1947Q1   1947Q2  ...     2025Q1     2025Q2
        Gross domestic product                 243.164  245.968  ...  30042.113  30485.729
        Personal consumption expenditures      156.161  160.031  ...  20554.984  20789.926
    """
    df = df.transpose()
    df.columns = df.loc['Time', :].values
    df = df.drop('Time')


    return df



def init_session_state(state_name, state_value):
    """
    Initialize the default value for session state.
    """
    if state_name not in st.session_state:
        st.session_state[state_name] = state_value


def get_plot_df(selected_index, state_name_df):
    """
    This function returns a df for ploting.

    st.session_state[state_name_df]:
                                              1947Q1 1947Q2  ...    2025Q1    2025Q2
        Gross domestic product                243.16 245.97  ... 30,042.11 30,485.73
        Personal consumption expenditures     156.16 160.03  ... 20,554.98 20,789.93
            Goods                              95.59  98.25  ...  6,432.30  6,471.11

    Returned plot_df:
               Gross domestic product Personal consumption expenditures    Goods Durable goods
        1947Q1                 243.16                            156.16    95.59         20.72
        1947Q2                 245.97                            160.03    98.25         21.35
    """
    index = st.session_state[state_name_df].index[selected_index].values
    plot_df = st.session_state[state_name_df].copy().loc[index, :].transpose()
    plot_df.columns = [i.strip() for i in plot_df] # remove indent.

    return plot_df
    






class line_frame():
    def __init__(
            self,
            data_name, # Must take this form: <name>-<platform>-<frequency>, valid frequency: "M", "Q", "A".
            df,
            description:str = 'test',
            box_height:int = 700,
            #box_height:int = 1200,
            height_offset = 60, # height of table and chart = box_height - height_offset.
            default_obs:int = -4,
            indent_config:dict = {},
            source:str = '',
            df_bg_line = [],
            show_zero = False,
            ):
        self.data_name = data_name
        self.df = df
        self.disable_download_chart = True
        self.description = description
        self.box_height = box_height
        self.height_offset = height_offset
        self.obs = default_obs
        self.indent_config = indent_config
        self.data_source = source
        self.df_bg_line = df_bg_line # it will be True if you call `add_baselines` to  add lines at the background.
        self.zero_line = show_zero
        self.current_dir = os.getcwd()
        self.unit_info = get_unit_info(self.current_dir)
        # Maximum num of periods to plot in the chart. The website may run slowly if this number is too large.
        self.max_periods_to_show = 8165 # 8165
        #self.max_periods_to_show = 10 # For testing purposes.
        self.initialize_session_state()
        self.freq = get_frequency(self.data_name)



    def get_recession_indicator_try(self, df_plot):
        # Rename column name to Time and Recession.
        recession_name = 'RECESSION-FRED-D'
        df = pd.read_csv(
                os.path.join('data', 'parse_data', f'{recession_name}.csv'),
                header = 0, # Ignore the first row (original column name).
                names = ['Time', 'Recession']
                )


        ###------Convert frequency of recession indicator to match the main dataset------###
        freq = st.session_state[self.state_name_freq]
        # set method = max, so mark that period (e.g., quarter) as recession if there is any period (e.g., day) is identified as recession.
        df = convert_frequency(df, freq, method = 'max') 

        ###------Match time periods between the recession dataset and main dataset------###
        start_period, end_period = df_plot['Time'].min(), df_plot['Time'].max()
        df = df.query(
                "Recession == 1 and Time >= @start_period & Time <= @end_period"
                ).reset_index(drop = True)
        df['Time'] = format_time_column_to_str(df)


        return df



    def init_default_df_to_show(self):
        ###------Format Time column and get first, last period------###
        # Convert values in Time column to string.
        self.df['Time'] = format_time_column_to_str(self.df)

        # Get start and end period
        first_period, last_period = get_default_period(list(self.df['Time']), self.obs)


        ###------Form dataset------###
        # df to show by default. By default, it shows the last four obs.
        # Do not format the indent of df until it is being persented in the box.
        df_show = self.df.query("Time >= @first_period and Time <= @last_period")
        df_show = get_table_df(df_show)
        return df_show, first_period, last_period


    def initialize_session_state(self):
        """
        When you need to define a new session state:
            First, assign its name to a class attribute (self.state_name_<variable name>)
            Second, append its value to dict "ss" through ss[self.state_name_<variable name>] = ...
        """
        df_show, first_period, last_period = self.init_default_df_to_show()

        ss = {}

        # Signal of highlighting horizontal axis when data are in percentage value.
        self.state_name_zero_line = self.key('zero_line')
        # Discription of chart
        self.state_name_description = self.key('description')
        # Used to save users choice of variable unit, such as "Level", "Percentage Change", ...
        self.state_name_var_unit = self.key('var_unit')
        # Used to save users choice of if to display data from "All Periods".
        self.state_name_all_periods = self.key('all_period_checkbox')
        # Used to save users choice of the first period of dataset.
        self.state_name_first_period = self.key('first_period')
        # Used to save users choice of the last period of dataset.
        self.state_name_last_period = self.key('last_period')
        # For df to show
        self.state_name_df = self.key('df_show')
        # For df to plot when user clicks "Chart" button.
        self.state_name_selected_cols = self.key('selected_cols')
        # For indent adjument signal
        self.state_name_adj_indent = self.key('adj_indent')
        # For table-chart switch signal
        self.state_name_show_table = self.key('show_table')
        # For modify signal
        self.state_name_modify_content = self.key('modify_content')
        # Signal of if Modify window is shown.
        self.state_name_show_modify_window = self.key('show_modify_window')
        # For line formats (line style, width, and color)
        np.random.seed(400) # Specify random seed to generate color scheme.
        self.state_name_line_format_info = self.key('line_format_info')
        # Signal for using shadow area to represent recession periods.
        self.state_name_show_recession = self.key('show_recession')
        # Recession area color
        self.state_name_recession_color = self.key('recession_color')
        # Recession area opacity
        self.state_name_recession_opacity = self.key('recession_opacity')
        # Signal for download_chart. It is false if user have not yet make the plot.
        self.state_name_disable_download_chart = self.key('allow_download_chart')
        # Signal for adjusting frequency because of reachiing max obs.
        self.state_name_have_adj_freq_since_max_obs = self.key('adj_freq_since_max_obs')
        # frequency
        self.state_name_freq = self.key('freq')
        # frequency before updating.
        self.state_name_previous_freq = self.key('previous_freq')
        # warning message
        self.state_name_freq_warning_message = self.key('freq_warning_message')



        ss[self.state_name_zero_line] = self.zero_line
        ss[self.state_name_description] = self.description
        ss[self.state_name_var_unit] = 'Level'
        ss[self.state_name_all_periods] = False
        ss[self.state_name_first_period] = first_period
        ss[self.state_name_last_period] = last_period
        ss[self.state_name_df] = df_show
        ss[self.state_name_selected_cols] = []
        ss[self.state_name_adj_indent] = True
        ss[self.state_name_show_table] = True
        ss[self.state_name_modify_content] = False
        ss[self.state_name_line_format_info] = init_line_format(standardize_col_name(self.df.columns.to_list()[1:]))
        ss[self.state_name_show_recession] = True
        ss[self.state_name_recession_color] = '#5F6463'
        ss[self.state_name_recession_opacity] = 0.2
        ss[self.state_name_var_unit] = 'Level'
        ss[self.state_name_all_periods] = False
        ss[self.state_name_first_period] = first_period
        ss[self.state_name_have_adj_freq_since_max_obs] = False
        ss[self.state_name_freq] = get_frequency(self.data_name)
        ss[self.state_name_previous_freq] = get_frequency(self.data_name)

        ss[self.state_name_freq_warning_message] = []

        for i in ss.keys():
            init_session_state(i, ss[i])

        # Generate new state each time
        st.session_state[self.state_name_show_modify_window] = False




    def unit_transformation(self, unit:str, df, data_name:str, original_description:str):
        """
        This function convert the df to a specific unit listed below.
    
        unit_list = [
                'Level',
                'Change', 'Change from Year Ago',
                'Percent Change', 'Percent Change from Year Ago',
                'Natural Log', 'Index'
                ]
        data_unit:  a certain unit above.
        """
        cols = df.columns.to_list()
        cols.remove('Time')
        freq = data_name[-1] # data frequency, such as M, Q, A.
        window = get_YoY_window(freq)
    
        result = df[['Time']]
        if unit == 'Level':
            result = df
            st.session_state[self.state_name_description] = original_description
        elif unit == 'Change':
            result = pd.concat([result, df[cols].diff(1)], axis = 1)
            st.session_state[self.state_name_description] = original_description
        elif unit == 'Change from Year Ago':
            result = pd.concat([result, df[cols].diff(window)], axis = 1)
        elif unit == 'Percent Change':
            result = pd.concat([result, df[cols].pct_change(periods = 1) * 100], axis = 1)
            st.session_state[self.state_name_description] = 'Percent, %'
        elif unit == 'Percent Change from Year Ago':
            result = pd.concat([result, df[cols].pct_change(periods = window) * 100], axis = 1)
            st.session_state[self.state_name_description] = 'Percent, %'
        elif unit == 'Natural Log':
            result = pd.concat([result, np.log(df[cols])], axis = 1)
            st.session_state[self.state_name_description] = 'Natural Log'
        elif unit == 'Index':
            df_indexed = get_indexed_df(df)
            result = pd.concat([result, df_indexed], axis = 1)
            st.session_state[self.state_name_description] = 'Index (Scale Value to 100 for The First Period)'
    
        return result
    




        
    def show(self, n_legend_cols:int = 4):
        """
        This function returns a format chart which allow you to select a particular column to plot.


        df: dataframe contains data. 
             Time     Gross domestic product  Personal consumption expenditures  ...  State and local  
            1947Q1                   243.164                            156.161  ...           13.318  
            1947Q2                   245.968                            160.031  ...           13.714  
            1947Q3                   249.585                            163.543  ...           14.324  
        default_obs: a NON-ZERO numerical value,
                        If it is 4, then show data in the first 4 years.
                        If it is -4, then show data in the last 4 years.
                        If user mistakenly pass a 0, then replace it by -4.

        indent_config: a dict contains indent info for the variable name in the table.
                       Example:
                                    {"Gross domestic product":0,
	    			"Personal consumption expenditures":0,
	    			"Goods":1}
        """

        # Allow altair to deal with a dataset with more than 5000 obs.
        alt.data_transformers.disable_max_rows()

        ###------Container for description and buttons------###
        container = st.container(
                border = False,
                horizontal_alignment = 'left', vertical_alignment = 'bottom',
                horizontal = True
                )

        # Button config
        button_config = get_table_widget_info(self.data_name)
        button_modify = button_config['modify_button']
        button_table = button_config['table_button']
        button_chart = button_config['chart_button']
        button_format = button_config['format_button']
        button_download = button_config['download_button']


        with container:

            ###------Data Description------###
            if self.data_source:
                st.write(
                        format_description(
                            st.session_state[self.state_name_description],
                            self.data_source
                            )
                        )
            else:
                st.write(st.session_state[self.state_name_description])

            st.space() # add space, so all bottoms align to the right.

            ###------Modify button------###
            if st.button(button_modify['label'], button_modify['key']):
                self.modify_BEA_table()

            ###------Table button------###
            if st.button(button_table['label'], button_table['key']):
                st.session_state[self.state_name_show_table] = True

            ###------Chart button------###
            if st.button(button_chart['label'], button_chart['key']):
                st.session_state[self.state_name_show_table] = False

            ###------Format button------###
            if st.button(
                    button_format['label'],
                    button_format['key'],
                    disabled = st.session_state[self.state_name_show_table]
                    ):
                self.format_lines_in_chart()

            ###------Download data button------###
            st.download_button(
                    label = button_download['label'],
                    key = button_download['key'],
                    data = self.get_download_csv(st.session_state[self.state_name_df]),
                    file_name = self.download_file_name(self.data_name, '.csv')
                    )



        ###------Container of data table------###
        box = st.container(border = False, horizontal_alignment = 'left', vertical_alignment = 'top', height = self.box_height, key = self.key('DataTableFrame'), horizontal = True)

        with box:
            # If pass indent config file, then format table index.
            if self.indent_config and st.session_state[self.state_name_adj_indent]:
                st.session_state['indent_config'] = self.indent_config
                update_table_indent(self.state_name_df, self.state_name_adj_indent)

            if st.session_state[self.state_name_show_table]: # show table
                self.show_table()
            else: # show chart
                self.show_chart(n_legend_cols = n_legend_cols)

            

    @st.dialog("Choose Time Horizon", width = 'medium')
    def modify_BEA_table(self):
        st.session_state[self.state_name_show_modify_window] = True
    
        qrts_list = list(self.df['Time'].values)
        with st.form(f'{self.data_name}_modify'):
            # Selectbox: First period.
            first_period = st.selectbox(
                    'First Period:',
                    options = qrts_list,
                    key = self.key('st'),
                    index = qrts_list.index(st.session_state[self.state_name_first_period])
                    )

            # Selectbox: Last period.
            last_period = st.selectbox(
                    'Last Period:',
                    options = qrts_list,
                    key = self.key('et'),
                    index = qrts_list.index(st.session_state[self.state_name_last_period])
                    )
            

            frequency_name_to_short = {v:k for k,v in frequency_dict().items()}
            freq_list = get_available_freq_list(self.data_name)
            data_freq = st.selectbox(
                    'Frequency',
                    options = freq_list,
                    key = self.key('List_of_data_frequency'),
                    index = freq_list.index(
                        frequency_mapping(st.session_state[self.state_name_freq])
                        )
                    )
            freq = frequency_name_to_short[data_freq]
            original_freq = get_frequency(self.data_name)




    
            # Check box: if to plot data in all periods.
            st.session_state[self.state_name_all_periods] = st.checkbox(
                    'All Periods',
                    key = self.key('AllPeriods'),
                    value = st.session_state[self.state_name_all_periods]
                    )

            if st.session_state[self.state_name_all_periods]:
                first_period, last_period = qrts_list[0], qrts_list[-1]



            ###------Select data unit------###
            unit_list = list(self.unit_info.keys())

            data_unit = st.selectbox(
                    'Units',
                    options = unit_list,
                    key = self.key('data_unit'),
                    index = unit_list.index(st.session_state[self.state_name_var_unit])
                    )

            st.session_state[self.state_name_var_unit] = data_unit

            ###------Decide if to show y = 0------###
            st.session_state[self.state_name_zero_line] = True if self.unit_info[data_unit]['percentage value'] or self.zero_line else False

            ###------Submit button------###
            submit = st.form_submit_button('Refresh Table', key = self.key('ModifySubmit'))
            if submit:
                valid_modify_info, error_message = check_modify_info(
                        first_period, last_period, qrts_list, self.max_periods_to_show,
                        st.session_state[self.state_name_show_table],
                        st.session_state[self.state_name_selected_cols],
                        freq, original_freq,
                        st.session_state[self.state_name_all_periods]
                        )

                if valid_modify_info:
                    #st.session_state[self.state_name_freq] = freq
                    self.update_freq(freq)
                    self.update_modify_info(first_period, last_period, data_unit, freq, original_freq)
                else:
                    st.warning(list_message(error_message))

            







    def update_modify_info(self, first_period, last_period, data_unit, freq, original_freq):
        """
        Update modified information.
        """
        df = self.df

        if freq != original_freq:
            df = convert_frequency(df, freq, original_freq=st.session_state[self.state_name_previous_freq])
        target_first_period = str(pd.Period(first_period).start_time.to_period(freq))
        target_last_period = str(pd.Period(last_period).end_time.to_period(freq))





        # Update first and last period to session state.
        st.session_state[self.state_name_first_period] = first_period
        st.session_state[self.state_name_last_period] = last_period

        # Save filtered df. Query at the end so it will not miss the first obs for terms such as "change" and "% change".

        if self.unit_info[data_unit]['difference term']:
            df_show = self.unit_transformation(
                    data_unit,
                    #self.df,
                    df,
                    self.data_name,
                    self.description
                    ).query('Time >= @target_first_period and Time <= @target_last_period')
        else:
            df_show = self.unit_transformation(
                    data_unit,
                    df.query('Time >= @target_first_period and Time <= @target_last_period'),
                    self.data_name,
                    self.description
                    )


        # Adjust indent for variable column.
        df_show = get_table_df(df_show)
        st.session_state[self.state_name_df] = df_show
        # Reset adjust df indent signal since new df is formed.
        if self.indent_config:
            st.session_state[self.state_name_adj_indent] = True
        else:
            st.session_state[self.state_name_adj_indent] = False
            
        st.session_state[self.state_name_modify_content] = True

        st.rerun()


    
    @st.dialog("Lines Format")
    def format_lines_in_chart(self):
        """
        Allow users to format lines.
        """
        disable_save_button = True
        with st.form(f'form_format_{self.data_name}'):
            self.recession_period_module()
            
            Format_info = {} # A dict to save format info for each line.
            # Users need to select at least one data series, otherwise hide format setups and disable "save" button.
            if st.session_state[self.state_name_selected_cols]:
                disable_save_button = False
                for one_line_name in standardize_col_name(st.session_state[self.state_name_selected_cols]):
                    format_module, one_format_info = self.line_format_module(one_line_name)
                    Format_info[one_line_name] = one_format_info

            else:
                st.write("Please first select one or more data series listed on the left side.")


            ###------Submit buton------###
            submit = st.form_submit_button('Save', key = self.key('FormatSubmit'), disabled = disable_save_button)

            if submit:
                for one_line_name in Format_info.keys():
                    st.session_state[self.state_name_line_format_info][one_line_name] = Format_info[one_line_name]

                st.rerun()


    def recession_period_module(self):
        container = st.container(border = True)
        with container:
            st.write(get_format_module_title("General Setup"))
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

            toggle_list = [True, False]
            st.session_state[self.state_name_show_recession] = col1.selectbox(
                    "Show Recession Periods",
                    options = toggle_list,
                    key = f'toggle_recession_area_{self.data_name}',
                    index = toggle_list.index(st.session_state[self.state_name_show_recession])
                    )
            st.session_state[self.state_name_recession_color] = col2.color_picker(
                    'Color',
                    value = st.session_state[self.state_name_recession_color],
                    key = f'recession_color_picker_{self.data_name}'
                    )
            st.session_state[self.state_name_recession_opacity] = col3.number_input(
                    'Opacity',
                    min_value = 0.0,
                    max_value = 0.2,
                    value = st.session_state[self.state_name_recession_opacity],
                    key = f'recession_opacity_picker_{self.data_name}'
                    )


    def line_format_module(self, line_name:str):
        """
        Return a standardize module that allows user to customize the style, width, and color of a line.
            line_width      line_style      color
        """
        # A list of names for built-in line styles.
        line_style_list = list(builtin_line_styles().keys())
        # location index of line style name to show in "line_style_list".
        default_index = line_style_list.index(line_style_mapping(st.session_state[self.state_name_line_format_info][line_name]['line_style']))

        container = st.container(border = True)
        with container:
            st.write(get_format_module_title(line_name))
            with st.container(horizontal = True, vertical_alignment = 'center'):
                col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
                line_width = col1.number_input(
                        'Line width',
                        min_value = 1.0,
                        key = f'line_width_{line_name}',
                        value = st.session_state[self.state_name_line_format_info][line_name]['line_width']
                        )
                line_style = col2.selectbox(
                        'Line style',
                        key = f'line_style_{line_name}',
                        options = line_style_list,
                        # Use index to specify default value. It saves the latest change.
                        index = default_index
                        )
                line_color = col3.color_picker(
                        'Color',
                        key = f'line_color_{line_name}',
                        value = st.session_state[self.state_name_line_format_info][line_name]['line_color']
                        )
    
        return container, {"line_width":line_width, "line_style":line_style_mapping(line_style), "line_color":line_color}
        
    
    def show_table(self):
        df = st.session_state[self.state_name_df]
        df.columns = df.columns.astype('string')
    
        st.dataframe(
                df,
                height = self.box_height - self.height_offset,
                column_config = NumCol_accounting_format(st.session_state[self.state_name_df].columns),
                key = self.key('DataTableContent')
                )
    
    
    
    def show_chart(self, n_legend_cols = 4, border = False):

        content_height = self.box_height - self.height_offset
        df = st.session_state[self.state_name_df]
    
        # Adjust indent
        if st.session_state[self.state_name_modify_content] and st.session_state[self.state_name_adj_indent]:
            update_table_indent(self.state_name_df, self.state_name_adj_indent)

        ###------A list of variables to plot (left side)------###
        gdp_items = st.dataframe(
                    pd.DataFrame(df.index, columns = ['Select data series to plot:']),
                    on_select = 'rerun',
                    selection_mode = 'multi-row',
                    hide_index = True,
                    height = content_height - 30,
                    key = self.key('ChartLeftBoxList'),
                    width = 300
                )
        # a list of index for rows being selected, such as [0, 1, 2].
        selected_items = gdp_items.selection['rows']
    
        ###------Chart (right side)------###
        plot_df = get_plot_df(selected_items, self.state_name_df)
        # Update selected col to session state for formatting lines.
        st.session_state[self.state_name_selected_cols] = plot_df.columns.to_list()

        if len(self.df_bg_line):
            plot_df = self.append_bg_line(plot_df)

        # Show chart only if users select one or more items.
        if selected_items:

            plot_df = self.get_freq_adj_df(
                    plot_df,
                    st.session_state[self.state_name_freq],
                    set_original_freq = st.session_state[self.state_name_freq]
                    )
            n_obs = plot_df.shape[0] * plot_df.shape[1]


            if n_obs <= self.max_periods_to_show:
                self.display_chart(plot_df, content_height, n_legend_cols)
            else:
                plot_df, message, is_highest_freq_level = self.adjust_data_frequency(plot_df)
                st.session_state[self.state_name_freq_warning_message] = message

                ###------Convert frequency------###
                # If not reach highest frequency level, show chart, else, hide chart.
                if not is_highest_freq_level:
                    # Only pop up window when frequency is changed.
                    if (
                            st.session_state[self.state_name_have_adj_freq_since_max_obs] 
                            and not st.session_state[self.state_name_show_modify_window]
                        ):
                        pop_up_message_window(message)
                        
                    ###------Display chart------###
                    self.display_chart(plot_df, content_height, n_legend_cols)
                else:
                    if not st.session_state[self.state_name_show_modify_window]:
                        pop_up_message_window(message)





    def get_freq_adj_df(self, df, freq, set_original_freq = None):
        if set_original_freq == None: # If use does not pass a value, use previous_freq.
            set_original_freq = st.session_state[self.state_name_previous_freq]

        df['Time'] = df.index.astype(str)
        df = convert_frequency(df, target_frequency=freq, original_freq=set_original_freq)
        df['Time'] = df['Time'].astype('string')
        df = df.set_index('Time')

        return df

    

    def adjust_data_frequency(self, df):

        freq = st.session_state[self.state_name_freq]
        is_highest_freq_level = False
        while df.shape[0] * df.shape[1] > self.max_periods_to_show:
            if freq == get_frequency_level(freq_index = -1): # If already the highesst freq level.
                is_highest_freq_level = True
                break
            else:
                freq = get_frequency_level(freq_index = get_frequency_level(freq) + 1)

            df = self.get_freq_adj_df(df, freq)


        # If 
        if freq != st.session_state[self.state_name_freq]:
            st.session_state[self.state_name_have_adj_freq_since_max_obs] = True
            #st.session_state[self.state_name_freq] = freq
            self.update_freq(freq)
        else:
            st.session_state[self.state_name_have_adj_freq_since_max_obs] = False

        message =  [Message.n_obs_surpass_the_limit(self.max_periods_to_show)]

        if is_highest_freq_level:
            message.append(Message.change_sample_period())
        else:
            message.append(Message.convert_sample_frequency(freq))


        return df, message, is_highest_freq_level







    def display_chart(self, plot_df, content_height, n_legend_cols):
        # Hide grid line for both axis.
        chart = self.get_chart_lines(plot_df, content_height, n_legend_cols = n_legend_cols).configure_axis(grid = False)
        st.altair_chart(chart, key = self.key('ChartRightBoxChart'), width = 'stretch')


    def get_chart_lines(self, df, content_height:int, n_legend_cols = 4):
        """
        Return a line chart.
    
        bg_lines:   An alt.Chart() item, e.g., a plot of growth rate of gdp.
                    If you pass a `bg_lines`, this function will add `bg_lines` (an alt chart item) to the main chart.
        zero_line:  If True, draw y = 0 in chart. Usually used in growth rate chart.
    
        """


        ###------Standardize column name for df------###
        df.columns = standardize_col_name(df.columns.to_list())
        col_selected = df.columns.to_list()
        df['Time'] = df.index.values.astype(str)    # convert time column to string
        df = df[['Time'] + col_selected].reset_index(drop = True)


        ###------Get df for bar chart------###
        # Replace all empty values in df with 0, so the bar chart can cover all time periods in df.
        df_bar = df[['Time'] + [df.columns[1]]].fillna(0)

    
        ###------Define height for elements------###
        #bar_height = 0.07 * content_height
        bar_height = 0.04 * content_height
        legend_height = 0.25 * content_height
        chart_height = content_height - bar_height - legend_height
    
    
        ###------Define selector------###
        selector = alt.selection_point(
                nearest = True,
                on = 'pointerover',
                clear = 'pointerout',
                empty = False
                )
    
        bar_selector = alt.selection_interval(encodings = ['x'])

        legend_selector = alt.selection_point(
                fields = ['key'],
                bind = 'legend',
                on = 'click',
                clear = 'dblclick',
                )
    
        ###------Define spike line------###
        rule_tooltip = format_tooltip(col_selected)
        rule = alt.Chart(df).mark_rule(color = 'grey').encode(
                x = 'Time:N',
                #y = alt.value(0),
                y2 = alt.value('height'),
                opacity = alt.condition(selector, alt.value(1), alt.value(0)),
                tooltip = rule_tooltip,
                ).add_params(selector).transform_filter(bar_selector)
    
    
        ###------Define lines------###
        lines = alt.Chart(df).transform_fold(col_selected).mark_line().encode(
                x = alt.X(
                    'Time:N',
                    title = None,
                    axis = alt.Axis(
                        labelAngle = 0,
                        labelAlign = 'center' # center the tick label.
                        )
                    ).scale(zero = False),
                y = alt.Y('value:Q', title = None).scale(zero = False),
                color = alt.Color(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_color'] for i in col_selected]
                        ),
                    legend = alt.Legend(
                        title = None,
                        titleLimit = 1500,
                        orient = 'bottom',
                        direction = 'horizontal',
                        columns = n_legend_cols,
                        labelLimit = 500,
                        symbolSize = 400,
                        symbolStrokeWidth = 4,
                        offset = 0, # Distance between legend and chart. Smaller -> Closer.
                        ),
                    # Legend is arranged in the same order as in self.df
                    sort = list(st.session_state[self.state_name_line_format_info].keys())
                    ),

                size = alt.Size(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_width'] for i in col_selected] if len(col_selected) > 1 else [st.session_state[self.state_name_line_format_info][col_selected[0]]['line_width'], st.session_state[self.state_name_line_format_info][col_selected[0]]['line_width'] - 0.01]
                        ),
                    # If I set legend = None, if will overlap with the color legend, and the symbol
                    # will not present properly (clipped). I have not yet figure out how to solve
                    # this problem, so I simply put the Size legend on the left of chart and 
                    # set the strokewidth to 0 to hide it.
                    legend = alt.Legend(
                        orient = 'left', values = [''], title = None, symbolStrokeWidth = 0
                        )
                    ),

                strokeDash = alt.StrokeDash(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_style'] for i in col_selected]
                        ),

                    legend = None
                    ),

                opacity = alt.condition(
                    legend_selector,
                    alt.value(1),
                    alt.value(0.2)
                    ),
                ).add_params(legend_selector).transform_filter(bar_selector).properties(height = chart_height)
    
        ###------If zero_line = True, show zero line (y = 0)------###
        #zero_mark_opacity = alt.value(0)
        #if st.session_state[self.state_name_zero_line]:
        #    zero_mark_opacity = alt.value(1)
    
        zero_mark = alt.Chart(df).mark_line(color = 'grey', size = 3).encode(
                x = 'Time:N',
                y = alt.datum(0),
                #opacity = zero_mark_opacity,
                ).transform_filter(bar_selector)

        ###------Add selection bar below the chart------###
        bar = alt.Chart(df_bar).mark_bar(color = 'grey').encode(
                x = alt.X('Time:N', title = None, axis = None),
                y = alt.value(1),
                #opacity = alt.condition(bar_selector, alt.value(.4), alt.value(0.2)),
                opacity = alt.value(0),
                tooltip = alt.Tooltip('Time:N', title = ' '),
                ).add_params(
                        bar_selector
                ).properties(
                        height = bar_height,
                        title = alt.Title(
                            #"Drag in the bar chart below to select a period of time.",
                            text = [
                                get_hint_message(
                                # Use .join, so there will not be a large gap between each sentence when users download the chart.
                                " ".join([
                                    "Drag the bar above to adjust selected time periods.",
                                    "Click on unselected area to restore the default period."
                                    ])
                                ),
                                get_hint_message(
                                " ".join([
                                    "Click on one of the items below to highligh a single line.",
                                    "Hold Shift button and click to select multiple items.",
                                    "Double click in the main chart to restore default setup."
                                    ])
                                ),
                                get_hint_message("Shaded areas indicate U.S. recessions.")
                                ],
                            fontSize = 14,
                            fontWeight = 400, # normal text: 400, bold: larger number, e.g., 800
                            offset = 5, # The distance between title and chart, the smaller the closer.
                            orient = 'bottom'
                            )
                )

        ###------Recession periods------###
        df_recession = self.get_recession_indicator_try(df)
        recession_periods = alt.Chart(df_recession).mark_rect(stroke = None).encode(
                x = 'Time:N',
                opacity = alt.value(st.session_state[self.state_name_recession_opacity]),
                color = alt.value(st.session_state[self.state_name_recession_color])
                ).transform_filter(bar_selector)


    
        ###------Merge chart items------###
        chart = alt.layer(rule, lines)

        # If zero_line = True, show zero line (y = 0)
        if st.session_state[self.state_name_zero_line]:
            chart = alt.layer(chart, zero_mark)
        # Show recession periods if triggered.
        if st.session_state[self.state_name_show_recession]:
            chart = alt.layer(chart, recession_periods)
    

        # Use configure_view to change color and size of the chart border.
        chart = (chart & bar).configure_view(stroke = 'grey', strokeWidth = .2)

        return chart
    

    def update_freq(self, freq):
        """
        Up date frequency to session state and record previous frequency.
        """
        st.session_state[self.state_name_previous_freq] = st.session_state[self.state_name_freq]
        st.session_state[self.state_name_freq] = freq



    
    def key(self, key_name):
        """
        This function returns a key name for your streamlit elements
        """
        return f'{self.data_name}_{key_name}'

    def download_file_name(self, file_name:str, file_type:str):
        """
        file_name: by default, it will be self.data_name
        file_type: .csv, .pdf, .png...
        """
        first_period = st.session_state[self.state_name_first_period]
        last_period = st.session_state[self.state_name_last_period]
        return f"EconData_{file_name.split('-')[0]}_Period_{first_period}_to_{last_period}.{file_type}"

    def get_download_csv(self, df):
        """
        Return a csv for user to download.
        """
        return df.to_csv()

    def get_download_png(self, chart_item):
        """
        chart_item: an altair chart.
        """
        return vlc.vegalite_to_png(chart_item.to_json(), scale = 2)

            
    def append_bg_line(self, df):
        """
        This function append columns in df_bg_line to the main df so they will be ploted
        together.
        """

        first_period, last_period = df.index.min(), df.index.max()
        df_bg = self.df_bg_line
        df_bg['Time'] = format_time_column_to_str(df_bg)
        df_bg.index = df_bg['Time'].values
        df_bg = (df_bg
                .query("Time >= @first_period and Time <= @last_period")
                .drop('Time', axis = 1)
                )
        df = pd.concat([df, df_bg], axis = 1)

        return df
                    


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

#   ______________________________________________________________
#  |                                 |                            |
#  | Description                     |     Modify | Table | Chart |
#  |_________________________________|____________________________|
#   _______________  _____________________________________________
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |   columns     ||               chart                         |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |_______________||_____________________________________________|
#  
#
#    Requirement:
#        1. a dataframe
#        2. an indent config file (optional). If not, the program will not adjust indent for the first column (index) of df.
#
#    Instruction:
#        Call `line_frame(data_name, df, indent_config, description, source).show()` to present the chart/table frame.
#
#        data_name:      the name of dataset, also, it will be the flag of key for streamlit components.
#        df:             dataframe
#        indent_config:  [optional] a dictionary contains configure info to adjust indent of the first column/index of your presented dataframe.
#        Description:    [optional]Text used to explain the table. It will show up at the top left corner of the frame.
#        source:         [optional]Text will hyperlink (in markdown form) that tells the data source. It will show up below the Description.
#                        Example: 
#                            source_bea, source_fred = '[BEA](your_url)', '[FRED](your_url)'
#                            source = f'{source_bea}, {source_fred}' # This is the one you pass to `line_frame`.
#        df_bg_line:     Dataframe contains the data you want to show in chart but not in table. 
#                        For example, the main df contains the growth rate of C, I, G, and NX. And you want to include the growth rate of RGDP in the chart, but you do not want to show
#                        the growth rate of RGDP in table.
#                            1. The first column must be 'Time', and its value must be consistent with the main df, e.g., if Time in df is 2020Q1, then Time in df_bg_line must also
#                                be 2022Q1, 2024Q1, ... It CANNOT be in other form, such as 2024-01-01.
#
#    Column name format:
#        If column name contains special characters such as ".", ":", you must specify how to replace those characters in function <standardize_col_name()>.
#








    st.set_page_config(layout = 'wide')

    percentage_share_of_GDP = False

    data_name = 'NGDP-BEA-Q'
    #data_name = 'RGDP-BEA-A'
    df = pd.read_csv(f'../../data/{data_name}.csv')

    if percentage_share_of_GDP:
        # get % share of GDP
        df = get_percentage_share_GDP(df)

    ###------Format Data Source------###
    source_bea = '[BEA](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*1dmdvxn*_ga*MTQ5ODgyNDYwNS4xNzM2Nzc1ODM1*_ga_J4698JNNFT*czE3NjM3Mzc2NjUkbzIyJGcxJHQxNzYzNzM3NjY5JGo1NiRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI1Il1dfQ==)'
    source_unemployment = '[FRED](https://fred.stlouisfed.org/series/UNRATE)'

    data_source = f"{source_bea}, {source_unemployment}"

    ###------Load indent config file for row index of table------###
    with open('./config/chart_config.json') as f:
        indent_config = json.load(f)[data_name[:-2]]


    #line_frame(data_name, df, indent_config = indent_config, description = '[Billions of dollars] Seasonally adjusted', source = data_source).show()




    ###------Federal funds effective rate------###
    data_name = "FFER-FRED-D"
    df = pd.read_csv(f'../../data/{data_name}.csv')
    line_frame(data_name, df, description = '[Billions of dollars] Seasonally adjusted', source = data_source).show()



    #=====================================================
    # ~~~~~~~~~~~~~~~~~~~~~
    # Example of plotting both the main df and background lines as comparison.
    # ~~~~~~~~~~~~~~~~~~~~~
#
#    data = pd.read_csv('../../data/RGDP-BEA-A.csv')
#    df_line = data[['Time']]
#    df_line['Growth Rate of RGDP'] = (data['Gross domestic product'].pct_change() * 100).round(2)
#
#
#    line_frame(data_name, df, indent_config = indent_config, description = '[Billions of dollars] Seasonally adjusted', source = data_source, df_bg_line = df_line, show_zero = True).show()
#
#








    """
    To do list:
        Bugs:

        New functions:
            -- Add a button: Add/Remove Line
            

            -- Button integration:
                -- Put "Modify", "Format", "Add/Remove Line" under a dialog triggered by button "Edit Graph"


        User experience improvement:
            -- Automatic convert frequncy when obs is greater than 2000.

            -- Add a "Format" button next to "Chart" to achieve the following functionalities.
                -- Change the following chart format:
                    -- log scale axis
                    -- recession shading (if to show recession area in grey.)





        
    """





