# services/grading/grading_rules.py
"""
GRADING RULES - WHOLE NUMBERS ONLY
"""

GRADING_SYSTEMS = {
    "csee": {
        "name": "CSEE",
        "scale": 100,
        "division": True,
        "points": True,
        "gpa": False,
        "grades": [
            {"grade": "A", "min": 81, "max": 100, "points": 1, "remark": "Excellent"},
            {"grade": "B", "min": 61, "max": 80, "points": 2, "remark": "Very Good"},
            {"grade": "C", "min": 41, "max": 60, "points": 3, "remark": "Good"},
            {"grade": "D", "min": 21, "max": 40, "points": 4, "remark": "Satisfactory"},
            {"grade": "F", "min": 0, "max": 20, "points": 5, "remark": "Fail"}
        ],
        "division_ranges": {
            "I": (7, 17),
            "II": (18, 21),
            "III": (22, 25),
            "IV": (26, 35),
            "0": (36, 45)
        }
    },
    "nacte": {
        "name": "NACTE",
        "scale": 100,
        "division": False,
        "points": True,
        "gpa": True,
        "grades": [
            {"grade": "A", "min": 75, "max": 100, "points": 4, "remark": "Excellent"},
            {"grade": "B+", "min": 70, "max": 74, "points": 3, "remark": "Very Good"},
            {"grade": "B", "min": 65, "max": 69, "points": 3, "remark": "Good"},
            {"grade": "C", "min": 60, "max": 64, "points": 2, "remark": "Above Average"},
            {"grade": "D", "min": 50, "max": 59, "points": 2, "remark": "Average"},
            {"grade": "F", "min": 0, "max": 49, "points": 0, "remark": "Fail"}
        ]
    },
    "plse": {
        "name": "PLSE",
        "scale": 50,
        "division": False,
        "points": False,
        "gpa": False,
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
    """Get grade - whole numbers only"""
    if system not in GRADING_SYSTEMS:
        system = "csee"
    
    try:
        marks = int(float(marks))  # Convert to whole number
    except:
        return GRADING_SYSTEMS[system]["grades"][-1]
    
    # Handle PLSE percentages
    if system == "plse" and 50 < marks <= 100:
        marks = int((marks / 100) * 50)
    
    for grade in GRADING_SYSTEMS[system]["grades"]:
        if grade["min"] <= marks <= grade["max"]:
            return grade
    
    return GRADING_SYSTEMS[system]["grades"][-1]


def calculate_division(points, system="csee"):
    """Calculate division - whole numbers only"""
    if system != "csee" or points is None:
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