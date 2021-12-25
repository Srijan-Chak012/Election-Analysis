#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup as bs
import re
import numpy as np
import pandas as pd


# In[ ]:


def soup_url(url):
    html = requests.get(url)
    soup = bs(html.content,'html5lib')
    return soup


# In[ ]:


def create_dist_dict(url):
    soup = soup_url(url)
    district = soup.findAll('h5')
    print(district)
    didict = {}
    for item in district:
        a = str(item)
        district_link = a[a.find('href="')+6:a.find('" style')]
        district_link = district_link.replace('&amp;' , '&')
        district_name = a[a.find(' ">')+3:a.find(' </a>')]
        didict[district_name] = url + district_link
    return didict


# In[ ]:


url = "https://myneta.info/bihar2020/"
DistrictDict = create_dist_dict(url)
print(DistrictDict)


# In[ ]:


def create_AC_dict(DistrictDict):
    for district in DistrictDict:
        url = DistrictDict[district]
        soup = soup_url(url)
        table = soup.find_all("table")[-1]
        ac_href = table.find_all('a', href = True)
        raw_ac = []
        raw_ac = str(ac_href)
        raw_ac = raw_ac.split(', <') 
        new_ac = []
        for ac in raw_ac: 
            ac = "<" + ac 
            new_ac.append(ac)
        correct_ac = []
        for a in new_ac:
            if '><' not in a:
                correct_ac.append(a)
        acdict = {}
        for a in correct_ac:
            ac_link = a[a.find('href="')+6:a.find('">')]
            ac_link = ac_link.replace('&amp;' , '&')
            ac_name = a[a.find('">')+2:a.find('</a>')]
            if ac_link[:4] == "http":
                acdict[ac_name] = ac_link
            else:
                acdict[ac_name] = url[:url.find('index.php?')] + ac_link
        DistrictDict[district] = acdict
        print(DistrictDict)
    return DistrictDict


# In[ ]:


masterdict = create_AC_dict(DistrictDict)


# In[ ]:


def create_candidate_dict(masterdict):
    for district in masterdict:
        for ac in masterdict[district]:
            tableData = []
            url = masterdict[district][ac]
            soup = soup_url(url)
            # if soup.title.string.lower().find('delete') == -1:
            if soup.find("table",{"id":"table1"}) != None:
                table = soup.find("table",{"id":"table1"})
                allRows = table.findAll('tr')
                for row in allRows:   
                    eachRow = []
                    cells = row.findAll('td')
                    for cell in cells:
                        eachRow.append(cell.text.encode('utf-8').strip())
                    tableData.append(eachRow)
                tableData = [x for x in tableData if x != []]
                CandidateCol = [x[0] for x in tableData]
                PartyCol = [x[1] for x in tableData]
                CrimesCol = [x[2] for x in tableData]
                EducationCol = [x[3] for x in tableData]
                AgeCol = [x[4] for x in tableData]
                AssetsCol = [x[5] for x in tableData]
                LiabilityCol = [x[6] for x in tableData]
                canddict = {}
                canddict = {
                            "Candidate Name" : CandidateCol,
                            "Party" : PartyCol,
                            "Criminal Cases" : CrimesCol,
                            "Education" : EducationCol,
                            "Age" : AgeCol,
                            "Assets" : AssetsCol,
                            "Liabilities" : LiabilityCol}
                masterdict[district][ac] = canddict
                return masterdict
                break
    return masterdict


# In[ ]:


masterdict = create_candidate_dict(masterdict)


# In[ ]:


masterDF = pd.DataFrame()
for district in masterdict:
    for ac in masterdict[district]:
        if type(masterdict[district][ac]) is dict:    #find lowest dictionary
                candidateDF = pd.DataFrame(masterdict[district][ac])   #create temporary DF with lowest level dictionary
                candidateDF['ac'] = str(ac)   #add AC, district, year, and state to each row within the DF
                candidateDF['District'] = str(district)
                masterDF = masterDF.append(candidateDF)   #append temporary DF to final DF

#initial data cleaning 
#create a copy for cleaning, so the original data is still available unchanged
themasterDF = masterDF.copy()


#creating an Education Rank column as education is ordinal instead of categorical
themasterDF["EduRank"] = 0
edurank = {
            "others" : 0,
            "not given": 0,
            "illiterate": 1,
            "literate": 2,
            "5th pass": 3,
            "8th pass": 4,
            "10th pass": 5,
            "12th pass": 6,
            "graduate": 7,
            "graduate professional": 8,
            "post graduate": 9,
            "doctorate": 10
            }

for a_val, b_val in edurank.iteritems():
    themasterDF["EduRank"][themasterDF.education==a_val] = b_val

#renaming columns
themasterDF.rename(columns={'candidate name':'cand_name', 'criminal cases':'criminal_cases'}, inplace=True)

#creating a winner column & binary win column
themasterDF["WinnerTF"] = themasterDF.cand_name.str.contains('winner')
themasterDF["Winner"] = np.where(themasterDF["WinnerTF"]==True,1,0)

#creating a clean assets column
themasterDF["Asset"] = themasterDF["assets"].map(lambda x:x.lstrip('rsÂ ').split(" ~")[0].replace(",", ""))

#creating a clean liabilities column
themasterDF["Liability"] = themasterDF["liabilities"].map(lambda x:x.lstrip('rsÂ ').split(" ~")[0].replace(",", ""))


if themasterDF.cand_name.str.contains('winner'):
    themasterDF["Winner"] = 1
else:
    themasterDF["Winner"] = 0
        
themasterDF.to_csv("masterdictdump.csv")

