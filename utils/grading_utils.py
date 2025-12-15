# -*- coding: utf-8 -*-
"""
Created on Sun Dec 14 13:17:00 2025

@author: jayap
"""

import pandas as pd

GRADE_RANGES = [
    (1.0, 3.0, "Weakness", "red"),
    (3.0, 5.0, "Average",  "yellow"),
    (5.0, float("inf"), "Strength", "green"),
]

def grade_to_answer_and_color(val, ranges=GRADE_RANGES):
    if pd.isna(val):
        return "N/A", "gray"

    for low, high, label, color in ranges:
        if low <= val < high:
            return label, color

    return "Out of Range", "gray"