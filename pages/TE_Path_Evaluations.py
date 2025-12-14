# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 22:06:37 2025

@author: jayap
"""
# Full-featured QB_Path_Evaluations.py with sliders and PFF tables
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
st.set_page_config(page_title="OT Evaluation", layout="wide")

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

# ----------------------------
# Functions
# ----------------------------

def load_data():
    df1 = pd.read_excel("Utah Transfer Portal Master Sheet.xlsx", sheet_name=4)
    df2 = pd.read_excel("Utah TP Cross Check Board.xlsx", sheet_name=5)
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
        data["Team"].str.replace(r"[^A-Za-z0-9]", "", regex=True).str.lower()
    )
    return data.reset_index(drop=True)

def film_color(val):
    if val <= 3.75:
        return "red"
    elif val <= 4.25:
        return "gold"
    elif val <=4.49:
        return "orange"
    else:
        return "green"

def prospect_color(val):
    if val <= 40:
        return "red"
    elif val <= 70:
        return "gold"
    else:
        return "green"

def av_color(val):
    if val <= -1:
        return "red"
    elif val <= 1:
        return "gold"
    else:
        return "green"

def metric_bar(title, value, x_range, color):
    fig = go.Figure(go.Bar(
        x=[value],
        y=["metric"],
        orientation="h",
        marker=dict(color=color),
        text=[f"{value:.1f}"],
        textposition="outside",
        showlegend=False
    ))

    fig.update_layout(
        title=dict(
            text=title,
            x=0,
            xanchor="left",
            font=dict(size=20)
        ),
        xaxis=dict(range=x_range, showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False),
        height=90,
        margin=dict(l=20, r=20, t=30, b=10)
    )

    return fig

def display_player(player):
    
    ###Bio
    college = player["COLLEGE"]
    number = player["#"]
    position = player["POS"]
    conference = player["CONF"]
    player_name = player['Name']
    st.markdown(
        f"""
        <h1 style='text-align: center; font-size: 70px'; margin-bottom: .05em;'>
            {player_name} - {position}
        </h1>
        """,
        unsafe_allow_html = True
    )
    st.markdown(
        f"""
        <h2 style='text-align:center; font-size:30px; margin-top:0;'>
            {player['COLLEGE']} • #{int(player['#'])} • {player['Conference']}
        </h2>
        """,
        unsafe_allow_html=True
    )

    #Top Left Graph
    prospect_data = {
        "FCS Prospect %": pd.to_numeric((player['FCS Prospect Percentile']*100), errors="coerce").round(2),
        "G5 Prospect %": pd.to_numeric((player['G5 Prospect Percentile']*100), errors="coerce").round(2),
        "P4 Prospect %": pd.to_numeric((player['P4 Prospect Percentile']*100), errors="coerce").round(2)
    }

    # Split page in half
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(
            "<h1 style='text-align: center; font-size: 22px;'>Production and Film Ranking</h1>",
            unsafe_allow_html=True
        )
    
        fig = go.Figure(go.Bar(
            x=list(prospect_data.values()),
            y=list(prospect_data.keys()),
            orientation="h",
            marker=dict(
                color=[prospect_color(v) for v in prospect_data.values()]
            ),
            text=[f"{v}%" for v in prospect_data.values()],
            textposition="auto"
        ))
    
        fig.update_layout(
            xaxis_title="Percentile",
            yaxis_title="",
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
    
        st.plotly_chart(fig, use_container_width=True)

        # Example data
    
    

    with col_right:
        player_metrics = {
            "Quality of Player": player["Film Grade"],
            "Average Value Metric": player["Average Value"]
        }
        st.markdown(
            "<h1 style='text-align: center; font-size: 22px;'>Projection</h1>",
            unsafe_allow_html=True
        )
    
        st.plotly_chart(
            metric_bar(
                "Film Grade",
                player["Film Grade"],
                [1, 7],
                film_color(player["Film Grade"])
            ),
            use_container_width=True
        )
    
        st.plotly_chart(
            metric_bar(
                "Average Value",
                player["Average Value"],
                [-10, 10],
                av_color(player["Average Value"])
            ),
            use_container_width=True
        )
        portal_entry = player["TRANSFER PORTAL"]
        tier = player["TIER"]
        proj = player["PRO PROJECTION"]
        ##fit = player["SCHEME FIT"]
        arch = player["ARCHETYPE"]
            
        
    st.markdown(
        f"""
        **Transfer Portal:** {player['TRANSFER PORTAL']} | **Tier:** {player['TIER']}
        \n **Scheme Fit:** {player['PRO PROJECTION']} | **Archetype:** {player['ARCHETYPE']}
        """
    )
    
    ##Middle Table
    st.markdown(
        f"""
        <h1 style='text-align: center; font-size: 30px'>
            Player Grades
        </h1>
        """,
        unsafe_allow_html = True
    )

    pass_data, run_data = get_pass_run_data(player)
        
    # Build HTML table
    html_table = """
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td colspan="2" style="border: 1px solid black; text-align:center;">Pass Catching</td>
            <td colspan="2" style="border: 1px solid black; text-align:center;">Run Blocking</td>
        </tr>
        <tr>
            <td style="border: 1px solid black; text-align:center;"> Criteria Question</td>
            <td style="border: 1px solid black; text-align:center;">Evaluation</td>
            <td style="border: 1px solid black; text-align:center;">Criteria Question</td>
            <td style="border: 1px solid black; text-align:center;">Evaluation</td>
        </tr>
    """
    
    # Number of rows is max of pass/run
    n_rows = max(len(pass_data), len(run_data))
    
    for i in range(n_rows):
        html_table += "<tr>"
        # Pass column
        if i < len(pass_data):
            q, a = pass_data[i]
            html_table += f'<th style="border: 1px solid black;">{q}</td>'
            html_table += f'<td style="border: 1px solid black;">{a}</td>'
        else:
            html_table += '<th style="border: 1px solid black;"></td>' * 2
    
        # Run column
        if i < len(run_data):
            q, a = run_data[i]
            html_table += f'<th style="border: 1px solid black;">{q}</td>'
            html_table += f'<td style="border: 1px solid black;">{a}</td>'
        else:
            html_table += '<th style="border: 1px solid black;"></td>' * 2
    
        html_table += "</tr>"
    
    html_table += "</table>"

    st.markdown(html_table, unsafe_allow_html=True)
    
    

def get_pass_run_data(player):
    # Map question -> column in Excel
    pass_questions = {
        "vs Man Coverage": "vs Man Coverage",
        "vs Zone Coverage": "vs Zone Coverage",
        "Ball Skills": "Ball Skills",
        "Field Stretching": "Field Stretching",
        "Yards After Catch/Contact": "Yards After Catch/Contact"
    }

    run_questions = {
        "Inline Blocking": "Inline Blocking",
        "Toughness As Blocker": "Toughness As Blocker",
        "Pursuit Angles As Blocker": "Pursuit Angles As Blocker",
        "Leg Drive": "Leg Drive"
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