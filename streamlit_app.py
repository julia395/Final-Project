
##### This app is just an extremely simple example.
##### See the Streamlit documentation for how to create more complex apps.

import pandas as pd
import numpy as np

business = pd.read_csv('business.csv')

#removing businesses that are permenatley closed 
business = business[business['is_open'] == 1]

#splitting the string of categories for each row into a list 
categories = business['categories'].str.split(", ")

#replacing the categories column with a list for each row 
business['categories'] = categories

#remove missing values in the categories column 
categories = categories.dropna()

#creating a list of all the categories by iterating through the nested list 
#of categories and flattening the list 
flatlist = []
for sublist in categories:
    for element in sublist:
        flatlist.append(element)

#removing duplicates from the flattened list of categories 
category_list = []
for category in flatlist:
    if category not in category_list:
       category_list.append(category)

#changing flattened list of all categories into pandas series and counting occurance 
#of each category then creating a dictionary
categories_series = pd.Series(flatlist)
occurances = categories_series.value_counts()
occurances_dict = occurances.to_dict()

# keeping only one category for each business based on which category has the 
# most businesses

#add column of number of occurances
business_exploded = business.explode('categories')
occur = business_exploded['categories'].map(occurances_dict)
business_exploded['occurance_of_category'] = occur

#sort rows by business id then occurance of category so the same business is kept 
#together and the most popular category for the business will be listed first
business = business_exploded.sort_values(by=['business_id','occurance_of_category'], ascending=False)

#keeping only one row for each business that has the most popular category
business = business.drop_duplicates(subset='business_id', keep='first')

# keeping only businesses that in top 1 percentile of businesses with most of reviews within each category 
rank = business.groupby('categories')['review_count'].rank(pct=True)
business['percent_rank'] = rank
top_reviewed_bus = business[business['percent_rank'] >= 0.99]

import requests 

bus_id_list = top_reviewed_bus['business_id'].tolist()

review_df = pd.DataFrame()
api_key = 'ghT50Lq_KgKyg-kKuwT5Hvv-gAAGprAWRdHyo50TPgeHlrWSG54jvmo9CGGRjlKwfm2uq5x4e8i7i_JOd49-DulkbwDZRTsve8chhPe59MtuiEM9qfXpHhwpq5RpYnYx'
headers = {'Authorization': "Bearer {}".format(api_key)}
for bus_id in bus_id_list:
   req = requests.get('https://api.yelp.com/v3/businesses/{}/reviews'.format(bus_id), headers = headers)
   data = req.json()
   if 'error' not in data:
    df_response = pd.DataFrame(data['reviews'])
    df_response['business_id'] = bus_id
    review_df = review_df.append(df_response)

df_review_bus = pd.merge(top_reviewed_bus, review_df , on='business_id')
df_review_bus = df_review_bus.drop(columns=['address','is_open'])

#should i save as file here so data is static?
df_review_bus.to_csv('df_review_bus.csv')

## RUN FROM HERE 
import streamlit as st
import pandas as pd

#load csv file i just created
df_yelp_data = pd.read_csv('df_review_bus.csv')

#change time_created to date
df_yelp_data['time_created']= pd.to_datetime(df_yelp_data['time_created'])

#go back and change for streamlit
#category_chosen = st.sidebar.selectbox("Select a Category", df_yelp_data.categories.unique())
category_chosen = 'Restaurants'
category_filter = df_yelp_data[df_yelp_data['categories'] == category_chosen]

subset = df_yelp_data[df_yelp_data['categories'] == category_chosen]
aft_mar_2022 = subset[subset['time_created'] >= 'March 01, 2022 00:00']
bef_mar_2022 = subset[subset['time_created'] < 'March 01, 2022 00:00']

txt_aft_2022 = ' '.join(aft_mar_2022['text']).lower()
txt_bef_2022 = ' '.join(bef_mar_2022['text']).lower()

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

word_tokens_before = word_tokenize(txt_bef_2022)
word_tokens_after = word_tokenize(txt_aft_2022)
stop_words = set(stopwords.words('english'))

before_words = []
for word in word_tokens_before:
    if word.isalpha() and word not in stop_words:
        before_words.append(word)

amount_of_words_b = len(before_words)

after_words = []
for word in word_tokens_after:
    if word.isalpha() and word not in stop_words:
        after_words.append(word)

amount_of_words_a = len(after_words)

before_frequency = FreqDist(before_words)
after_frequency = FreqDist(after_words)

before_dist = pd.DataFrame(before_frequency.most_common(20),columns=['Word', 'Frequency'])
after_dist = pd.DataFrame(after_frequency.most_common(20),columns=['Word', 'Frequency'])

b_percentage = []
b_frequency = before_dist["Frequency"].tolist()

for freq in b_frequency:
    percent = freq/amount_of_words_b
    formated = "{:.2%}".format(percent)
    b_percentage.append(formated)

before_dist['Percent Frequency'] = b_percentage

a_percentage = []
a_frequency = after_dist["Frequency"].tolist()

for freq in a_frequency:
    percent = freq/amount_of_words_a
    formated = "{:.2%}".format(percent)
    a_percentage.append(formated)

after_dist['Percent Frequency'] = a_percentage

st.write(after_dist)
st.write(before_dist)

##### Title and intro

#st.title( 'Example Streamlit App' )
#st.write( '''
#This app is very small and does almost nothing.
#It's just an example.
#''' )


##### Inputs

#st.header( 'Choose two numbers' )
#a = st.slider( label='a', min_value=1, max_value=10, value=2, step=1 )
#b = st.slider( label='b', min_value=1, max_value=10, value=3, step=1 )


##### Output

#st.header( 'Tiny computations')
#st.write( f'{a} + {b} = {a+b}' )
#st.write( f'{a} - {b} = {a-b}' )
#st.write( f'{a} * {b} = {a*b}' )
#st.write( f'{a} / {b} = {a/b}' )
