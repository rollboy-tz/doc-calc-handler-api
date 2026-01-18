# services/grading/grading_rules.py
"""
GRADING RULES - CLEAN VARIABLES
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
        ]
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