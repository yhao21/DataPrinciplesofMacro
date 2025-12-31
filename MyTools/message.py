from MyTools.frequency_conversion import frequency_mapping
import streamlit as st



def get_hint_message(txt_input):
    return f"Hint: {txt_input}"


def format_message(text_input):
    return f"""
            {text_input}
            """

def list_message(message_list:list):
    return "\n".join(message_list)


class Message:
    """
    Use three quote for all messages.
    """

    def n_obs_surpass_the_limit(max_periods_to_show):
    
        return format_message(f"""
                Total number of observations cannot be greater than {max_periods_to_show}. 
                (Total number of observations = number of time periods X number of selected variables.)
        """)
    
    def change_sample_period():
        return format_message('Click on "Modify" to adjust sample period.')
    
    def convert_sample_frequency(freq):
        return format_message(f'The sample frequency is being converted to "{frequency_mapping(freq)}"')



    def get_recommend_last_period(first_period, derived_last_period):
        return format_message(f'Example Sample Period: First Period = {first_period}, Last Period = {derived_last_period}')
                
    
    def get_recommend_first_period(derived_first_period, last_period):
        return format_message(f'Example Sample Period: First Period = {derived_first_period}, Last Period = {last_period}')
    

