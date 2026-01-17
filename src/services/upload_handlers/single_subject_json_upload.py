# services/upload_handlers/single_subject_json_upload.py
"""
SINGLE SUBJECT JSON UPLOAD HANDLER - TANZANIA NECTA SYSTEM
Process JSON data with marks for ONE subject only
Same logic as Excel upload but accepts JSON input
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from ..calculations.grade_calculator import GradeCalculator

class SingleSubjectJSONUploadHandler:
    """
    Handle JSON data with ONE subject marks - Tanzania NECTA
    
    Expected JSON structure:
    [
        {
            "admission_no": "ADM001",
            "student_id": "STU001",
            "full_name": "JOHN MWAMBA",
            "gender": "M",
            "class": "FORM 4",
            "stream": "EAST",
            "marks": 85,
            "remarks": "Excellent"
        }
    ]
    """
    
    def __init__(self, subject_name: str, max_score: int = 100, grading_rules: str = 'CSEE'):
        self.subject_name = subject_name
        self.max_score = max_score
        self.grading_rules = grading_rules  # 'CSEE' or 'PSLE'
        self.calculator = GradeCalculator(grading_rules)
        
        # Expected fields in JSON
        self.expected_fields = [
            'admission_no', 'student_id', 'full_name', 'gender',
            'class', 'stream', 'marks', 'remarks'
        ]
    
    def process_json(self, json_data: List[Dict]) -> Dict:
        """
        Process JSON data with subject marks
        
        Args:
            json_data: List of student dictionaries with marks
            
        Returns:
            Dictionary with processed data
        """
        try:
            # 1. Validate JSON structure
            validation = self._validate_json_structure(json_data)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid JSON structure',
                    'details': validation['errors']
                }
            
            # 2. Extract and clean data (JSON is already in dict format)
            cleaned_data = self._extract_json_data(json_data)
            
            # 3. Calculate grades (Tanzania NECTA system)
            processed_data = self._calculate_grades(cleaned_data)
            
            # 4. Calculate ranks
            processed_data = self._calculate_ranks(processed_data)
            
            # 5. Generate subject analysis with GENDER breakdown
            analysis = self._generate_subject_analysis(processed_data)
            
            # 6. Return processed data
            return {
                'success': True,
                'subject': self.subject_name,
                'max_score': self.max_score,
                'grading_rules': self.grading_rules,
                'students_processed': len(processed_data),
                'subject_analysis': analysis,
                'student_data': processed_data,
                'validation_stats': {
                    'valid_rows': len(processed_data),
                    'invalid_rows': validation['invalid_count']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'JSON processing failed: {str(e)}',
                'subject': self.subject_name
            }
    
    def _validate_json_structure(self, json_data: List[Dict]) -> Dict:
        """Validate JSON data structure"""
        errors = []
        valid_count = 0
        invalid_count = 0
        
        if not isinstance(json_data, list):
            return {'valid': False, 'errors': ['JSON data must be a list'], 'invalid_count': 0}
        
        # Check for required fields
        required_fields = ['admission_no', 'student_id', 'full_name', 'gender', 'marks']
        
        for idx, student in enumerate(json_data):
            row_num = idx + 1
            
            # Check if it's a dictionary
            if not isinstance(student, dict):
                errors.append(f'Row {row_num}: Not a valid dictionary')
                invalid_count += 1
                continue
            
            # Check required fields
            missing_fields = [field for field in required_fields if field not in student]
            if missing_fields:
                errors.append(f'Row {row_num}: Missing fields: {", ".join(missing_fields)}')
                invalid_count += 1
                continue
            
            # Check admission_no and student_id
            if not student['admission_no'] or not student['student_id']:
                errors.append(f'Row {row_num}: Missing admission_no or student_id')
                invalid_count += 1
                continue
            
            # Validate gender
            gender = str(student.get('gender', '')).strip().lower()
            if gender not in ['m', 'f', 'male', 'female']:
                errors.append(f'Row {row_num}: Invalid gender: {student.get("gender")}')
                invalid_count += 1
                continue
            
            # Validate marks
            marks = student.get('marks')
            if marks is not None:
                try:
                    marks_float = float(marks)
                    if not (0 <= marks_float <= self.max_score):
                        errors.append(f'Row {row_num}: Marks {marks} out of range (0-{self.max_score})')
                        invalid_count += 1
                        continue
                except (ValueError, TypeError):
                    errors.append(f'Row {row_num}: Invalid marks: {marks}')
                    invalid_count += 1
                    continue
            
            valid_count += 1
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'valid_count': valid_count,
            'invalid_count': invalid_count
        }
    
    def _extract_json_data(self, json_data: List[Dict]) -> List[Dict]:
        """Extract and clean data from JSON"""
        cleaned_data = []
        
        for student in json_data:
            # Normalize gender
            gender = None
            if 'gender' in student and student['gender']:
                gender_str = str(student['gender']).strip().lower()
                if gender_str in ['m', 'male']:
                    gender = 'M'
                elif gender_str in ['f', 'female']:
                    gender = 'F'
            
            # Normalize marks
            marks = student.get('marks')
            if marks is not None:
                try:
                    marks = float(marks)
                except (ValueError, TypeError):
                    marks = None
            
            cleaned_student = {
                'admission_no': str(student.get('admission_no', '')).strip(),
                'student_id': str(student.get('student_id', '')).strip(),
                'full_name': str(student.get('full_name', '')).strip(),
                'gender': gender,
                'class': str(student.get('class', '')).strip(),
                'stream': str(student.get('stream', '')).strip(),
                'marks': marks,
                'remarks': str(student.get('remarks', '')).strip()
            }
            
            cleaned_data.append(cleaned_student)
        
        return cleaned_data
    
    def _calculate_grades(self, student_data: List[Dict]) -> List[Dict]:
        """Calculate grades using Tanzania NECTA system"""
        for student in student_data:
            if student['marks'] is not None:
                # Tanzania NECTA system
                grade_info = self.calculator.calculate_grade(student['marks'])
                student['grade'] = grade_info['grade']
                student['grade_remarks'] = grade_info['remarks']
            else:
                student['grade'] = 'ABSENT'
                student['grade_remarks'] = 'Hakushiriki'
        
        return student_data
    
    def _calculate_ranks(self, student_data: List[Dict]) -> List[Dict]:
        """Calculate subject rank for each student"""
        # Filter students with valid marks
        ranked_students = [
            s for s in student_data 
            if s['marks'] is not None and s['grade'] != 'ABSENT'
        ]
        
        # Sort by marks descending (highest first)
        ranked_students.sort(key=lambda x: x['marks'], reverse=True)
        
        # Assign ranks with tie handling
        current_rank = 1
        prev_mark = None
        skip = 0
        
        for student in ranked_students:
            if prev_mark is not None and student['marks'] < prev_mark:
                current_rank += 1 + skip
                skip = 0
            elif prev_mark is not None and student['marks'] == prev_mark:
                skip += 1
            
            student['subject_rank'] = current_rank
            prev_mark = student['marks']
        
        # Update original data
        rank_map = {s['student_id']: s['subject_rank'] for s in ranked_students}
        for student in student_data:
            student['subject_rank'] = rank_map.get(student['student_id'])
        
        return student_data
    
    def _generate_subject_analysis(self, student_data: List[Dict]) -> Dict:
        """
        Generate TAHINI analysis for the subject with GENDER breakdown
        """
        # Filter students with marks
        students_with_marks = [s for s in student_data if s['marks'] is not None]
        marks = [s['marks'] for s in students_with_marks]
        
        # Basic statistics
        total_students = len(student_data)
        present_students = len(students_with_marks)
        absent_students = total_students - present_students
        
        # Gender counts
        male_students = [s for s in student_data if s.get('gender') == 'M']
        female_students = [s for s in student_data if s.get('gender') == 'F']
        unknown_gender = total_students - len(male_students) - len(female_students)
        
        # Grade distribution with GENDER breakdown
        grade_distribution = {}
        for grade in ['A', 'B', 'C', 'D', 'E', 'ABSENT']:
            grade_students = [s for s in student_data if s['grade'] == grade]
            male_in_grade = [s for s in grade_students if s.get('gender') == 'M']
            female_in_grade = [s for s in grade_students if s.get('gender') == 'F']
            
            if grade_students:
                grade_distribution[grade] = {
                    'total': len(grade_students),
                    'percentage': round((len(grade_students) / total_students) * 100, 1),
                    'male': len(male_in_grade),
                    'female': len(female_in_grade)
                }
        
        # Calculate pass rate (A, B, C, D are passes in TZ)
        passing_grades = ['A', 'B', 'C', 'D']
        passed_students = [s for s in student_data if s['grade'] in passing_grades]
        
        # Performance summary with GENDER breakdown
        performance = {
            'total_students': total_students,
            'present_students': present_students,
            'absent_students': absent_students,
            'subject_average': round(np.mean(marks), 2) if marks else 0,
            'subject_highest': max(marks) if marks else 0,
            'subject_lowest': min(marks) if marks else 0,
            'pass_rate': round((len(passed_students) / total_students) * 100, 1) if total_students > 0 else 0,
            'gender_breakdown': {
                'male': {
                    'total': len(male_students),
                    'percentage': round((len(male_students) / total_students) * 100, 1) if total_students > 0 else 0,
                    'passed': len([s for s in male_students if s['grade'] in passing_grades])
                },
                'female': {
                    'total': len(female_students),
                    'percentage': round((len(female_students) / total_students) * 100, 1) if total_students > 0 else 0,
                    'passed': len([s for s in female_students if s['grade'] in passing_grades])
                },
                'unknown': unknown_gender
            },
            'grade_distribution': grade_distribution
        }
        
        # Generate summary notes
        notes = [
            f"Jumla ya wanafunzi: {total_students}",
            f"Wanafunzi walioshiriki: {present_students}",
            f"Wanafunzi wasioshiriki: {absent_students}",
            f"Wastani wa somo: {performance['subject_average']}%",
            f"Asilimia ya kufaulu: {performance['pass_rate']}%",
            f"Wavulana: {performance['gender_breakdown']['male']['total']} ({performance['gender_breakdown']['male']['percentage']}%)",
            f"Wasichana: {performance['gender_breakdown']['female']['total']} ({performance['gender_breakdown']['female']['percentage']}%)"
        ]
        
        # Add gender performance notes
        if performance['gender_breakdown']['male']['total'] > 0:
            male_pass_rate = round((performance['gender_breakdown']['male']['passed'] / performance['gender_breakdown']['male']['total']) * 100, 1)
            notes.append(f"Kiwango cha kufaulu kwa wavulana: {male_pass_rate}%")
        
        if performance['gender_breakdown']['female']['total'] > 0:
            female_pass_rate = round((performance['gender_breakdown']['female']['passed'] / performance['gender_breakdown']['female']['total']) * 100, 1)
            notes.append(f"Kiwango cha kufaulu kwa wasichana: {female_pass_rate}%")
        
        return {
            'subject_name': self.subject_name,
            'grading_rules': self.grading_rules,
            'performance_summary': performance,
            'summary_notes': notes
        }
    
    def get_expected_structure(self) -> Dict:
        """Get expected JSON structure"""
        return {
            'subject': self.subject_name,
            'max_score': self.max_score,
            'grading_rules': self.grading_rules,
            'expected_fields': self.expected_fields,
            'sample_data': [
                {
                    'admission_no': 'ADM001',
                    'student_id': 'STU001',
                    'full_name': 'JOHN MWAMBA',
                    'gender': 'M',
                    'class': 'FORM 4',
                    'stream': 'EAST',
                    'marks': 85,
                    'remarks': 'Excellent'
                },
                {
                    'admission_no': 'ADM002',
                    'student_id': 'STU002',
                    'full_name': 'SARAH JUMANNE',
                    'gender': 'F',
                    'class': 'FORM 4',
                    'stream': 'EAST',
                    'marks': 78,
                    'remarks': 'Very Good'
                }
            ],
            'validation_rules': {
                'marks_range': f'0-{self.max_score}',
                'gender_values': 'M/male, F/female',
                'required_fields': ['admission_no', 'student_id', 'full_name', 'gender', 'marks']
            }
        }