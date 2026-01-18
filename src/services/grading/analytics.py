# services/grading/analytics.py
"""
ANALYTICS - WHOLE NUMBERS ONLY
"""
import datetime


class ResultAnalytics:
    """Calculate analytics - whole numbers only"""
    
    @staticmethod
    def calculate_ranks(students_data):
        """Calculate ranks"""
        sorted_students = sorted(
            students_data,
            key=lambda x: x['summary']['average'],
            reverse=True
        )
        
        current_rank = 1
        previous_avg = None
        skip_count = 0
        
        for i, student in enumerate(sorted_students):
            current_avg = student['summary']['average']
            
            if previous_avg is not None and current_avg == previous_avg:
                student['summary']['rank'] = current_rank
                skip_count += 1
            else:
                current_rank = i + 1 - skip_count
                student['summary']['rank'] = current_rank
            
            previous_avg = current_avg
        
        return sorted_students
    
    @staticmethod
    def calculate_subject_ranks(students_data, subject_columns):
        """Calculate subject ranks"""
        for subject in subject_columns:
            # Get students with marks
            attended = []
            for idx, student in enumerate(students_data):
                if subject in student["subjects"] and student["subjects"][subject].get("marks") is not None:
                    attended.append((idx, student))
            
            # Sort by marks
            attended.sort(key=lambda x: x[1]["subjects"][subject]["marks"], reverse=True)
            
            # Assign ranks
            current_rank = 1
            previous_marks = None
            skip_count = 0
            
            for i, (orig_idx, student) in enumerate(attended):
                current_marks = student["subjects"][subject]["marks"]
                
                if previous_marks is not None and current_marks == previous_marks:
                    students_data[orig_idx]["subjects"][subject]["subject_rank"] = current_rank
                    skip_count += 1
                else:
                    current_rank = i + 1 - skip_count
                    students_data[orig_idx]["subjects"][subject]["subject_rank"] = current_rank
                
                previous_marks = current_marks
        
        return students_data
    
    @staticmethod
    def calculate_subject_analysis(students_data, subject_columns, external_ids=None):
        """Calculate subject analytics"""
        subject_analysis = {}
        
        for subject in subject_columns:
            # Collect data
            marks = []
            attended = 0
            grades = {}
            
            for student in students_data:
                if subject in student["subjects"]:
                    subj = student["subjects"][subject]
                    
                    if subj.get("attended") and subj.get("marks") is not None:
                        mark = subj["marks"]
                        grade = subj["grade"]
                        
                        marks.append(mark)
                        attended += 1
                        grades[grade] = grades.get(grade, 0) + 1
            
            total = len(students_data)
            analysis = {
                "attendance": {
                    "total": total,
                    "attended": attended,
                    "rate": int((attended / total) * 100) if total > 0 else 0
                }
            }
            
            if marks:
                analysis["performance"] = {
                    "average": int(sum(marks) / len(marks)),
                    "high": max(marks),
                    "low": min(marks),
                    "pass_rate": int((sum(1 for s in students_data 
                                        if subject in s["subjects"] and s["subjects"][subject].get("pass", False)) / attended) * 100) if attended > 0 else 0
                }
                
                analysis["grades"] = {
                    "counts": grades,
                    "percentages": {g: int((c / total) * 100) for g, c in grades.items()}
                }
            
            subject_analysis[subject] = analysis
        
        return subject_analysis
    
    @staticmethod
    def calculate_class_analysis(students_data, subject_columns, external_ids=None):
        """Calculate class analytics"""
        total = len(students_data)
        
        if total == 0:
            return {}
        
        # Collect data
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
        
        # Build analysis
        analysis = {
            "overview": {
                "students": total,
                "subjects": len(subject_columns),
                "average": int(sum(averages) / total),
                "range": {
                    "high": max(averages),
                    "low": min(averages)
                }
            },
            "grades": {
                "counts": {g: grades.count(g) for g in set(grades)},
                "percentages": {g: int((grades.count(g) / total) * 100) for g in set(grades)}
            }
        }
        
        # Add divisions
        if divisions:
            analysis["divisions"] = {
                "counts": divisions,
                "percentages": {d: int((c / total) * 100) for d, c in divisions.items()}
            }
        
        return analysis