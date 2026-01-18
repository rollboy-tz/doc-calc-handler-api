# services/grading/result_builder.py
"""
RESULT BUILDER - SIMPLE
"""

class ResultBuilder:
    """Build results for database"""
    
    @staticmethod
    def format_for_database(results):
        """Format results"""
        if not results.get("success"):
            return results
        
        formatted = {
            "exam_id": results["metadata"]["exam_id"],
            "class_id": results["metadata"]["class_id"],
            "rule": results["metadata"]["rule"],
            "processed": results["metadata"]["processed"],
            "students": []
        }
        
        for student in results["students"]:
            student_entry = {
                "id": student["student"]["id"],
                "admission": student["student"]["admission"],
                "name": student["student"]["name"],
                "gender": student["student"]["gender"],
                "summary": student["summary"],
                "subjects": []
            }
            
            for subject_name, subject_data in student["subjects"].items():
                student_entry["subjects"].append({
                    "name": subject_name,
                    "marks": subject_data["marks"],
                    "grade": subject_data["grade"],
                    "pass": subject_data.get("pass", False)
                })
            
            formatted["students"].append(student_entry)
        
        return formatted