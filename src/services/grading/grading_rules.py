# services/grading/grading_rules.py
"""
GRADING RULES - WITH ALL REQUIRED FUNCTIONS
"""

GRADING_SYSTEMS = {
    "csee": {
        "name": "CSEE",
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
        "division": False,
        "points": True,
        "gpa": True,
        "grades": [
            {"grade": "A", "min": 75, "max": 100, "points": 4.0, "remark": "Excellent"},
            {"grade": "B+", "min": 70, "max": 74, "points": 3.5, "remark": "Very Good"},
            {"grade": "B", "min": 65, "max": 69, "points": 3.0, "remark": "Good"},
            {"grade": "C", "min": 60, "max": 64, "points": 2.5, "remark": "Above Average"},
            {"grade": "D", "min": 50, "max": 59, "points": 2.0, "remark": "Average"},
            {"grade": "F", "min": 0, "max": 49, "points": 0.0, "remark": "Fail"}
        ]
    },
    "plse": {
        "name": "PLSE",
        "division": False,
        "points": False,
        "gpa": False,
        "grades": [
            {"grade": "A", "min": 80, "max": 100, "remark": "Excellent"},
            {"grade": "B", "min": 60, "max": 79, "remark": "Very Good"},
            {"grade": "C", "min": 40, "max": 59, "remark": "Good"},
            {"grade": "D", "min": 20, "max": 39, "remark": "Satisfactory"},
            {"grade": "E", "min": 0, "max": 19, "remark": "Weak"}
        ]
    }
}


def get_grade_for_marks(system, marks):
    """Get grade information for given marks in a system"""
    if system not in GRADING_SYSTEMS:
        system = "csee"
    
    try:
        marks = float(marks)
    except (ValueError, TypeError):
        # Return default fail grade for invalid marks
        return GRADING_SYSTEMS[system]["grades"][-1]
    
    for grade_info in GRADING_SYSTEMS[system]["grades"]:
        if grade_info["min"] <= marks <= grade_info["max"]:
            return grade_info
    
    # Default to lowest grade
    return GRADING_SYSTEMS[system]["grades"][-1]


def calculate_division(total_points, system="csee"):
    """Calculate division for CSEE system"""
    if system != "csee":
        return None
    
    if total_points is None:
        return None
    
    ranges = GRADING_SYSTEMS[system]["division_ranges"]
    
    if ranges["I"][0] <= total_points <= ranges["I"][1]:
        return "I"
    elif ranges["II"][0] <= total_points <= ranges["II"][1]:
        return "II"
    elif ranges["III"][0] <= total_points <= ranges["III"][1]:
        return "III"
    elif ranges["IV"][0] <= total_points <= ranges["IV"][1]:
        return "IV"
    elif total_points >= ranges["0"][0]:
        return "0"
    else:
        return None