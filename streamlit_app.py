import pandas as pd
import numpy as np
import streamlit as st
import requests 
import matplotlib.pyplot as plt

import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk import FreqDist

#add title to page
st.title('Yelp Business Data')

#reading updated business and review csv
business = pd.read_csv('bussiness_updated.csv')
reviews = pd.read_csv('df_review_bus.csv')

#displaying datframe of business data
st.dataframe(data=business, width=None, height=None)

#have user select category
with st.sidebar:
    st.subheader("User Inputs for Graph")
    category_chosen = st.sidebar.selectbox("Select a Category", reviews.categories.unique())

#subset of yelp data based on the category chosen 
category_subset = reviews[reviews['categories'] == category_chosen]

#taking all reviews from dataframe, joining them into one string, and making all the
#characters lowercase 
reviews_txt = ' '.join(category_subset['text']).lower()

#splitting into tokens
word_tokens = word_tokenize(reviews_txt)

#making list of stop words
stop_words = set(stopwords.words('english'))

#filterng out stop words and none words
words = []
for word in word_tokens:
    if word.isalpha() and word not in stop_words:
        words.append(word)

#getting frequency distrabution
frequency = FreqDist(words)

#creating dataframes
dist = pd.DataFrame(frequency.items(),columns=['word', 'freq'])

#sorting by frequency 
dist = dist.sort_values(by='freq', ascending=False).reset_index(drop=True)

#selecting only top 10
dist = dist.iloc[:10, :]

#getting data for graph 
words = dist['word']
frequency = dist['freq']

#create figure
fig = plt.figure()
#title for graph 
title = f"10 Most Frequent Words in Yelp Reviews for {category_chosen} category of Businesses"
#setting up graph and labels
plt.barh(words, frequency)
plt.ylabel('Word')
plt.xlabel('Word Frequency')
plt.title(title)
st.pyplot(fig)

st.markdown("*Only includes reviews for reviews from the top 1% of businesses based on review volume within each business category.")