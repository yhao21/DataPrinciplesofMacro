import json, os
import altair as alt
import streamlit as st




alt.renderers.enable('png')

# ~~~~~~~~~~~~~~~~~~~~~~~
# Set path
# ~~~~~~~~~~~~~~~~~~~~~~~
current_dir = os.getcwd()


# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Page Layout
# ~~~~~~~~~~~~~~~~~~~~~~~
st.set_page_config(layout = 'wide')


# ~~~~~~~~~~~~~~~~~~~~~~~
# Initialize pages
# ~~~~~~~~~~~~~~~~~~~~~~~
###------Load page info------###
# Note, you MUST make sure that the name of python page files is consistent with the key in page_info.json.
# For example, key for the first topic is gdp, then you much name the python page file as index_<key>_.py
with open(os.path.join(current_dir, 'config', 'page_info.json')) as f:
    page_data = json.load(f)


###------Init page------###
topics = []
for name, page_info in page_data.items():
    default = True if name == 'home' else False

    page_name = f'{name}.py'
    one_page = st.Page(
            page = os.path.join(current_dir, 'pages', page_name),
            title = page_info['title'],
            url_path = page_info['url_path'],
            default = default
            )
    topics.append(one_page)


###------Organize pages on the sidebar------###
pages = {
        "Menu":topics
        }
pg = st.navigation(pages, position = 'top')
pg.run()

















