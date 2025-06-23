# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 16:11:52 2025

@author: jayap
"""

# Simplified QB_Dashboard.py
import pandas as pd
import streamlit as st
from urllib.parse import quote

# Load and merge data
df1 = pd.read_excel('CFB Player Combined Table.xlsx', sheet_name=0)
df2 = pd.read_excel('CFB Player Combined Table.xlsx', sheet_name=1)
data = pd.merge(df1, df2, how='right')
data = data.dropna(subset=["PLAYER_ID", "NAME"])
data["PLAYER_ID"] = data["PLAYER_ID"].astype(str).str.strip()

# Height conversion
def height_to_inches(code):
    try:
        code = int(code)
        return (code // 1000) * 12 + ((code % 1000) // 10) + (code % 10) / 8
    except:
        return None

data["HEIGHT"] = data["HEIGHT"].apply(height_to_inches)

# Filters
conf = st.selectbox("Conference", ["All"] + sorted(data["CONFERENCE"].dropna().unique()))
state = st.selectbox("Home State", ["All"] + sorted(data["HOME STATE"].dropna().unique()))
if conf != "All":
    data = data[data["CONFERENCE"] == conf]
if state != "All":
    data = data[data["HOME STATE"] == state]

# Slider filters
data = data[(data['HEIGHT'].between(*st.slider("Height", 66.0, 80.0, (66.0, 80.0), 0.5))) &
            (data['Composite Score'].between(*st.slider("Composite Score", 1.0, 7.0, (1.0, 7.0), 0.5)))]

# Player links
data["PLAYER_DETAIL_LINK"] = data["PLAYER_ID"].apply(lambda pid: f"/QB_Path_Evaluations?player_id={quote(pid)}")

# Display table
cols = ["PLAYER_DETAIL_LINK", "NAME", "PROJECTED POSITION", "SCHOOL", "CONFERENCE", "HEIGHT", "HOME STATE", "Composite Score", "Ideal Scheme"]
st.dataframe(
    data[cols],
    column_config={"PLAYER_DETAIL_LINK": st.column_config.LinkColumn(label="View", display_text="Evaluation")},
    hide_index=True
)