# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 21:22:08 2025

@author: jayap
"""
import streamlit as st

st.set_page_config(page_title="Position Dashboard", layout="centered")

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
# 🔒 Hide this page from the sidebar
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
st.page_link("pages/CB_Dashboard.py", label="Cornerback (CB)")
st.page_link("pages/DB_Dashboard.py", label="Defensive Back (DB)")

st.markdown("---")
st.markdown("## Overview")

col1, col2, col3 = st.columns(3)

# ----------------------------
# Film Grade Methodology
# ----------------------------
with col1:
    st.markdown("""
    ### 🎥 Film Grade Methodology

    Every player in this dashboard has a **film grade**. Each position is evaluated using
    a set of **position-specific criteria questions** that emphasize:
    - Functional movement  
    - Functional strength  
    - Functional length  
    - Ability to win within role and scheme  

    Each question is graded based on an **average expected outcome**, with every outcome
    assigned a numerical value on a **1–7 scale**.
    Using **weighted sums** across all criteria, each player receives a final
    **Composite Film Grade** on a **1–7 scale**.

    **Tier Definitions**:
    - **P4 Starter**: 4.50+  
    - **P4 Spot Starter**: 4.25–4.49  
    - **G5 Starter**: 3.75–4.24  
    - **G5 Spot Starter**: 3.50–3.74  
    - **G5 Backup**: Below 3.50  
    """)

# ----------------------------
# Custom Metrics
# ----------------------------
with col2:
    st.markdown("""
    ### 📊 Custom Metrics

    In addition to film, this dashboard includes **custom-built metrics** designed to add
    context to player evaluation.

    These metrics are used to:
    - Compare players within similar competition levels  
    - Identify production versus projection gaps  
    - Provide additional context beyond box score scouting  

    Metrics are not intended to replace film, but to **support and validate**
    film-based conclusions.

    **Created Metrics Explained**:
    - **Average Value (Offense)**: Measures how valuable a player's production is to the
      overall team operation. *(A positive value suggests the player is outperforming team context.)*
    - **Average Value (Defense)**: Measures how much a defender contributes to the team’s
      total defensive production.
    - **Run Blocking Success (OT & IOL)**: Measures how often a player contributes to
      successful rushing plays.  
      *(Example: 0.10 = 1 successful contribution every 10 runs.)*
    """)

# ----------------------------
# Color Bank
# ----------------------------
with col3:
    st.markdown("""
    ### 🎨 Color Key

    🟩 **Green**  
    High-level traits with strong translation potential  

    🟨 **Yellow / Gold**  
    Adequate, situational, or role-dependent strengths  

    🟥 **Red**  
    Below replacement-level traits or limited projection  

    Color is used to support **quick visual scanning** across tables and charts.
    """)
