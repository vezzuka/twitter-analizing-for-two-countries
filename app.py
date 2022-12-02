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

import datetime as dt
import plotly.io as pio

import seaborn as sns
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
import re
import pylab


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

# Set Streamlit title and header
st.set_page_config(page_title='Twitter Analysis 2022',
                   page_icon='random',
                   layout='wide') # 'wide' or 'centered'

st.title('Tweeting behaviour and engagement from top users in 2022')


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Intro', 'Tweets by Category and Platform', 'Engagement by Category and Platform Usage', 'Wordclouds', 'Time Series', 'Executive Summary'])

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
    with st.container():
        st.plotly_chart(name_platform_p)

with tab4:
    # Markus code
    celebs = list(df1["name"].unique())
    celeb = st.selectbox("Select the twitter user", celebs)
                   # ('Bill Gates', 'Elon Musk', 'Harry Potter'))
    stop_words = set(stopwords.words('english'))
    stop_words = (list(stop_words)) + [" ", "based", "regarding", "good", "right", "even", "", "thank", "Thank", "https"]


    wordcloud_dic = {}

    # Setting stop words

    for i in range(len(celebs)):
       # selecting the celbrity

       df = df1[df1['name'] == celebs[i]]
       # saving the Tweet-content in a string variable
       x = str(df["content"])
       token = word_tokenize(x)

       # using regex to only select alphanumeric
       l = []
       for j in range(len(token)):
           l.append(re.sub(r'\W+', '', token[j]))

       # getting rid of stop words
       filtered = []
       for w in l:
           if w.lower() not in stop_words:
               filtered.append(w)

       # creating dic to count number of words
       word_dic = {}
       for m in filtered:
           if m in word_dic:
               word_dic[m] += 1
           else:
               word_dic[m] = 1

       s = {k: v for k, v in sorted(word_dic.items(), key=lambda item: item[1], reverse=True)}

       # Wordcloud
       comment_words = ''
       stop_words2 = list(STOPWORDS)

       # putting list back into a string
       token_2 = (" ".join(s))

       wordcloud = WordCloud(width=600, height=600,
                             background_color='white',
                             stopwords=stop_words2,
                             max_words=100,
                             min_word_length=3,
                             min_font_size=10).generate(token_2)

       wordcloud_dic[celebs[i]] = wordcloud

    if celeb:
       fig2 = plt.figure(figsize=(8, 8), facecolor=None)
       plt.imshow(wordcloud_dic[celeb])
       plt.axis("off")
       plt.tight_layout(pad=0)
       plt.title(celeb + ' Tweetcloud')
       st.pyplot(fig2)



    df_test = df1[["name", "likeCount", ]]
    s = df_test.groupby('name').likeCount.sum()
    so = s.sort_values(ascending=False)
    s_pol = df1.query(
       'name == "Joe Biden" or  name == "Barack Obama" or name == "Ron DeSantis" or name == "Alexandra Ocaso-Cortez" or name == "Narendra Modi"')

    df_group = df_test.groupby('name').agg({"likeCount": ["nunique", "sum"]})
    df_group.columns = df_group.columns.droplevel(0)
    df_group.columns = ["number_tweets", "likecount_sum"]

    fig,bar_celeb = plt.subplots()
    bar_celeb = so.plot.bar()
    plt.yscale('log')#, base=2)

    plt.style.use('seaborn-whitegrid')
    scatter_celeb, ax = plt.subplots()
    sns.scatterplot(x="retweetCount",
                    y="likeCount",
                    hue="name",
                    data=s_pol)
    ax.set_ylim(0, 200000)
    ax.set_xlim(0, 20000)

    with st.container():
       col1, col2 = st.columns(2)

       with col1:
           st.text('Work in Progress')
           st.pyplot(bar_celeb.figure)

       with col2:
           st.text('Work in Progress')
           st.pyplot(scatter_celeb)

with tab5:
   
   #selecting the celebrity
   celebs_tab3 = list(df1["name"].unique())+['-']
   celeb_tab3 = st.selectbox("Select the twitter user", celebs_tab3)
   st.write(celeb_tab3)

   tab1, tab2, tab3, tab4, tab5 = st.tabs(['Stats for every tweet', 'Stats per day', 'Stats per week', 'Stats per month', 'Stats by the days of the week'])

   
   #creating the plots for a chosen celebrity
   
   df_1=df1.loc[df1['name']==celeb_tab3]
   df_1=df_1[['date','replyCount', 'retweetCount', 'likeCount','quoteCount']]
   df_1['ratio_like_to_reply']=df_1['likeCount']/df_1['replyCount']
   df_1['ratio_like_to_retweet']=df_1['likeCount']/df_1['retweetCount']
   df_1['date'] = pd.to_datetime(df_1['date'])
      
   #fig_tab3=go.Figure()
   fig_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                       [{"secondary_y": True},{"secondary_y": True}],
                                       [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes during the year", "Number of replies during the year",                                    "Number of quotes during the year", "Number of retweets during the year",
                                 "likes/retweets during the year",
                                  "likes/replies during the year"))
  
   
   # Top left
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["likeCount"]),
       row=1, col=1, secondary_y=False)

   # Top right
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["replyCount"]),
       row=1, col=2, secondary_y=False)
   # Middle left 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["quoteCount"]),
       row=2, col=1, secondary_y=False)
   # Middle right 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["retweetCount"]),
       row=2, col=2, secondary_y=False)
   # Bottom left 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["ratio_like_to_retweet"]),
       row=3, col=1, secondary_y=False)
   # Bottom right 
   fig_tab3.add_trace(
       go.Scatter(x=df_1['date'],  y=df_1["ratio_like_to_reply"]),
       row=3, col=2, secondary_y=False)

   fig_tab3.update_layout(showlegend=False)


   #tweets every day
   df_1['date'] = pd.to_datetime(df_1['date'])
   days=df_1.groupby(pd.Grouper(key='date',freq='D')).sum()
   days['ratio_like_to_reply']=days['likeCount']/days['replyCount']
   days['ratio_like_to_retweet']=days['likeCount']/days['retweetCount']

   fig2_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                    subplot_titles=("Number of likes per day during the year", "Number of replies per day during the year", 
                                   "Number of quotes per day during the year", "Number of retweets per day during the year",
                                  "likes/retweets for each day during the year",
                                   "likes/replies for each day during the year"))

    
    # Top left
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Middle left 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Middle right 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["retweetCount"]),
        row=2, col=2, secondary_y=False)

    # Bottom left 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)

    # Bottom right 
   fig2_tab3.add_trace(
        go.Scatter(x=days.index,  y=days["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig2_tab3.update_layout(showlegend=False)


   #tweets every week
   weeks=df_1.groupby(pd.Grouper(key='date', freq='W-MON')).sum()
   weeks['ratio_like_to_reply']=weeks['likeCount']/weeks['replyCount']
   weeks['ratio_like_to_retweet']=weeks['likeCount']/weeks['retweetCount']

   fig3_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes per week during the year", "Number of replies per week during the year", 
                                   "Number of quotes per week during the year", "Number of retweets per week during the year",
                                  "likes/retweets for each week during the year",
                                   "likes/replies for each week during the year"))


    # Top left
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Middle left 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Middle right 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["retweetCount"]),
        row=2, col=2, secondary_y=False)

    # Bottom left 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)
    # Bottom right 
   fig3_tab3.add_trace(
        go.Scatter(x=weeks.index,  y=weeks["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig3_tab3.update_layout(showlegend=False)
   


   #tweets every month
   months=df_1.groupby(pd.Grouper(key='date',freq='M')).sum()
   months['ratio_like_to_reply']=months['likeCount']/months['replyCount']
   months['ratio_like_to_retweet']=months['likeCount']/months['retweetCount']

   fig4_tab3 = make_subplots(rows=3, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}],
                                        [{"secondary_y": True}, {"secondary_y": True}]],
                   subplot_titles=("Number of likes per month during the year", "Number of replies per month during the year", 
                                   "Number of quotes per month during the year", "Number of retweets per month during the year",
                                  "likes/retweets for each month during the year",
                                   "likes/replies for each month during the year"))


    # Top left
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["likeCount"]),
        row=1, col=1, secondary_y=False)


   # Top right
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["replyCount"]),
        row=1, col=2, secondary_y=False)

   # Middle left 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["quoteCount"]),
        row=2, col=1, secondary_y=False)

   # Middle right 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["retweetCount"]),
        row=2, col=2, secondary_y=False)

   # Bottom left 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["ratio_like_to_retweet"]),
        row=3, col=1, secondary_y=False)
   # Bottom right 
   fig4_tab3.add_trace(
        go.Scatter(x=months.index,  y=months["ratio_like_to_reply"]),
        row=3, col=2, secondary_y=False)

   fig4_tab3.update_layout(showlegend=False)
   
   #tweets by the week day
   df_1['day_of_week'] = df_1['date'].dt.day_name()
   day_of_week=df_1.drop('date', axis=1).groupby(df_1['day_of_week']).sum()
   sorter = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
   sorterIndex = dict(zip(sorter,range(len(sorter))))
   day_of_week['Day_id'] = day_of_week.index
   day_of_week['Day_id'] = day_of_week['Day_id'].map(sorterIndex)
   day_of_week.sort_values('Day_id', inplace=True)

   fig5_tab3 = make_subplots(rows=2, cols=2,specs=[[{"secondary_y": True}, {"secondary_y": True}],
                                        [{"secondary_y": True},{"secondary_y": True}]],
                   subplot_titles=("Number of likes for day of the week", "Number of replies for day of the week", 
                                   "Number of quotes for day of the week", "Number of retweets for day of the week"))

    # Top left
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["likeCount"]),
        row=1, col=1, secondary_y=False)


    # Top right
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["replyCount"]),
        row=1, col=2, secondary_y=False)

    # Bottom left 
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["quoteCount"]),
        row=2, col=1, secondary_y=False)

    # Bottom right 
   fig5_tab3.add_trace(
        go.Scatter(x=day_of_week.index,  y=day_of_week["retweetCount"]),
        row=2, col=2, secondary_y=False)



   fig5_tab3.update_layout(showlegend=False)
   
   with tab1:
       st.plotly_chart(fig_tab3)
   with tab2:
       st.plotly_chart(fig2_tab3)
   with tab3:
       st.plotly_chart(fig3_tab3)
   with tab4:
       st.plotly_chart(fig4_tab3)
   with tab5:
       st.plotly_chart(fig5_tab3)

with tab6:
    st.text('Work in Progress')
    st.write('[Tweet with more likes](https://twitter.com/elonmusk/status/1519480761749016577?lang=en)')
    st.write('[Github Repo](https://github.com/vezzuka/twitter-analyzing-for-two-countries)')
