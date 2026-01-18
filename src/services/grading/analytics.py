# services/grading/analytics.py
"""
ANALYTICS - CLEAN VARIABLES
"""

class ResultAnalytics:
    
    @staticmethod
    def calculate_subject_analysis(students_data, subject_columns, external_ids=None):
        subject_analysis = {}
        
        for subject in subject_columns:
            # Clean counters
            marks = []
            attended = 0
            grades = {}
            
            for student in students_data:
                if subject in student["subjects"]:
                    subj = student["subjects"][subject]
                    
                    if subj.get("attended") and subj.get("marks") is not None:
                        marks.append(subj["marks"])
                        attended += 1
                        grade = subj["grade"]
                        grades[grade] = grades.get(grade, 0) + 1
            
            total = len(students_data)
            analysis = {
                "attendance": {
                    "total": total,
                    "attended": attended,
                    "rate": round((attended / total) * 100, 2) if total > 0 else 0
                }
            }
            
            if marks:
                analysis["performance"] = {
                    "average": round(sum(marks) / len(marks), 2),
                    "high": max(marks),
                    "low": min(marks),
                    "pass_rate": round(
                        (sum(1 for s in students_data 
                            if subject in s["subjects"] and s["subjects"][subject].get("pass", False)) / attended) * 100, 2
                    ) if attended > 0 else 0
                }
                
                analysis["grades"] = {
                    "counts": grades,
                    "percentages": {g: round((c / total) * 100, 2) for g, c in grades.items()}
                }
            
            subject_analysis[subject] = analysis
        
        return subject_analysis
    
    @staticmethod
    def calculate_class_analysis(students_data, subject_columns, external_ids=None):
        total = len(students_data)
        
        if total == 0:
            return {}
        
        # Clean data collection
        averages = []
        grades = []
        divisions = {}
        
        for student in students_data:
            avg = student["summary"]["average"]
            grade = student["summary"]["grade"]
            division = student["summary"].get("division")
            
            averages.append(avg)
            grades.append(grade)
            
            if division:
                divisions[division] = divisions.get(division, 0) + 1
        
        # Clean analysis
        analysis = {
            "overview": {
                "students": total,
                "subjects": len(subject_columns),
                "average": round(sum(averages) / total, 2),
                "range": {
                    "high": max(averages),
                    "low": min(averages)
                }
            },
            "grades": {
                "counts": {g: grades.count(g) for g in set(grades)},
                "percentages": {g: round((grades.count(g) / total) * 100, 2) for g in set(grades)}
            }
        }
        
        # Add divisions if CSEE
        if divisions:
            analysis["divisions"] = {
                "counts": divisions,
                "percentages": {d: round((c / total) * 100, 2) for d, c in divisions.items()}
            }
        
        return analysis