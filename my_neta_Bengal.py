#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup as bs
import re
import numpy as np
import pandas as pd


# In[2]:


def soup_url(url):
    html = requests.get(url)
    soup = bs(html.content,'html5lib')
    return soup


# In[3]:


def create_dist_dict(url):
    soup = soup_url(url)
    district = soup.findAll('h5')
    didict = {}
    for item in district:
        a = str(item)
        district_link = a[a.find('href="')+6:a.find('" style')]
        district_link = district_link.replace('&amp;' , '&')
        district_name = a[a.find(' ">')+3:a.find(' </a>')]
        didict[district_name] = url + district_link
    return didict


# In[4]:


url = "https://myneta.info/uttarpradesh2017/"
DistrictDict = create_dist_dict(url)
print(DistrictDict)


# In[5]:


def create_AC_dict(DistrictDict):
    masterdict = {}
    for district in DistrictDict:
        url = DistrictDict[district]
        soup = soup_url(url)
        table = soup.find_all("table")[-1]
        allRows = table.findAll('tr')
        tableData = []
        for row in allRows:   
            eachRow = []
            cells = row.findAll('td')
            for cell in cells:
                eachRow.append(cell.text.encode('utf-8').strip())
            tableData.append(eachRow)
        tableData = [x for x in tableData if x != []]
        CandidateCol = [x[1].decode('utf-8') for x in tableData]
        PartyCol = [x[2].decode('utf-8') for x in tableData]
        CrimesCol = [x[3].decode('utf-8') for x in tableData]
        EducationCol = [x[4].decode('utf-8') for x in tableData]
        AgeCol = [x[5].decode('utf-8') for x in tableData]
        AssetsCol = [x[6].decode('utf-8') for x in tableData]
        LiabilityCol = [x[7].decode('utf-8') for x in tableData]
        canddict = {}
        canddict = {
                    "Candidate Name" : CandidateCol,
                    "Party" : PartyCol,
                    "Criminal Cases" : CrimesCol,
                    "Education" : EducationCol,
                    "Age" : AgeCol,
                    "Assets" : AssetsCol,
                    "Liabilities" : LiabilityCol}
        masterdict[district] = canddict
    return masterdict


# In[14]:


from pprint import pprint
masterdict = create_AC_dict(DistrictDict)
pprint(masterdict)


# In[15]:


masterDF = pd.DataFrame()
for district in masterdict:
#         if type(masterdict[district]) is dict:    #find lowest dictionary
        candidateDF = pd.DataFrame(masterdict[district]) #create temporary DF with lowest level dictionary)
#         print(candidateDF.head())
        candidateDF['District'] = str(district)
        candidateDF['Election'] = 'uttarpradesh2017'
        masterDF = masterDF.append(candidateDF)   #append temporary DF to final DF

print(masterDF.columns.tolist())
#initial data cleaning 
#create a copy for cleaning, so the original data is still available unchanged


# In[16]:


themasterDF = masterDF.copy()

#### Text preprocessing here
themasterDF["EduRank"] = 0
edurank = {
            "Others" : 0,
            "Not given": 0,
            "Illiterate": 1,
            "Literate": 2,
            "5th pass": 3,
            "8th pass": 4,
            "10th pass": 5,
            "12th pass": 6,
            "Graduate": 7,
            "Graduate professional": 8,
            "Post graduate": 9,
            "Doctorate": 10
            }

for a_val, b_val in edurank.items():
    themasterDF["EduRank"][themasterDF.Education==a_val] = b_val

themasterDF.to_csv("/home/srijan/Laptop-data/HS Lab/Elections/rahul2.csv")


# In[26]:


df = pd.read_csv("/home/srijan/Laptop-data/HS Lab/Elections/rahul2.csv")
df = df.drop(['Unnamed: 0'],axis = 1)
# print(df.columns.tolist())
df
# df.shape


# In[27]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
df = df.groupby('Party')


# In[28]:


df.plot(x='Party',y='Criminal Cases',kind = 'bar')


# In[29]:


# df = df.groupby('Party')
df.plot(x='Party',y='EduRank',kind = 'bar')


# In[33]:


# df = df.groupby('Party')
df.plot(x='Party',y='Age',kind = 'bar')


# In[ ]:




