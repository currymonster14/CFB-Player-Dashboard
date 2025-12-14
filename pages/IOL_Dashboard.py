# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 16:11:52 2025

@author: jayap
"""

import os
import pandas as pd
import streamlit as st
from urllib.parse import quote

st.set_page_config(page_title="IOL Dashboard", layout="wide")
# 🔒 Hide this page from the sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] a[href*="Path_Evaluations"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
def load_data():
    df1 = pd.read_excel("Utah Transfer Portal Master Sheet.xlsx", sheet_name=6, header = 1)
    df2 = pd.read_excel("Utah TP Cross Check Board.xlsx", sheet_name=13, header = 1)
    data = pd.merge(df1, df2, how="left", on="Name")
    data = data.dropna(subset=["Film Grade"])
    data["Name"] = data["Name"].astype(str).str.strip()
    data["GRADE"] = pd.to_numeric(data["GRADE"], errors="coerce").round(2)
    # Split name into first and last
    data["FirstName"] = data["Name"].str.split().str[0]
    data["LastName"]  = data["Name"].str.split().str[-1]
    #Create player_id: FirstName_LastName_School (all lowercase, underscores)
    data["player_id"] = (
        data["FirstName"].str.replace(r"[^A-Za-z0-9]", "", regex=True).str.lower()
        + "_" +
        data["LastName"].str.replace(r"[^A-Za-z0-9]", "", regex=True).str.lower()
        + "_" +
        data["School"].str.replace(r"[^A-Za-z0-9]", "", regex=True).str.lower()
    )
    return data.reset_index(drop=True)

data = load_data()

# Slider filter
st.markdown("### Composite Score")
min_grade, max_grade = st.slider("Composite Score", 1.0, 7.0, (1.0, 7.0), 0.1)
data = data[data['GRADE'].between(min_grade, max_grade)]
# Filters
# ----------------------------
st.markdown("### Filters")

col1, col2, col3, col4, col5 = st.columns(5)
st.divider()
with col1:
    conf = st.multiselect(
        "Conference",
        ["All"] + sorted(data["Conference"].dropna().unique()),
        default=["All"]
    )

with col2:
    arch = st.multiselect(
        "Archetype",
        ["All"] + sorted(data["ARCHETYPE"].dropna().unique()),
        default=["All"]
    )

with col3:
    scheme = st.selectbox(
        "Scheme Fit",
        ["All"] + sorted(data["SCHEME FIT"].dropna().unique())
    )

with col4:
    tier = st.multiselect(
        "Tier",
        ["All"] + sorted(data["TIER"].dropna().unique()),
        default=["All"]
    )

with col5:
    portal = st.multiselect(
        "Transfer Portal",
        ["All"] + sorted(data["TRANSFER PORTAL"].dropna().unique()),
        default=["All"]
    )

df = data.copy()
# Apply filters
#if proj and "All" not in proj:
#    data = data[data["PRO PROJECTION"].isin(proj)]
if conf and "All" not in conf:
    data = data[data["Conference"].isin(conf)]
if arch and "All" not in arch:
    data = data[data["ARCHETYPE"].isin(arch)]
if scheme != "All":
    data = data[data["SCHEME FIT"] == scheme]
if tier and "All" not in tier:
    data = data[data["TIER"].isin(tier)]
if portal and "All" not in portal:
    data = data[data["TRANSFER PORTAL"].isin(portal)]



# ----------------------------
# Create clickable LinkColumn
# ----------------------------
# Add clickable link
data["PLAYER_DETAIL_LINK"] = data["player_id"].apply(
    lambda pid: f"IOL_Path_Evaluations?player_id={pid}"
    )

cols = ["PLAYER_DETAIL_LINK", "Name", "COLLEGE", "Conference", "TRANSFER PORTAL", "TIER", "SCHEME FIT", "GRADE", "ARCHETYPE"]

st.write("### Interior Offensive Linemen")
st.dataframe(
    data[cols],
    column_config={
        "PLAYER_DETAIL_LINK": st.column_config.LinkColumn(label="View", display_text="Evaluation")
    },
    hide_index=True
)