# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 22:03:26 2025

@author: jayap
"""
# Full-featured QB_Path_Evaluations.py with sliders and PFF tables
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils.grading_utils import grade_to_answer_and_color
st.set_page_config(page_title="WR Evaluation", layout="wide")

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
    df1 = pd.read_excel("Utah Transfer Portal Master Sheet.xlsx", sheet_name=3)
    df2 = pd.read_excel("Utah TP Cross Check Board.xlsx", sheet_name=4)
    data = pd.merge(df1, df2, how="left")

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

def render_side_by_side_table(player, pass_questions_list, run_questions_list, title=None):
    if title:
        st.subheader(title)

    # Determine max rows for looping
    n_rows = max(len(pass_questions_list), len(run_questions_list))

    html_table = """
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <th style="border:1px solid black; text-align:center;">Pass Criteria</th>
            <th style="border:1px solid black; text-align:center;">Evaluation</th>
            <th style="border:1px solid black; text-align:center;">Run Criteria</th>
            <th style="border:1px solid black; text-align:center;">Evaluation</th>
        </tr>
    """

    color_map = {"green": "#2ecc71", "yellow": "#f1c40f", "red": "#e74c3c", "gray": "#bdc3c7"}

    for i in range(n_rows):
        html_table += "<tr>"

        # Pass side
        if i < len(pass_questions_list):
            q = pass_questions_list[i]
            question = q["question"]
            answer_col = q["answer_col"]
            grade_col = q["grade_col"]
            answer = player[answer_col] if answer_col in player.index else "N/A"
            grade_val = player[grade_col] if grade_col in player.index else None
            _, color = grade_to_answer_and_color(grade_val)
            color_hex = color_map.get(color, "#bdc3c7")

            html_table += f'<td style="border:1px solid black; text-align:center; padding:4px;"><b>{question}</b></td>'
            html_table += f'<td style="border:1px solid black; text-align:left; padding:4px; background-color:{color_hex};">{answer}</td>'
        else:
            html_table += '<td style="border:1px solid black;"></td><td style="border:1px solid black;"></td>'

        # Run side
        if i < len(run_questions_list):
            q = run_questions_list[i]
            question = q["question"]
            answer_col = q["answer_col"]
            grade_col = q["grade_col"]
            answer = player[answer_col] if answer_col in player.index else "N/A"
            grade_val = player[grade_col] if grade_col in player.index else None
            _, color = grade_to_answer_and_color(grade_val)
            color_hex = color_map.get(color, "#bdc3c7")

            html_table += f'<td style="border:1px solid black; text-align:center; padding:4px;"><b>{question}</b></td>'
            html_table += f'<td style="border:1px solid black; text-align:left; padding:4px; background-color:{color_hex};">{answer}</td>'
        else:
            html_table += '<td style="border:1px solid black;"></td><td style="border:1px solid black;"></td>'

        html_table += "</tr>"

    html_table += "</table>"

    st.markdown(html_table, unsafe_allow_html=True)

            
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
            {player['COLLEGE']} • #{player['#']} • {player['CONF']}
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
    
    def value_to_color(val):
        if val <= 40:
            return "red"
        elif val <= 70:
            return "yellow"
        else:
            return "green"

    bar_colors = [value_to_color(v) for v in prospect_data.values()]
    
    # Split page in half
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(
            f"""
            <h1 style='text-align: center; font-size: 22px';> 
            Production and Film Ranking
            </h1>
            """,
            unsafe_allow_html = True
        )
    
        fig = go.Figure(go.Bar(
            x=list(prospect_data.values()),
            y=list(prospect_data.keys()),
            orientation='h',
            marker=dict(
                color=bar_colors,  # later you can customize colors based on value
            ),
            text=[f"{v}%" for v in prospect_data.values()],
            textposition='auto'
        ))
    
        fig.update_layout(
            xaxis_title="Percentile",
            yaxis_title="",
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
    
        st.plotly_chart(fig, use_container_width=True)

        # Example data
    player_metrics = {
        "Quality of Player": player["Film Grade"],
        "Average Value Metric": player["Average Value"]
    }
    

    ### Top Right Information
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
        fit = player["SCHEME FIT"]
        arch = player["ARCHETYPE"]
            
        
    st.markdown(
    f"""
    <div style="text-align: center; font-size: 18px;">
        <b>Transfer Portal:</b> {player['TRANSFER PORTAL']} &nbsp;|&nbsp;
        <b>Tier:</b> {player['TIER']} &nbsp;|&nbsp;
        <b>Role:</b> {proj} &nbsp;|&nbsp;
        <b>Scheme Fit:</b> {fit} &nbsp;|&nbsp;
        <b>Archetype:</b> {player['ARCHETYPE']}
    </div>
    """,
    unsafe_allow_html=True
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

    pass_questions = [
    {"question": "Vs Press Coverage", "answer_col": "Vs Press Coverage", "grade_col": "Grade"},
    {"question": "vs Off Coverage", "answer_col": "vs Off Coverage", "grade_col": "Grade.1"},
    {"question": "vs Man Coverage", "answer_col": "vs Man Coverage", "grade_col": "Grade.2"},
    {"question": "vs Zone Coverage", "answer_col": "vs Zone Coverage", "grade_col": "Grade.3"},
    ]

    run_questions = [
        {"question": "Ball Skills", "answer_col": "Ball Skills", "grade_col": "Grade.4"},
        {"question": "Field Stretching", "answer_col": "Field Stretching", "grade_col": "Grade.5"},
        {"question": "Yards After Catch/Contact", "answer_col": "Yards After Catch/Contact", "grade_col": "Grade.6"}
    ]

    render_side_by_side_table(player, pass_questions, run_questions, title="Player Evaluation")

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

##Middle Table
st.markdown(
    f"""
    <h1 style='text-align: center; font-size: 30px'>
        Player Grades
    </h1>
    <h2 style='text-align: center; font-size: 30px'>
        Compare Two Players Side-By-Side
    </h2>
    """,
    unsafe_allow_html = True
)

# Map question -> column in Excel
pass_questions = [
    {"question": "Vs Press Coverage", "answer_col": "Vs Press Coverage", "grade_col": "Grade"},
    {"question": "vs Off Coverage", "answer_col": "vs Off Coverage", "grade_col": "Grade.1"},
    {"question": "vs Man Coverage", "answer_col": "vs Man Coverage", "grade_col": "Grade.2"},
    {"question": "vs Zone Coverage", "answer_col": "vs Zone Coverage", "grade_col": "Grade.3"},
]

run_questions = [
    {"question": "Ball Skills", "answer_col": "Ball Skills", "grade_col": "Grade.4"},
    {"question": "Field Stretching", "answer_col": "Field Stretching", "grade_col": "Grade.5"},
    {"question": "Yards After Catch/Contact", "answer_col": "Yards After Catch/Contact", "grade_col": "Grade.6"}
]


player1 = player.iloc[0]  # the current page’s player
player2_name = st.selectbox("Select Player 2", [""] + list(data["Name"].sort_values().unique()))

if player2_name:  # Only run if something is selected
    player2_df = data[data["Name"] == player2_name]
    if not player2_df.empty:
        player2 = player2_df.iloc[0]
    else:
        st.warning(f"No player found with name {player2_name}")
        player2 = None
else:
    player2 = None


if player2 is not None:
    # render side-by-side table with player1 and player2
    # Combine questions for comparison
    comparison_questions = pass_questions + run_questions

    # Build DataFrame
    comparison_df = pd.DataFrame({
        "Criteria Question": [q["question"] for q in comparison_questions],
        "Player 1": [player1[q["answer_col"]] if q["answer_col"] in player1.index else "N/A" for q in comparison_questions],
        "Player 2": [player2[q["answer_col"]] if q["answer_col"] in player2.index else "N/A" for q in comparison_questions],
        "Player 1 Grade": [player1[q["grade_col"]] if q["grade_col"] in player1.index else None for q in comparison_questions],
        "Player 2 Grade": [player2[q["grade_col"]] if q["grade_col"] in player2.index else None for q in comparison_questions],
    })

    color_map = {"green": "#2ecc71", "yellow": "#f1c40f", "red": "#e74c3c", "gray": "#bdc3c7"}

    col1, col2, col3 = st.columns([3,4,3])
    
    # Player names at top
    col1.markdown(
        f"<div style='font-weight:bold; text-align:center; font-size:15px; padding:12px;'>{player1['Name']}</div>", 
        unsafe_allow_html=True
    )
    col2.markdown(
        f"<div style='font-weight:bold; text-align:center; font-size:15px; padding:12px'>Criteria Questions</div>", 
        unsafe_allow_html=True
    )
    col3.markdown(
        f"<div style='font-weight:bold; text-align:center; font-size:15px; padding:12px;'>{player2['Name']}</div>", 
        unsafe_allow_html=True
    )
    
    for idx, row in comparison_df.iterrows():
        
        
        _, color1 = grade_to_answer_and_color(row["Player 1 Grade"])
        _, color2 = grade_to_answer_and_color(row["Player 2 Grade"])
        
        # Player 1
        col1.markdown(
            f"<div style='background-color:{color_map.get(color1,'gray')}; "
            f"padding:8px; border-radius:5px; text-align:center; vertical-align:middle; height:40px;'>"
            f"{row['Player 1']}</div>",
            unsafe_allow_html=True
        )
        
        # Criteria
        col2.markdown(
            f"<div style='text-align:center; font-weight:bold; padding:8px; vertical-align:middle; height:40px;'>"
            f"{row['Criteria Question']}</div>",
            unsafe_allow_html=True
        )
        
        # Player 2
        col3.markdown(
            f"<div style='background-color:{color_map.get(color2,'gray')}; "
            f"padding:8px; border-radius:5px; text-align:center; vertical-align:middle; height:40px;'>"
            f"{row['Player 2']}</div>",
            unsafe_allow_html=True
        )

    # Player Film Grades
    st.markdown("<br><br>", unsafe_allow_html=True)
    player1_grade = player1["Film Grade"]
    player2_grade = player2["Film Grade"]
    
    # Negative for left side
    player1_grade_neg = -player1_grade
    
    fig = go.Figure()
    
        # Player 1 bar (left) with dynamic color
    fig.add_trace(go.Bar(
        x=[player1_grade_neg],
        y=["Film Grade"],  # single row
        orientation='h',
        name=player1['Name'],
        marker_color=film_color(player1_grade),
        text=[f"{player1['Name']} - {player1_grade:.2f}"],
        textposition="inside",
        insidetextanchor="middle",
        width=0.6  # thicker bar
    ))
    
    # Player 2 bar (right) with dynamic color
    fig.add_trace(go.Bar(
        x=[player2_grade],
        y=["Film Grade"],
        orientation='h',
        name=player2['Name'],
        marker_color=film_color(player2_grade),
        text=[f"{player2['Name']} - {player2_grade:.2f}"],
        textposition="inside",
        insidetextanchor="middle",
        width=0.6
    ))
    
    fig.update_layout(
        barmode='overlay',
        title=dict(
            text="Film Grade Comparison",
            x=0.5,           # center the title
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=True
        ),
        yaxis=dict(
            showticklabels=False
        ),
        height=300,
        plot_bgcolor='white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    pass


else:
    st.info("Select a player to see a comparison.")