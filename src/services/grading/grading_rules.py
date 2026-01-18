# services/grading/grading_rules.py
"""
GRADING RULES - SECONDARY SCHOOLS ONLY (CSEE & ACSEE)
"""

GRADING_SYSTEMS = {
    "csee": {
        "name": "CSEE (Form 4 - O-Level)",
        "level": "ordinary",
        "scale": 100,
        "division": True,
        "points": True,
        "grades": [
            {"grade": "A", "min": 81, "max": 100, "points": 1, "remark": "Excellent"},
            {"grade": "B", "min": 61, "max": 80, "points": 2, "remark": "Very Good"},
            {"grade": "C", "min": 41, "max": 60, "points": 3, "remark": "Good"},
            {"grade": "D", "min": 21, "max": 40, "points": 4, "remark": "Satisfactory"},
            {"grade": "F", "min": 0, "max": 20, "points": 5, "remark": "Fail"}
        ],
        "division_ranges": {
            "I": (7, 17),     # 7-17 points
            "II": (18, 21),   # 18-21 points
            "III": (22, 25),  # 22-25 points
            "IV": (26, 35),   # 26-35 points
            "0": (36, 45)     # 36+ points = Fail
        }
    },
    
    "acsee": {
        "name": "ACSEE (Form 6 - A-Level)",
        "level": "advanced",
        "scale": 100,
        "division": True,
        "points": True,
        "grades": [
            {"grade": "A", "min": 80, "max": 100, "points": 5, "remark": "Excellent"},
            {"grade": "B", "min": 70, "max": 79, "points": 4, "remark": "Very Good"},
            {"grade": "C", "min": 60, "max": 69, "points": 3, "remark": "Good"},
            {"grade": "D", "min": 50, "max": 59, "points": 2, "remark": "Satisfactory"},
            {"grade": "E", "min": 40, "max": 49, "points": 1, "remark": "Pass"},
            {"grade": "F", "min": 0, "max": 39, "points": 0, "remark": "Fail"}
        ],
        "division_ranges": {
            "I": (13, 15),    # 13-15 points (AAA to AAB)
            "II": (10, 12),   # 10-12 points (ABB to BBB)
            "III": (7, 9),    # 7-9 points (BBC to CCC)
            "IV": (4, 6),     # 4-6 points (CCD to DDD)
            "0": (0, 3)       # 0-3 points = Fail
        },
        "min_principals": 3,
        "max_principals": 3
    },
    
    "plse": {
        "name": "PLSE (Std 7 - Primary)",
        "level": "primary",
        "scale": 50,
        "division": False,
        "points": False,
        "grades": [
            {"grade": "A", "min": 40, "max": 50, "remark": "Excellent"},
            {"grade": "B", "min": 30, "max": 39, "remark": "Very Good"},
            {"grade": "C", "min": 20, "max": 29, "remark": "Good"},
            {"grade": "D", "min": 10, "max": 19, "remark": "Satisfactory"},
            {"grade": "E", "min": 0, "max": 9, "remark": "Weak"}
        ]
    }
}


def get_grade_for_marks(system, marks):
    """Get grade for marks"""
    if system not in GRADING_SYSTEMS:
        system = "csee"
    
    try:
        marks = int(float(marks))
    except:
        return GRADING_SYSTEMS[system]["grades"][-1]
    
    # Handle PLSE percentages (if someone enters 85 instead of 42)
    if system == "plse" and 50 < marks <= 100:
        marks = int((marks / 100) * 50)
    
    for grade in GRADING_SYSTEMS[system]["grades"]:
        if grade["min"] <= marks <= grade["max"]:
            return grade
    
    return GRADING_SYSTEMS[system]["grades"][-1]


def calculate_division(points, system="csee"):
    """Calculate division for CSEE or ACSEE"""
    if system not in ["csee", "acsee"] or points is None:
        return None
    
    points = int(points)
    ranges = GRADING_SYSTEMS[system]["division_ranges"]
    
    if ranges["I"][0] <= points <= ranges["I"][1]:
        return "I"
    elif ranges["II"][0] <= points <= ranges["II"][1]:
        return "II"
    elif ranges["III"][0] <= points <= ranges["III"][1]:
        return "III"
    elif ranges["IV"][0] <= points <= ranges["IV"][1]:
        return "IV"
    elif points >= ranges["0"][0]:
        return "0"
    
    return None