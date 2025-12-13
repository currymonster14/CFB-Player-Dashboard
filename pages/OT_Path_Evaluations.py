# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:09:59 2025

@author: jayap
"""

# Full-featured QB_Path_Evaluations.py with sliders and PFF tables
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
#st.set_page_config(page_title="Player Evaluation", layout="wide")

# ----------------------------
# Functions
# ----------------------------

def load_data():
    df1 = pd.read_excel("Utah Transfer Portal Master Sheet.xlsx", sheet_name=5, header = 1)
    df2 = pd.read_excel("Utah TP Cross Check Board.xlsx", sheet_name=6)
    data = pd.merge(df1, df2, how="left", on="Name")

    # clean columns
    data = data.dropna(subset=["Film Grade"])
    data["Name"] = data["Name"].astype(str).str.strip()
    data["GRADE"] = pd.to_numeric(data["GRADE"], errors="coerce").round(2)
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

def film_color(val):
    if val <= 3.75:
        return "red"
    elif val <= 4.5:
        return "gold"
    else:
        return "green"

def prospect_color(val):
    if val <= 40:
        return "red"
    elif val <= 70:
        return "gold"
    else:
        return "green"

def pass_color(val):
    if val <= 0.96:
        return "red"
    elif val <= 0.98:
        return "gold"
    else:
        return "green"

def run_color(val):
    if val <= -0.2:
        return "red"
    elif val <= -0.1:
        return "gold"
    else:
        return "green"
    
def single_bar(title, value, x_range, color):
    fig = go.Figure(go.Bar(
        x=[value],
        y=["metric"],
        orientation="h",
        marker=dict(color=color),
        text=[f"{value:.2f}"],
        textposition="auto",
        showlegend=False
    ))

    fig.update_layout(
        title=dict(text=title, x=0.25, font=dict(size=18)),
        xaxis=dict(range=x_range, showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False),
        height=90,
        margin=dict(l=10, r=10, t=35, b=5)
    )
    return fig

def display_player(player):

    # =======================
    # BIO / HEADER
    # =======================
    st.markdown(
        f"""
        <h1 style='text-align:center; font-size:70px; margin-bottom:0.1em;'>
            {player['Name']} – {player['Position']}
        </h1>
        <h2 style='text-align:center; font-size:30px; margin-top:0;'>
            {player['COLLEGE']} • #{player['Number']} • {player['Conference']}
        </h2>
        """,
        unsafe_allow_html=True
    )

    # =======================
    # TOP SECTION
    # =======================
    col_left, col_right = st.columns(2)

    # ---------- LEFT ----------
    with col_left:
        st.markdown("<h3 style='text-align:center;'>Production and Film Ranking</h3>", unsafe_allow_html=True)

        prospect_data = {
            "FCS Prospect %": player["FCS Prospect Percentile"] * 100,
            "G5 Prospect %": player["G5 Prospect Percentile"] * 100,
            "P4 Prospect %": player["P4 Prospect Percentile"] * 100
        }

        fig = go.Figure(go.Bar(
            x=list(prospect_data.values()),
            y=list(prospect_data.keys()),
            orientation="h",
            marker=dict(color=[prospect_color(v) for v in prospect_data.values()]),
            text=[f"{v:.1f}%" for v in prospect_data.values()],
            textposition="auto"
        ))

        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)


    # ---------- RIGHT ----------
    with col_right:
        st.markdown("<h3 style='text-align:center;'>Projection and Tier</h3>", unsafe_allow_html=True)

        # Pass
        fig = single_bar(
            "Film Grade",
            player["Film Grade"],
            [1, 7],
            film_color(player["Film Grade"])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pass
        fig = single_bar(
            "Pass Blocking Efficiency",
            player["Pass Block Efficiency"],
            [0.95, 1.00],
            pass_color(player["Pass Block Efficiency"])
        )
        st.plotly_chart(fig, use_container_width=True)

        # Run metrics side-by-side
        run_cols = st.columns(3)
        run_metrics = {
            "Run": player["Run Block Success"],
            "Zone": player["Zone Run Block Success"],
            "Gap": player["Gap Run Block Success"]
        }

        for (label, value), col in zip(run_metrics.items(), run_cols):
            with col:
                fig = single_bar(label, value, [-1, 1], run_color(value))
                st.plotly_chart(fig, use_container_width=True)

    # =======================
    # MIDDLE TABLE
    # =======================
    st.markdown(
        f"""
        **Transfer Portal:** {player['TRANSFER PORTAL']} | **Tier:** {player['TIER']} | **Scheme Fit:** {player['SCHEME FIT']}
        | **Archetype:** {player['ARCHETYPE']}
        """
    )
    st.markdown("<h2 style='text-align:center;'>Player Grades</h2>", unsafe_allow_html=True)

    pass_data, run_data = get_pass_run_data(player)
    n_rows = max(len(pass_data), len(run_data))

    table_html = """
    <table style="border-collapse:collapse; width:100%;">
        <tr>
            <th colspan="2" style="border:1px solid black;">Pass Catching</th>
            <th colspan="2" style="border:1px solid black;">Run Blocking</th>
        </tr>
        <tr>
            <th style="border:1px solid black;">Question</th>
            <th style="border:1px solid black;">Evaluation</th>
            <th style="border:1px solid black;">Question</th>
            <th style="border:1px solid black;">Evaluation</th>
        </tr>
    """

    for i in range(n_rows):
        table_html += "<tr>"

        for dataset in (pass_data, run_data):
            if i < len(dataset):
                q, a = dataset[i]
                table_html += f"<td style='border:1px solid black;'><b>{q}</b></td>"
                table_html += f"<td style='border:1px solid black;'>{a}</td>"
            else:
                table_html += "<td style='border:1px solid black;'></td>" * 2

        table_html += "</tr>"

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    

def get_pass_run_data(player):
    # Map question -> column in Excel
    pass_questions = {
        "Handles Outside Shoulder": "Handles Outside Shoulder",
        "Handles Power Thru Him": "Handles Power Thru Him",
        "Handles Inside Shoulder": "Handles Inside Shoulder",
    }

    run_questions = {
        "Drive/Engage/Finish": "Drive/Engage/Finish",
        "Space Pursuit Angles": "Space Pursuit Angles",
        "Space Block Finishing": "Space Block Finishing"
    }

    # Build lists of tuples (Question, Answer)
    pass_data = [(q, player[col]) for q, col in pass_questions.items() if col in player.index]
    run_data = [(q, player[col]) for q, col in run_questions.items() if col in player.index]

    return pass_data, run_data

# ----------------------------
# Main
# ----------------------------
params = st.query_params
player_id = params.get("player_id", [])

if not player_id:
    st.warning("No player selected. Go to a dashboard first.")
    st.stop()

data = load_data()
player = data[data["player_id"] == player_id]

if player.empty:
    st.error(f"No player found with player_id: {player_id}")
else:
    display_player(player.iloc[0])