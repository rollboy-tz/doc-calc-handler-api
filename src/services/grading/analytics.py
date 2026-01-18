# services/grading/analytics.py
"""
ANALYTICS - FIXED WITH ALL REQUIRED METHODS
"""
import datetime


class ResultAnalytics:
    """Calculate ranks and statistics"""
    
    @staticmethod
    def calculate_ranks(students_data):
        """Calculate class ranks based on average marks"""
        # Sort by average (descending)
        sorted_students = sorted(
            students_data,
            key=lambda x: x['summary']['average'],
            reverse=True
        )
        
        # Assign ranks with tie handling
        current_rank = 1
        previous_avg = None
        skip_count = 0
        
        for i, student in enumerate(sorted_students):
            current_avg = student['summary']['average']
            
            if previous_avg is not None and abs(current_avg - previous_avg) < 0.01:
                student['summary']['rank'] = current_rank
                skip_count += 1
            else:
                current_rank = i + 1 - skip_count
                student['summary']['rank'] = current_rank
            
            previous_avg = current_avg
        
        return sorted_students
    
    @staticmethod
    def calculate_subject_ranks(students_data, subject_columns):
        """Calculate ranks per subject"""
        for subject in subject_columns:
            # Get students who attended this subject
            attended = []
            for idx, student in enumerate(students_data):
                if subject in student['subjects'] and student['subjects'][subject].get('marks') is not None:
                    attended.append((idx, student))
            
            # Sort by marks
            attended.sort(key=lambda x: x[1]['subjects'][subject]['marks'], reverse=True)
            
            # Assign ranks
            current_rank = 1
            previous_marks = None
            skip_count = 0
            
            for i, (orig_idx, student) in enumerate(attended):
                current_marks = student['subjects'][subject]['marks']
                
                if previous_marks is not None and abs(current_marks - previous_marks) < 0.01:
                    students_data[orig_idx]['subjects'][subject]['subject_rank'] = current_rank
                    skip_count += 1
                else:
                    current_rank = i + 1 - skip_count
                    students_data[orig_idx]['subjects'][subject]['subject_rank'] = current_rank
                
                previous_marks = current_marks
        
        return students_data
    
    @staticmethod
    def calculate_subject_analysis(students_data, subject_columns, external_ids=None):
        """Calculate subject-level analytics"""
        external_ids = external_ids or {}
        subject_analysis = {}
        
        for subject in subject_columns:
            # Initialize counters
            marks = []
            attended = 0
            grades = {}
            gender_marks = {"M": [], "F": [], "Unknown": []}
            
            for student in students_data:
                gender = student['student'].get('gender', 'Unknown').upper()
                
                if subject in student['subjects']:
                    subj = student['subjects'][subject]
                    
                    if subj.get('attended') and subj.get('marks') is not None:
                        mark = subj['marks']
                        grade = subj['grade']
                        
                        marks.append(mark)
                        attended += 1
                        grades[grade] = grades.get(grade, 0) + 1
                        gender_marks[gender].append(mark)
            
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
                            if subject in s['subjects'] and s['subjects'][subject].get('pass', False)) / attended) * 100, 2
                    ) if attended > 0 else 0
                }
                
                analysis["grades"] = {
                    "counts": grades,
                    "percentages": {g: round((c / total) * 100, 2) for g, c in grades.items()}
                }
                
                # Gender analysis
                gender_avgs = {}
                for gender, marks_list in gender_marks.items():
                    if marks_list:
                        gender_avgs[gender] = round(sum(marks_list) / len(marks_list), 2)
                
                analysis["gender"] = {
                    "averages": gender_avgs,
                    "counts": {g: len(m) for g, m in gender_marks.items() if m}
                }
            
            subject_analysis[subject] = analysis
        
        return subject_analysis
    
    @staticmethod
    def calculate_class_analysis(students_data, subject_columns, external_ids=None):
        """Calculate class-level analytics"""
        external_ids = external_ids or {}
        total = len(students_data)
        
        if total == 0:
            return {}
        
        # Collect data
        averages = []
        grades = []
        divisions = {}
        gender_data = {"M": [], "F": [], "Unknown": []}
        
        for student in students_data:
            avg = student['summary']['average']
            grade = student['summary']['grade']
            division = student['summary'].get('division')
            gender = student['student'].get('gender', 'Unknown').upper()
            
            averages.append(avg)
            grades.append(grade)
            gender_data[gender].append(avg)
            
            if division:
                divisions[division] = divisions.get(division, 0) + 1
        
        # Build analysis
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
        
        # Gender analysis
        gender_performance = {}
        for gender, marks_list in gender_data.items():
            if marks_list:
                gender_performance[gender] = {
                    "average": round(sum(marks_list) / len(marks_list), 2),
                    "count": len(marks_list),
                    "percentage": round((len(marks_list) / total) * 100, 2)
                }
        
        analysis["gender"] = gender_performance
        
        # Division analysis
        if divisions:
            analysis["divisions"] = {
                "counts": divisions,
                "percentages": {d: round((c / total) * 100, 2) for d, c in divisions.items()}
            }
        
        # Add IDs if available
        if external_ids:
            analysis["exam_id"] = external_ids.get("exam_id")
            analysis["class_id"] = external_ids.get("class_id")
        
        return analysis