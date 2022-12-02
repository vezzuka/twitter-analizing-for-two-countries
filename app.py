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
                              title="Usage of Twitter Platforms, % from user total tweets",
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

# Bar charts: Interactions
# Create subplot grid
cat_interactions = make_subplots(rows=1, cols=2, subplot_titles=("Total Interactions", "Interactions/Tweet"))

# Add traces top left
actions = ['Replies', 'Retweets', 'Likes', 'Quotes']
colors = ['#FD3216', '#6A76FC', '#FBE426', '#FF9616']  # '#F6F926']
aggregators = ['Total', 'Mean']

for c, action in enumerate(actions):
    for i, agg in enumerate(aggregators):
        y_str = f'{agg}_{action}'
        cat_interactions.add_trace(go.Bar(name=action,
                                          x=tweets_agg['category'],
                                          y=tweets_agg[y_str],
                                          marker_color=colors[c]), row=1, col=i + 1)
        cat_interactions.update_traces(  # hovertemplate='<extra></extra>'+
            # '%{x}<br>'+
            # '<br>{action}:  %{y}',
            textfont_size=11,
            # title_xaxis="Category",
            # marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
            # line=dict(color='#000000', width=1))
        )

cat_interactions.update_layout(barmode='stack',
                               width=1400,
                               height=500,
                               title="Total Twitter Interactions",
                               title_font_size=22,
                               title_x=0.5,
                               title_xanchor='center',
                               xaxis_title="Category",
                               legend_title="Interaction Type",
                               hovermode='x unified',
                               font=dict(family="Comic, monospace",
                                         size=14,
                                         color="RoyalBlue")
                               )

# Bar charts: Platform usage
cat_platform = px.bar(cns_df,
                    x = 'category',
                    y = 'Tweets',
                    color = 'Device',
                    custom_data = ['Device'],
                    barmode = 'stack')

cat_platform.update_traces(hovertemplate='<extra></extra>'+
                                       '%{customdata[0]}:  %{y}',
                                       textfont_size=11,
                                       #title_xaxis="Category",
                              #marker=dict(colors=['gold', 'mediumturquoise',  'lightgreen'],
                                          #line=dict(color='#000000', width=1))
                             )

cat_platform.update_layout(yaxis_title = 'Tweets',
                         width = 800, height = 500,
                         title="Tweets by Platform",
                         title_font_size = 22,
                         title_x = 0.5,
                         title_xanchor = 'center',
                         xaxis_title="Category",
                         legend_title="Device",
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


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Intro', 'Tweets by Category and Platform', 'Engagement by Category', 'User Analysis', 'Time Series', 'Executive Summary'])

with tab1:
    with st.container():
        st.header('Scope')
        st.text('We analysed the tweeting behaviour and the engagement created from 19 top users, selected from 3 different categories shown below\n'
                '\n'                
                'We wanted to get some insights on which users and categories are more active and get more engagement, which keywords they use and \n'
                'how did these patterns changed throughout the year.\n\n')
    with st.container():
        st.header('Users by Categories')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader('Tech CEOs')
            st.text('Elon Musk (Technoking)\n'
                    'Mark Zuckerberg (CEO Meta)\n'
                    'Tim Cook (CEO Apple)\n'
                    'Sundar Pichai (CEO Alphabet)\n'
                    'Satya Nadella (CEO Microsoft)\n'
                    'Jeff Bezos (former CEO Amazon)\n'
                    'Bill Gates (former CEO Microsoft)\n'
                    )
        with col2:
            st.subheader('Politicians')
            st.text('Joe Biden (President of US)\n'
                    'Narenda Modi(PM of India)\n'
                    'Barack Obama (former President of US)\n'
                    'Volodymyr Zelenskyy (President of Ukraine)\n'
                    'Ron DeSantis (Governor of Florida)\n'
                    'Alexandria Ocasio-Cortez (NY Representative)\n'
                    )
        with col3:
            st.subheader('Celebrities')
            st.text('Justin Bieber (Musician)\n'
                    'Katy Perry (Musician)\n'
                    'Rihanna (Musician)\n'
                    'Lady Gaga(Musician and actress)\n'
                    'Ellen DeGeneres (Comedian and TV Host)\n'
                    'Kim Kardashian (Socialite)\n'
                    )
        with st.container():
            st.header('Analysis')
            st.text('We calculated the following metrics for a total of 15.4k Tweets between January 1st and November 30th 2022:\n\n'
                    '- Total Tweets by Category and Platform\n'
                    '- Interactions (Likes, Retweets, Replies and Quotes) by Category\n'
                    '- User Analysis: Wordclouds, Behaviour and Platform usage\n'
                    '- Time Series for Interactions metrics, including Likes to Replies and Likes Ratio'
                    )

with tab2:
   #st.header("A cat")
   with st.container():
       col1, col2 = st.columns(2)

       with col1:
           st.plotly_chart(cat_plat)
       with col2:
           st.plotly_chart(cat_tweets)
   with st.container():
       st.plotly_chart(cat_platform)

with tab3:
    with st.container():
        st.plotly_chart(cat_interactions)

with tab4:
   st.header("A dog")
   with st.container():
       st.plotly_chart(name_platform_p)

with tab5:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
