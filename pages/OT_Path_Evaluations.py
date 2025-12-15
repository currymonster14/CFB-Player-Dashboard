# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:09:59 2025

@author: jayap
"""

# Full-featured QB_Path_Evaluations.py with sliders and PFF tables
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.grading_utils import grade_to_answer_and_color
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
        **Transfer Portal:** {player['TRANSFER PORTAL']} | **Tier:** {player['TIER']} 
        \n**Pass Scheme Fit:** {player['PASS SCHEME FIT']} | **Pass Scheme Fit:** {player['RUN SCHEME FIT']} | **Archetype:** {player['ARCHETYPE']}
        """
    )
    st.markdown("<h2 style='text-align:center;'>Player Grades</h2>", unsafe_allow_html=True)

    # Map question -> column in Excel
    pass_questions = [
    {
        "question": "Handles Outside Shoulder",
        "answer_col": "Handles Outside Shoulder",
        "grade_col": "Grade"
    },
    {
        "question": "Handles Power Thru Him",
        "answer_col": "Handles Power Thru Him",
        "grade_col": "Grade.1"
    },
    {
        "question": "Handles Inside Shoulder",
        "answer_col": "Handles Inside Shoulder",
        "grade_col": "Grade.2"
    }
    ]

    run_questions = [
    {
        "question": "Drive / Engage / Finish",
        "answer_col": "Drive/Engage/Finish",
        "grade_col": "Grade.3"
    },
    {
        "question": "Space Pursuit Angles",
        "answer_col": "Space Pursuit Angles",
        "grade_col": "Grade.4"
    },
    {
        "question": "Space Block Finishing",
        "answer_col": "Space Block Finishing",
        "grade_col": "Grade.5"
    }
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
{
    "question": "Handles Outside Shoulder",
    "answer_col": "Handles Outside Shoulder",
    "grade_col": "Grade"
},
{
    "question": "Handles Power Thru Him",
    "answer_col": "Handles Power Thru Him",
    "grade_col": "Grade.1"
},
{
    "question": "Handles Inside Shoulder",
    "answer_col": "Handles Inside Shoulder",
    "grade_col": "Grade.2"
}
]

run_questions = [
{
    "question": "Drive / Engage / Finish",
    "answer_col": "Drive/Engage/Finish",
    "grade_col": "Grade.3"
},
{
    "question": "Space Pursuit Angles",
    "answer_col": "Space Pursuit Angles",
    "grade_col": "Grade.4"
},
{
    "question": "Space Block Finishing",
    "answer_col": "Space Block Finishing",
    "grade_col": "Grade.5"
}
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