# services/grading/grading_rules.py
"""
GRADING RULES FOR DIFFERENT EDUCATION SYSTEMS
"""

GRADING_SYSTEMS = {
    "csee": {
        "name": "CSEE (Form 4)",
        "grades": [
            {"grade": "A", "min": 81, "max": 100, "points": 1, "description": "Excellent"},
            {"grade": "B", "min": 61, "max": 80, "points": 2, "description": "Very Good"},
            {"grade": "C", "min": 41, "max": 60, "points": 3, "description": "Good"},
            {"grade": "D", "min": 21, "max": 40, "points": 4, "description": "Satisfactory"},
            {"grade": "F", "min": 0, "max": 20, "points": 5, "description": "Fail"}
        ],
        "division_thresholds": {
            "I": 17,    # Points 12-17
            "II": 21,   # Points 18-21
            "III": 25,  # Points 22-25
            "IV": 35    # Points 26-35
        }
    },
    
    "nacte": {
        "name": "NACTE (Technical)",
        "grades": [
            {"grade": "A", "min": 75, "max": 100, "points": 4.0, "description": "Excellent"},
            {"grade": "B+", "min": 70, "max": 74, "points": 3.5, "description": "Very Good"},
            {"grade": "B", "min": 65, "max": 69, "points": 3.0, "description": "Good"},
            {"grade": "C", "min": 60, "max": 64, "points": 2.5, "description": "Above Average"},
            {"grade": "D", "min": 50, "max": 59, "points": 2.0, "description": "Average"},
            {"grade": "F", "min": 0, "max": 49, "points": 0.0, "description": "Fail"}
        ]
    },
    
    "plse": {
        "name": "PLSE (Primary)",
        "grades": [
            {"grade": "A", "min": 80, "max": 100, "points": 1, "description": "Excellent"},
            {"grade": "B", "min": 60, "max": 79, "points": 2, "description": "Very Good"},
            {"grade": "C", "min": 40, "max": 59, "points": 3, "description": "Good"},
            {"grade": "D", "min": 20, "max": 39, "points": 4, "description": "Satisfactory"},
            {"grade": "E", "min": 0, "max": 19, "points": 5, "description": "Weak"}
        ]
    }
}


def get_grade_for_marks(system, marks):
    """Get grade for given marks in a system"""
    if system not in GRADING_SYSTEMS:
        system = "csee"
    
    marks = float(marks)
    
    for grade_info in GRADING_SYSTEMS[system]["grades"]:
        if grade_info["min"] <= marks <= grade_info["max"]:
            return grade_info
    
    # Default to lowest grade
    return GRADING_SYSTEMS[system]["grades"][-1]


def calculate_division(total_points, system="csee"):
    """Calculate division for CSEE system"""
    if system != "csee":
        return None
    
    thresholds = GRADING_SYSTEMS[system]["division_thresholds"]
    
    if total_points <= thresholds["I"]:
        return "I"
    elif total_points <= thresholds["II"]:
        return "II"
    elif total_points <= thresholds["III"]:
        return "III"
    else:
        return "IV"