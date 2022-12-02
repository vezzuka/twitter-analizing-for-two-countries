# Twitter Dashboard Group Challenge

# Import Packages
import streamlit as st
import pandas as pd
import json
from urllib.request import urlopen
from copy import deepcopy

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
#import matplotlib.plotly as plt

@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

# Load clean data from data folder
df1 = pd.read_csv('./data/tweets_clean.csv')
tweets_clean = deepcopy(df1)

# Create a df aggregating by category for total and mean actions
tweets_agg = tweets_clean.groupby('category').agg({'name': 'nunique',
                                                   'id': 'count',
                                                   'replyCount': ['sum', 'mean'],
                                                   'retweetCount': ['sum', 'mean'],
                                                   'likeCount': ['sum', 'mean'],
                                                   'quoteCount': ['sum', 'mean']
                                                  })

tweets_agg.columns = tweets_agg.columns.droplevel()
tweets_agg.columns = ['Users_Analysed', 'Total_Tweets',
                      'Total_Replies', 'Mean_Replies',
                      'Total_Retweets', 'Mean_Retweets',
                      'Total_Likes', 'Mean_Likes',
                      'Total_Quotes', 'Mean_Quotes']

tweets_agg.reset_index(inplace=True)

# Create a df aggregating by sourceLabel for pie chart
source_dict_pie = {'Twitter for iPhone': 'Iphone',
                   'Twitter for iPad': 'iPad',
                   'Twitter for Android': 'Android',
                   'Twitter for Mac': 'Other',
                   'Twitter Web App': 'Web App',
                   'Twitter Media Studio': 'Media Studio',
                   'Twitter Media Studio - LiveCut': 'Media Studio',
                   'The White House': 'The White House',
                   'TweetDeck': 'Other',
                   'Periscope': 'Periscope',
                   'Arrow.': 'Other'}

tweets_source_pie = tweets_clean.replace(source_dict_pie).groupby('sourceLabel').agg({'id': 'count'}).reset_index()
tweets_source_pie.rename({'id': 'Tweets'}, axis=1, inplace=True)

# Create a df aggregating by sourceLabel AND category
source_dict = {'Twitter for iPhone': 'Iphone',
               'Twitter for iPad': 'iPad',
               'Twitter for Android': 'Android',
               'Twitter for Mac': 'Mac',
               'Twitter Web App': 'Web App',
               'Twitter Media Studio': 'Media Studio',
               'Twitter Media Studio - LiveCut': 'Media Studio',
               'The White House': 'The White House',
               'TweetDeck': 'TweetDeck',
               'Periscope': 'Periscope',
               'Arrow.': 'Arrow'}

tweets_cns = tweets_clean.replace(source_dict).groupby(['category', 'sourceLabel']).agg({'id': 'count' }).reset_index()
tweets_cns.rename({'sourceLabel': 'Device', 'id': 'Tweets'}, axis=1, inplace=True)
cns_df = tweets_cns.fillna(0)

# Create a df aggregating by sourceLabel AND name
tweets_name = tweets_clean.replace(source_dict_pie).groupby(['name']).agg({'id': 'count' }).reset_index()
tweets_name.rename({'id': 'Total'}, axis=1, inplace=True)

tweets_nns = tweets_clean.replace(source_dict_pie).groupby(['name', 'sourceLabel']).agg({'id': 'count' }).reset_index()
tweets_nns.rename({'sourceLabel': 'Device', 'id': 'Tweets'}, axis=1, inplace=True)
nns_df = tweets_nns.fillna(0)

platform_usage = tweets_nns.merge(tweets_name, on='name', how='left')
platform_usage['percent'] = round(platform_usage['Tweets']/platform_usage['Total']*100, 1)

# Pie Chart - Device Distribution
cat_plat = go.Figure(go.Pie(labels=tweets_source_pie['sourceLabel'], values=tweets_source_pie['Tweets']))

cat_plat.update_traces(hoverinfo='label+percent+value',
                              hovertemplate='<extra></extra>'+
                              '%{label}<br>'+
                              '<br>Tweets: %{value:.0f}'+
                              '<br>%Total: %{percent}',
                              textinfo='text+value', textfont_size=11,
                              marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
                                          line=dict(color='#000000', width=1))
                             )

cat_plat.update_layout(title="Total Tweets by Platform",
                       width = 700, height = 500,
                       title_font_size = 22,
                       title_x = 0.5,
                       title_xanchor = 'center',
                       font=dict(family="Comic, monospace",
                                 size=14,
                                 color="RoyalBlue")
                      )

# Pie Chart - Total Tweets
cat_tweets = go.Figure((go.Pie(labels=tweets_agg['category'], values=tweets_agg['Total_Tweets'])))

cat_tweets.update_traces(hoverinfo='label+percent+value',
                              hovertemplate='<extra></extra>'+
                              '%{label}<br>'+
                              '<br>Tweets: %{value:.0f}'+
                              '<br>%Total: %{percent}',
                              textinfo='text+value', textfont_size=11,
                              marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
                                          line=dict(color='#000000', width=1))
                             )

cat_tweets.update_layout(title="Total Tweets by Category",
                         width = 700, height = 500,
                         title_font_size = 22,
                         title_x = 0.5,
                         title_xanchor = 'center',
                         #legend_title="Category",
                         font=dict(family="Comic, monospace",
                                   size=14,
                                   color="RoyalBlue")
                        )

# Scatter plot usage percent by name
name_platform_p = px.scatter(platform_usage,
                             y = 'Device',
                             x = 'name',
                             color = 'Device',
                             custom_data = ['percent'],
                             size='percent'
                             )

name_platform_p.update_traces(hovertemplate='<extra></extra>'+
                                            '%{y}:  %{customdata[0]}',
                              textfont_size=11
                              )

name_platform_p.update_layout(yaxis_title = 'Tweets',
                              width = 1200, height = 800,
                              title="Tweets by Twitter Platform",
                              title_font_size = 22,
                              title_x = 0.5,
                              title_xanchor = 'center',
                              xaxis_title="User",
                              legend_title="Platform",
                              hovermode='x unified',
                              font=dict(family="Comic, monospace",
                                        size=14,
                                        color="RoyalBlue")
                              )


# Paste here data frames or plots

# Set Streamlit title and header
st.set_page_config(page_title='Twitter Analysis 2022',
                   page_icon='random',
                   layout='wide') # 'wide' or 'centered'

st.title('Tweeting behaviour and engagement from top users in 2022')

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Intro', 'Category Analysis', 'User Analysis', 'Time Series', 'Executive Summary'])

with tab1:
    st.text('Intro:')

with tab2:
   #st.header("A cat")
   with st.container():
       col1, col2 = st.columns(2)

       with col1:
           st.plotly_chart(cat_plat, width=200)
       with col2:
           st.plotly_chart(cat_tweets)

   with st.container():
       st.plotly_chart(name_platform_p)

with tab3:
   st.header("A dog")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

   genre = st.radio("Select the twitter user",
                    ('Bill Gates', 'Elon Musk', 'Harry Potter'))

   if genre == 'Bill Gates':
       st.write(genre)
   else:
       st.write('Elon Musk or Harry Potter')

with tab4:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
