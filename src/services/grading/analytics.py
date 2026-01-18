# services/grading/analytics.py
"""
ANALYTICS AND STATISTICS CALCULATIONS
"""
import datetime


class ResultAnalytics:
    """Calculate ranks and statistics"""
    
    @staticmethod
    def calculate_ranks(students_data):
        """Calculate class ranks based on average marks"""
        # Sort by average marks (descending)
        sorted_students = sorted(
            students_data,
            key=lambda x: x['summary']['average_marks'],
            reverse=True
        )
        
        # Assign ranks with tie handling
        current_rank = 1
        previous_avg = None
        skip_count = 0
        
        for i, student in enumerate(sorted_students):
            current_avg = student['summary']['average_marks']
            
            if previous_avg is not None and abs(current_avg - previous_avg) < 0.01:
                student['summary']['class_rank'] = current_rank
                skip_count += 1
            else:
                current_rank = i + 1 - skip_count
                student['summary']['class_rank'] = current_rank
            
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
            all_marks = []
            attended_count = 0
            grade_counts = {}
            gender_marks = {"M": [], "F": [], "Unknown": []}
            gender_attendance = {"M": 0, "F": 0, "Unknown": 0}
            
            for student in students_data:
                gender = student['student_info'].get('gender', 'Unknown').upper()
                
                if subject in student['subjects']:
                    subj_data = student['subjects'][subject]
                    
                    if subj_data.get('marks') is not None:
                        marks = subj_data['marks']
                        grade = subj_data['grade']
                        
                        # Collect data
                        all_marks.append(marks)
                        attended_count += 1
                        
                        # Count grades
                        grade_counts[grade] = grade_counts.get(grade, 0) + 1
                        
                        # Gender data
                        gender_marks[gender].append(marks)
                        gender_attendance[gender] += 1
            
            total_students = len(students_data)
            absent_count = total_students - attended_count
            
            # Build analysis
            analysis = {
                "attendance": {
                    "total": total_students,
                    "attended": attended_count,
                    "absent": absent_count,
                    "rate": round((attended_count / total_students) * 100, 2) if total_students > 0 else 0
                }
            }
            
            # Add subject ID if available
            subject_id = None
            if external_ids and 'subject_ids' in external_ids:
                subject_id = external_ids['subject_ids'].get(subject.lower())
            
            if subject_id:
                analysis["subject_id"] = subject_id
            
            if all_marks:
                # Performance metrics
                analysis["performance"] = {
                    "average": round(sum(all_marks) / len(all_marks), 2),
                    "highest": max(all_marks),
                    "lowest": min(all_marks),
                    "median": sorted(all_marks)[len(all_marks) // 2] if all_marks else 0,
                    "pass_rate": round(
                        (sum(1 for s in students_data 
                            if subject in s['subjects'] and s['subjects'][subject].get('is_pass', False)) / attended_count) * 100, 2
                    ) if attended_count > 0 else 0
                }
                
                # Grade distribution
                analysis["grade_distribution"] = {
                    "counts": grade_counts,
                    "percentages": {g: round((c / total_students) * 100, 2) for g, c in grade_counts.items()}
                }
                
                # Gender analysis
                gender_avgs = {}
                for gender, marks_list in gender_marks.items():
                    if marks_list:
                        gender_avgs[gender] = round(sum(marks_list) / len(marks_list), 2)
                
                analysis["gender_analysis"] = {
                    "averages": gender_avgs,
                    "counts": gender_attendance
                }
            
            subject_analysis[subject] = analysis
        
        return subject_analysis
    
    @staticmethod
    def calculate_class_analysis(students_data, subject_columns, external_ids=None):
        """Calculate class-level analytics"""
        external_ids = external_ids or {}
        total_students = len(students_data)
        
        if total_students == 0:
            return {}
        
        # Collect data
        all_averages = []
        gender_data = {"M": [], "F": [], "Unknown": []}
        overall_grades = []
        
        for student in students_data:
            avg = student['summary']['average_marks']
            grade = student['summary']['overall_grade']
            gender = student['student_info'].get('gender', 'Unknown').upper()
            
            all_averages.append(avg)
            overall_grades.append(grade)
            gender_data[gender].append(avg)
        
        # Grade distribution
        grade_counts = {}
        for grade in overall_grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Gender performance
        gender_performance = {}
        for gender, marks_list in gender_data.items():
            if marks_list:
                gender_performance[gender] = {
                    "average": round(sum(marks_list) / len(marks_list), 2),
                    "count": len(marks_list),
                    "percentage": round((len(marks_list) / total_students) * 100, 2)
                }
        
        # Build analysis
        analysis = {
            "overview": {
                "total_students": total_students,
                "subjects_count": len(subject_columns),
                "class_average": round(sum(all_averages) / total_students, 2),
                "performance_range": {
                    "highest": max(all_averages) if all_averages else 0,
                    "lowest": min(all_averages) if all_averages else 0
                }
            },
            "grade_distribution": {
                "counts": grade_counts,
                "percentages": {g: round((c / total_students) * 100, 2) for g, c in grade_counts.items()}
            },
            "gender_performance": gender_performance,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add IDs if available
        if external_ids:
            analysis["exam_id"] = external_ids.get("exam_id")
            analysis["class_id"] = external_ids.get("class_id")
        
        return analysis