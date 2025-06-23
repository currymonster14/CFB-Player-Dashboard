# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 22:03:26 2025

@author: jayap
"""
# Full-featured QB_Path_Evaluations.py with sliders and PFF tables
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Player Details", layout="wide")

# Load data
def load_data():
    df1 = pd.read_excel('CFB Player Combined Table.xlsx', sheet_name=0)
    df2 = pd.read_excel('CFB Player Combined Table.xlsx', sheet_name=1)
    df3 = pd.read_excel('CFB Player Combined Table.xlsx', sheet_name=2)
    df = pd.merge(pd.merge(df1, df2, how='right'), df3, how='left')
    df = df.dropna(subset=["PLAYER_ID", "NAME"])
    df["PLAYER_ID"] = df["PLAYER_ID"].astype(str).str.strip()
    # df = df.dropna(subset = ["Written Evaluation"])
    return df.reset_index(drop=True)
    

def load_pff_data():
    return pd.read_excel("Data Tables/PFF QB Data.xlsx")

def height_to_inches(code):
    try:
        code = int(code)
        return (code // 1000) * 12 + ((code % 1000) // 10) + (code % 10) / 8
    except:
        return None

def round_score(score):
    return round(score, 2)

def display_player(player, pff_df):
    st.title(f"Player: {player['NAME']}")
    bio_col, img_col = st.columns([3, 1])

    with bio_col:
        st.subheader(f"School: {player['SCHOOL']}")
        st.subheader(f"Height: {player['HEIGHT']} | Weight: {player['WEIGHT']:.0f} | Hometown: {player['HOMETOWN']}, {player['HOME STATE']}")
        st.subheader(f"Position: {player['PROJECTED POSITION']}")
        st.subheader(f"Scheme: {player['Ideal Scheme']}")
        st.subheader(f"Composite Score: {player['Composite Score']:.2f}")
        # for col in player.index[9]:
        #     st.slider(col, 1.0, 7.0, float(player[col]), step = 0.5, disabled = True)

    with img_col:
        img_path = os.path.join("images", f"{player['NAME']} Profile.png")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.write("No image available.")

    st.markdown("### 🔢 Player Grades")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Athletic Ability")
        for col in player.index[13:19]:
            st.slider(col, 1, 7, int(player[col]), 1, disabled=True)

    with col2:
        st.subheader("Pass Grades")
        for col in player.index[19:24]:
            st.slider(col, 1, 7, int(player[col]), 1, disabled=True)

    with col3:
        st.subheader("Run Grades")
        for col in player.index[24:26]:
            st.slider(col, 1, 7, int(player[col]), 1, disabled=True)

    st.markdown("---")
    pff_row = pff_df[pff_df["PLAYER_ID"].astype(str).str.strip() == player["PLAYER_ID"]]

    if not pff_row.empty:
        pff_row = pff_row.reset_index(drop=True).drop(pff_row.columns[:3], axis=1)
        pff_row["COMP%"] = pd.to_numeric(pff_row["COMP%"], errors="coerce") * 100
        pff_row["TURNOVER WORTHY PLAY %"] = pd.to_numeric(pff_row["TURNOVER WORTHY PLAY %"], errors="coerce") * 100
        pff_row["BIG TIME THROW %"] = pd.to_numeric(pff_row["BIG TIME THROW %"], errors="coerce") * 100
        pff_display = pff_row.T.reset_index()
        pff_display.columns = ["Metric", "Value"]

        split_idx = pff_display[pff_display["Metric"].str.lower().str.strip() == "sacks"].index
        split_at = split_idx[0] + 1 if not split_idx.empty else len(pff_display)
        box_df = pff_display.iloc[:split_at]
        adv_df = pff_display.iloc[split_at:]
        

        table_col, eval_col = st.columns([2, 2])

        with table_col:
            st.markdown("### 📊 PFF Stats")
            st.markdown("#### Box Score")
            st.dataframe(box_df, hide_index=True, use_container_width=True)
            if not adv_df.empty:
                st.markdown("#### Advanced Metrics")
                st.dataframe(adv_df, hide_index=True, use_container_width=True)

        with eval_col:
            st.markdown("### 📝 Written Evaluation")
            st.markdown(player.get("Written Evaluation", "No evaluation available."))
    else:
        st.markdown("### 📝 Written Evaluation")
        st.markdown(player.get("Written Evaluation", "No evaluation available."))
        st.info("No PFF data available for this player.")

# Main
player_id = st.query_params['player_id']
if not player_id:
    st.error("No player ID provided.")
    st.stop()

if isinstance(player_id, list):
    player_id = player_id[0]

data = load_data()
data["HEIGHT"] = data["HEIGHT"].apply(height_to_inches)
data["Composite Score"] = data["Composite Score"].apply(round_score)
player = data[data["PLAYER_ID"] == player_id]
pff_df = load_pff_data()

if player.empty:
    st.error(f"No player found with PLAYER_ID: {player_id}")
else:
    display_player(player.iloc[0], pff_df)
