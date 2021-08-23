
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from adjustText import adjust_text
import matplotlib.patches as patches
import requests
import bs4
from bs4 import BeautifulSoup
import re

url = 'https://fbref.com/en/comps/40/stats/Scottish-Premiership-Stats#stats_standard'

res = requests.get(url)
## The next two lines get around the issue with comments breaking the parsing.
comm = re.compile("<!--|-->")
soup = BeautifulSoup(comm.sub("",res.text),'lxml')
all_tables = soup.findAll("tbody")


pre_df = dict()
teamname = []
features_wanted = {}
table = all_tables[2]
rows_tb = table.find_all('tr')
rs = rows_tb[0].find_all('td')
for i in range(len(rs)):
    if(rs[i]['data-stat'] !=None):
        features_wanted[rs[i]['data-stat']] = []
for row in rows_tb:
    if(row.find('th',{"scope":"row"}) != None):
        if(row.find('th',{'data-stat':'sqaud'})!=None):
            teamname.append(row.find('th',{'data-stat':'squad'}).text.strip())
        for f in features_wanted:
            cell = row.find("td",{"data-stat": f})
            if(cell !=None):
                a = cell.text.strip().encode()
                text=a.decode("utf-8")
                if f in pre_df:
                    pre_df[f].append(text)
                else:
                    pre_df[f] = [text]

dfplayer = pd.DataFrame.from_dict(pre_df)

bgcolor='white'
color1='blue'
scolor='grey'
textcolor='black'
font='Aerial'


# Data import & columns
af=dfplayer
#af = af.droplevel(0, axis=1)
#af = af[af.Player != 'Player']
#af = af[af['Age'].notna()]
af["minutes"] = pd.to_numeric(af["minutes"])

#Format Age
af['age']=af['age'].astype(str)

age_years =[]
for age in af['age']:
    age_years.append(age.split("-",1)[0])
    
age_days =[]
for age in af['age']:
    age_days.append(age.split("-",1)[-1])    
    
af['Age Years'] = pd.to_numeric(age_years)
af['Age Days'] = pd.to_numeric(age_days)
af['Age Days'] = af['Age Days']/365
af['age']=af['Age Years']+af['Age Days']

#Format Name
player_name =[]
for name in af['player']:
    player_name.append(name.split()[-1])

af['player'] = player_name

teams = list(af['squad'].drop_duplicates())
teams=sorted(teams)
team_choice = st.sidebar.selectbox(
    "Select a team:", teams, index=3)
af=af.loc[(af['squad'] == team_choice)]

fig, ax = plt.subplots(figsize=(12,9),dpi=80)

var1='age'
var2='minutes'

x1 = af[var1]
y1 = af[var2]

plt.scatter(x1, y1, color=scolor,edgecolor='black', s=100,zorder=4)

#players=['P. Hannola']
players=af['player']


# set the background color for the axes
ax.set_facecolor(bgcolor)

# iterate the dataframe
#for _, row_val in af.iterrows():
    
 #   if row_val["Player"] in players:
  #      # specify the values
   #     alpha, s, ec = 1, 100, color1

    #else:
     #   # specify the values
      #  alpha, s, ec = 0.15, 100, color1
        
 #   plt.scatter(
  #      row_val[var1], row_val[var2],
   #     s, hatch=5*"/", edgecolor=bgcolor, fc=color1, alpha=alpha, zorder=4
    #)

# player names with their coordinate locations   

text_values = af.loc[
    af["player"].isin(players),
    [var1, var2, "player"]
].values

# make an array of text
texts = [
    ax.text(
        val[0], val[1]+5, val[2], 
        size=10, color=textcolor, zorder=5,#rotation=45,
        fontfamily=font
    ) for val in text_values
]

# use adjust_text
adjust_text(
    texts, autoalign='x', 
    only_move={'points':'y', 'text':'xy'}, 
    force_objects=(0, 0), force_text=(0, 0), 
    force_points=(0, 0)
)

median = af['age'].median()
max_mins =af['minutes'].max()

#ax.plot([median,median],[0,max_mins],lw=median*2,color=scolor,zorder=3,alpha=0.5)

top_p= max_mins*0.65
bottom_p= max_mins*0.25
middle_p =max_mins*0.5

min_age =af['age'].min()
max_age =af['age'].max()

rect=patches.Rectangle ((17,top_p),9,max_mins-top_p,color='green',alpha=0.5,hatch="\\")
ax.add_patch(rect)

rect=patches.Rectangle ((28,0),max_age-28,top_p,color='red',alpha=0.5,hatch="\\")
ax.add_patch(rect)

#ax.plot([min_age,max_age],[top_p,top_p],lw=2,color=scolor,zorder=3,alpha=0.5)
#ax.plot([min_age,max_age],[bottom_p,bottom_p],lw=2,color=scolor,zorder=3,alpha=0.5)

#plt.text(x=max_age*0.95, y=top_p*1.15, s="Core\nPlayers", fontsize=16)
#plt.text(x=min_age*0.95, y=bottom_p*0.5, s="Peripheral\nPlayers", fontsize=16)
    
# add x-label and y-label
ax.set_xlabel(
    "Age", color=textcolor,
    fontsize=18, fontfamily=font
)
ax.set_ylabel(
    "Minutes played",color=textcolor,
    fontsize=18, fontfamily=font
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

st.pyplot(fig)
