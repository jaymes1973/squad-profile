
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from adjustText import adjust_text
import matplotlib.patches as patches
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(
     page_title="Squad Profile",
     layout="wide",
     )

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

dfteam= pd.read_html(url)[0]
dfteam = dfteam.droplevel(0, axis=1)

bgcolor='white'
color1='blue'
scolor='grey'
textcolor='black'
font='Aerial'


# Data import & columns
af=dfplayer
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

def age_mins_25(af):
    if af['age']<=25:
        val=af.age*af.minutes
    else:
        val=0
    return val
        
af["Mins aged Under 25"]=pd.to_numeric(af.apply(age_mins_25,axis=1))

def age_mins_25_29(af):
    if af['age']>25 and af['age']<29:
        val=af.age*af.minutes
    else:
        val=0
    return val
        
af["Mins aged 25 to 29"]=pd.to_numeric(af.apply(age_mins_25_29,axis=1))

def age_mins_29(af):
    if af['age']>=29:
        val=af.age*af.minutes
    else:
        val=0
    return val
        
af["Mins aged Over 29"]=pd.to_numeric(af.apply(age_mins_29,axis=1))

#Format Name
player_name =[]
for name in af['player']:
    player_name.append(name.split()[-1])

af['player'] = player_name

dftable=pd.DataFrame()
dftable['team']=dfteam['Squad']
dftable['Players used']=dfteam['# Pl']
dftable['Avg Squad Age']=dfteam['Age']
dftable['Mins X Under 25']=np.nan#
dftable['Mins X 25 to 29']=np.nan#
dftable['Mins X Over 29']=np.nan#
#dftable['Team mins']=np.nan#

clubs = list(dftable['team'].drop_duplicates())

#for clubs in dftable.team:
 #   hold_af=dfteam.loc[(dfteam['Squad'] == clubs)]
  #  dftable.at[dftable['team']==clubs, 'Team mins'] = hold_af["Min"]*11

for clubs in dftable.team:
    hold_af=af.loc[(af['squad'] == clubs)]
    dftable.at[dftable['team']==clubs, 'Mins X Under 25'] = hold_af["Mins aged Under 25"].sum()
    
for clubs in dftable.team:
    hold_af=af.loc[(af['squad'] == clubs)]
    dftable.at[dftable['team']==clubs, 'Mins X 25 to 29'] = hold_af["Mins aged 25 to 29"].sum()

for clubs in dftable.team:
    hold_af=af.loc[(af['squad'] == clubs)]
    dftable.at[dftable['team']==clubs, 'Mins X Over 29'] = hold_af["Mins aged Over 29"].sum()



teams = list(af['squad'].drop_duplicates())
teams=sorted(teams)
team_choice = st.sidebar.selectbox(
    "Select a team:", teams, index=3)
af=af.loc[(af['squad'] == team_choice)]
dfteam1=dfteam.loc[(dfteam['Squad']== team_choice)]


st.title('Squad Profile')

fig, ax = plt.subplots(figsize=(12,9),dpi=80)

var1='age'
var2='minutes'

x1 = af[var1]
y1 = af[var2]

median = af['age'].median()
max_mins =dfteam1['Min'].max()

top_p= max_mins*0.6
bottom_p= max_mins*0.4
middle_p =max_mins*0.5

min_age =af['age'].min()
max_age =af['age'].max()

plt.scatter(x1, y1, color=scolor,edgecolor='black', s=100,zorder=4)

players=af['player']

# set the background color for the axes
ax.set_facecolor(bgcolor)

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

rect=patches.Rectangle ((16,top_p),9,max_mins-top_p,color='green',alpha=0.5,hatch="\\")
ax.add_patch(rect)

rect=patches.Rectangle ((28,0),12,bottom_p,color='red',alpha=0.5,hatch="\\")
ax.add_patch(rect)

    
# add x-label and y-label
ax.set_xlabel(
    var1, color=textcolor,
    fontsize=18, fontfamily=font
)
ax.set_ylabel(
    "Minutes played",color=textcolor,
    fontsize=18, fontfamily=font
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(16, 40)
ax.set_ylim(0, max_mins+5)

st.pyplot(fig)

dftable.columns=["Team","No. of\nPlayers Used","Avg\nSquad age","Age x Mins\nUnder 25","Age x Mins\n25 to 29","Age x Mins\nOver 29"]

st.dataframe(dftable.style.format({"Avg\nSquad age":"{:.2f}","Age x Mins\nUnder 25":"{:.2f}","Age x Mins\n25 to 29":"{:.2f}",
                                   "Age x Mins\nOver 29":"{:.2f}"}))
