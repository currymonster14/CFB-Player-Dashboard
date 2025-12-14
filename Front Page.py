# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 21:22:08 2025

@author: jayap
"""
import streamlit as st

st.set_page_config(page_title="Position Dashboard", layout="centered")
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

st.title("🏈 Player Evaluation Dashboards")
st.markdown("### Select a Position:")

st.page_link("pages/QB_Dashboard.py", label="Quarterback (QB)")
st.page_link("pages/RB_Dashboard.py", label="Running Back (RB)")
st.page_link("pages/WR_Dashboard.py", label="Wide Receiver (WR)")
st.page_link("pages/TE_Dashboard.py", label="Tight End (TE)")
st.page_link("pages/OT_Dashboard.py", label="Offensive Tackles (OT)")
st.page_link("pages/IOL_Dashboard.py", label="Interior Offensive Line (IOL)")
# st.page_link("pages/DL_Dashboard.py", label="Defensive Line (DL)")
# st.page_link("pages/LB_Dashboard.py", label="Linebacker (LB)")
# st.page_link("pages/DB_Dashboard.py", label="Defensive Back (DB)")