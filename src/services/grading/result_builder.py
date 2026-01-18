# services/grading/result_builder.py
"""
RESULT BUILDER - CLEAN VARIABLES
"""

class ResultBuilder:
    
    @staticmethod
    def format_for_database(results):
        """Format results - clean variables"""
        if not results.get("success"):
            return results
        
        formatted = {
            "exam_id": results["metadata"]["exam_id"],
            "class_id": results["metadata"]["class_id"],
            "rule": results["metadata"]["grading_rule"],
            "processed": results["metadata"]["processing_time"],
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
                subject_entry = {
                    "name": subject_name,
                    "marks": subject_data["marks"],
                    "grade": subject_data["grade"],
                    "points": subject_data.get("points"),
                    "pass": subject_data.get("pass", False)
                }
                
                student_entry["subjects"].append(subject_entry)
            
            formatted["students"].append(student_entry)
        
        return formatted