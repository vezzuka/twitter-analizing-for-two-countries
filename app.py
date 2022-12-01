# Twitter Dashboard Group Challenge

# Import Packages
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
from plotly.subplots import make_subplots

@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

# Set Streamlit title and header
st.set_page_config(page_title='Twitter Analysis 2022',
                   page_icon='random',
                   layout='wide') # 'wide' or 'centered'

st.title('Analysis of tweeting behaviour and engagement from high profile users in 2022')

tab1, tab2, tab3 = st.tabs(['Category Analysis', 'User Analysis', 'Time Series'])

with tab1:
   st.header("A cat")
   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

with tab2:
   st.header("A dog")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)