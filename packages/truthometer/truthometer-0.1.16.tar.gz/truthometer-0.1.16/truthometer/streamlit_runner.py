import os
import streamlit.components.v1 as components
import streamlit as st
from pandas.io.clipboard import clipboard_get

import sys
sys.path.append('/Users/bgalitsky/Documents/true_gpt/making_chatgpt_truthful/truthometer/')
sys.path.append('/Users/bgalitsky/Documents/true_gpt/making_chatgpt_truthful')
sys.path.append('/Users/bgalitsky/Documents/true_gpt/making_chatgpt_truthful/truthometer/html')
sys.path.append('/Users/bgalitsky/Documents/true_gpt/making_chatgpt_truthful/truthometer/html/')
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

#https://github.com/dataprofessor/code/blob/master/streamlit/part3/penguins-app.py
from fact_checker_via_web import FactCheckerViaWeb

fact_checker = FactCheckerViaWeb()
st.write("""
# Truth-O-Meter App

This app does fact-checking of content produced by LLMs
""")

st.sidebar.header('Fact-checking features')

st.sidebar.markdown("""
[Example TXT input file]
""")

# Collects user input features into dataframe
uploaded_file = st.sidebar.file_uploader("Upload your input TXT file for fact-checking", type=["txt"])
if uploaded_file is not None:
    with open(uploaded_file) as f:
        text = f.readlines()
else:
    text = clipboard_get()

filename = fact_checker.perform_and_report_fact_check_for_text(text)
path = os.getcwd() + '/' + filename
HtmlFile = open(path, 'r', encoding='utf-8')
html_string = HtmlFile.read()
print(html_string)
components.html(html_string)

# or html_string = "<h3>this is an html string</h3>"
#
# st.markdown(html_string, unsafe_allow_html=True)

