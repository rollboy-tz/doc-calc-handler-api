# services/grading/result_builder.py
"""
RESULT FORMATTING AND FINAL OUTPUT BUILDER
"""
import json


class ResultBuilder:
    """Format and structure final results"""
    
    @staticmethod
    def format_for_database(results):
        """Format results for database storage"""
        if not results.get("success"):
            return results
        
        formatted = {
            "exam_id": results["metadata"]["exam_id"],
            "class_id": results["metadata"]["class_id"],
            "grading_rule": results["metadata"]["grading_rule"],
            "processed_at": results["metadata"]["processing_time"],
            "total_students": results["metadata"]["students_count"],
            "total_subjects": results["metadata"]["subjects_count"],
            "students_data": []
        }
        
        for student in results["students"]:
            student_entry = {
                "student_id": student["student_info"]["student_id"],
                "admission_no": student["student_info"]["admission_no"],
                "full_name": student["student_info"]["full_name"],
                "gender": student["student_info"]["gender"],
                "summary": student["summary"],
                "subjects": []
            }
            
            for subject_name, subject_data in student["subjects"].items():
                subject_entry = {
                    "subject_name": subject_name,
                    "marks": subject_data["marks"],
                    "grade": subject_data["grade"],
                    "points": subject_data.get("points"),
                    "is_pass": subject_data.get("is_pass", False)
                }
                
                # Add subject ID if available
                if "subject_ids" in results["metadata"]:
                    subject_id = results["metadata"]["subject_ids"].get(subject_name.lower())
                    if subject_id:
                        subject_entry["subject_id"] = subject_id
                
                student_entry["subjects"].append(subject_entry)
            
            formatted["students_data"].append(student_entry)
        
        return formatted
    
    @staticmethod
    def create_summary_report(results):
        """Create a summary report"""
        if not results.get("success"):
            return {"error": "Results processing failed"}
        
        analytics = results.get("analytics", {})
        class_level = analytics.get("class_level", {})
        
        return {
            "exam_summary": {
                "exam_id": results["metadata"]["exam_id"],
                "class_id": results["metadata"]["class_id"],
                "total_students": results["metadata"]["students_count"],
                "class_average": class_level.get("overview", {}).get("class_average", 0),
                "processing_date": results["metadata"]["processing_time"]
            },
            "performance_summary": {
                "grade_distribution": class_level.get("grade_distribution", {}),
                "gender_performance": class_level.get("gender_performance", {}),
                "attendance_summary": {
                    "total_students": results["metadata"]["students_count"],
                    "subjects_count": results["metadata"]["subjects_count"]
                }
            }
        }