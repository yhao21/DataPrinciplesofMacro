import streamlit as st
import os



"""
# Instruction

### Section 1: Time Series Data
Users can track real-time economic data on `Time Series Data` page. To get there, please click on `Menu`
on the top left, and then click on `Time Series Data`.

#### Data Selection
Users can choose any datasets in the drop-down list to display. By default, the web page presents
the data from the most recent four periods. Users can adjust the sample period and frequency 
by clicking on `Modify` button on the right side above the table. You will see a pop-up window.
"""
image_data_selection = st.container(horizontal_alignment = 'center')
image_data_selection.image(os.path.join(os.getcwd(), 'figures', 'data_selection.png'))

"""
#### Modify Data Selection
In the pop-up window, users can either select a
customized sample period (by setting a pair of `First Period` and `Last Period`) or choose to
present the full sample (by checking `All Periods`). Note, once you check
`All Periods`, it will override the customized first and last periods you set.
Users can also choose to set units for the data in the `Units` box.
"""
image_modify_window = st.container(horizontal_alignment = 'center')
image_modify_window.image(os.path.join(os.getcwd(), 'figures', 'modify_window.png'))

"""
#### Chart Mode
Users can visualize the data by clicking on `Chart` button. In the chart mode, you will see the list 
of variables in the dataset on the left side. Check the box in front of the variable name to plot
certain data series. Move your mouse to and check the box in front of `Select data series to plot` to 
select/remove all variables. Note, users can still adjust the sample period by clicking on `Modify`
button in the chart mode.
"""
image_chart_mode = st.container(horizontal_alignment = 'center')
image_chart_mode.image(os.path.join(os.getcwd(), 'figures', 'chart_mode.png'))

"""
#### Format Chart Elements
In the chart mode, users can adjust the features of the chart by clicking on `Format` button.
In the `General Setup` module, users can choose to adjust the visibility, color, and the opacity 
of recession periods. The format options for each selected data series are listed below the
`General Setup` module. Users can adjust the width, style, and the color for each line.
"""
image_format_window = st.container(horizontal_alignment = 'center')
image_format_window.image(os.path.join(os.getcwd(), 'figures', 'format_window.png'))

