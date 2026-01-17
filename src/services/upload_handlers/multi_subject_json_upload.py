# services/upload_handlers/multi_subject_json_upload.py
"""
MULTI SUBJECT JSON UPLOAD HANDLER - TANZANIA NECTA SYSTEM  
Process JSON data with marks for MULTIPLE subjects
Returns clean data with gender analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from ..calculations.grade_calculator import GradeCalculator

class MultiSubjectJSONUploadHandler:
    """
    Handle JSON data with MULTIPLE subjects marks - Tanzania NECTA
    
    Expected JSON structure:
    [
        {
            "admission_no": "ADM001",
            "student_id": "STU001",
            "full_name": "JOHN MWAMBA",
            "gender": "M",
            "class": "FORM 4",
            "stream": "EAST",
            "subjects": {
                "MATHEMATICS": 95,
                "ENGLISH": 92,
                "KISWAHILI": 88,
                "SCIENCE": 90,
                "GEOGRAPHY": 85
            },
            "remarks": "Excellent student"
        }
    ]
    """
    
    def __init__(self, subjects: List[str], grading_rules: str = 'CSEE'):
        self.subjects = subjects
        self.grading_rules = grading_rules  # 'CSEE' or 'PSLE'
        self.calculator = GradeCalculator(grading_rules)
        
        # Base fields that should always be present
        self.base_fields = ['admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream', 'subjects']
    
    def process_json(self, json_data: List[Dict]) -> Dict:
        """
        Process JSON data with multiple subjects marks
        
        Args:
            json_data: List of student dictionaries with subjects marks
            
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
            
            # 2. Extract and clean data
            cleaned_data = self._extract_json_data(json_data)
            
            # 3. Calculate grades for all subjects (Tanzania NECTA)
            processed_data = self._calculate_all_grades(cleaned_data)
            
            # 4. Calculate student summaries and positions
            final_results = self._calculate_summaries(processed_data)
            
            # 5. Generate class-wide statistics with GENDER analysis
            class_summary = self._generate_class_summary(final_results)
            
            # 6. Return comprehensive data
            return {
                'success': True,
                'subjects_processed': self.subjects,
                'total_students': len(final_results),
                'grading_rules': self.grading_rules,
                'class_summary': class_summary,
                'student_records': final_results,
                'processing_stats': {
                    'valid_students': len([s for s in final_results if s['valid']]),
                    'invalid_students': len([s for s in final_results if not s['valid']]),
                    'subjects_found': len(self.subjects),
                    'subjects_with_data': self._count_subjects_with_data(final_results)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'JSON processing failed: {str(e)}',
                'subjects_expected': self.subjects
            }
    
    def _validate_json_structure(self, json_data: List[Dict]) -> Dict:
        """Validate JSON data structure"""
        errors = []
        
        if not isinstance(json_data, list):
            return {'valid': False, 'errors': ['JSON data must be a list'], 'invalid_count': 0}
        
        # Check for required fields
        required_fields = ['admission_no', 'student_id', 'full_name', 'gender', 'subjects']
        
        for idx, student in enumerate(json_data):
            row_num = idx + 1
            
            # Check if it's a dictionary
            if not isinstance(student, dict):
                errors.append(f'Row {row_num}: Not a valid dictionary')
                continue
            
            # Check required fields
            missing_fields = [field for field in required_fields if field not in student]
            if missing_fields:
                errors.append(f'Row {row_num}: Missing fields: {", ".join(missing_fields)}')
                continue
            
            # Check admission_no and student_id
            if not student['admission_no'] or not student['student_id']:
                errors.append(f'Row {row_num}: Missing admission_no or student_id')
                continue
            
            # Validate gender
            gender = str(student.get('gender', '')).strip().lower()
            if gender not in ['m', 'f', 'male', 'female']:
                errors.append(f'Row {row_num}: Invalid gender: {student.get("gender")}')
                continue
            
            # Validate subjects structure
            subjects = student.get('subjects')
            if not isinstance(subjects, dict):
                errors.append(f'Row {row_num}: Subjects must be a dictionary')
                continue
            
            # Validate marks for each subject
            for subject_name, mark in subjects.items():
                if mark is not None:
                    try:
                        mark_float = float(mark)
                        if not (0 <= mark_float <= 100):
                            errors.append(f'Row {row_num}: {subject_name} marks {mark} out of range (0-100)')
                    except (ValueError, TypeError):
                        errors.append(f'Row {row_num}: {subject_name} invalid marks: {mark}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors[:10],  # Limit to first 10 errors
            'total_errors': len(errors)
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
            
            record = {
                'admission_no': str(student.get('admission_no', '')).strip(),
                'student_id': str(student.get('student_id', '')).strip(),
                'full_name': str(student.get('full_name', '')).strip(),
                'gender': gender,
                'class': str(student.get('class', '')).strip(),
                'stream': str(student.get('stream', '')).strip(),
                'subjects': {},
                'remarks': str(student.get('remarks', '')).strip(),
                'valid': True,
                'errors': []
            }
            
            # Extract marks for each subject
            subjects_data = student.get('subjects', {})
            for subject_name in self.subjects:
                if subject_name in subjects_data:
                    mark = subjects_data[subject_name]
                    if mark is not None:
                        try:
                            record['subjects'][subject_name] = {
                                'mark': float(mark),
                                'grade': None,      # Will be calculated
                                'remarks': None     # Will be calculated
                            }
                        except (ValueError, TypeError):
                            record['subjects'][subject_name] = {'mark': None, 'error': 'Invalid format'}
                            record['valid'] = False
                            record['errors'].append(f'{subject_name}: Invalid marks format')
                    else:
                        record['subjects'][subject_name] = {'mark': None, 'status': 'ABSENT'}
                else:
                    record['subjects'][subject_name] = {'mark': None, 'status': 'NOT PROVIDED'}
            
            cleaned_data.append(record)
        
        return cleaned_data
    
    def _calculate_all_grades(self, records: List[Dict]) -> List[Dict]:
        """Calculate grades for all subjects using Tanzania NECTA system"""
        for record in records:
            for subject_name, data in record['subjects'].items():
                if data.get('mark') is not None:
                    grade_info = self.calculator.calculate_grade(data['mark'])
                    record['subjects'][subject_name]['grade'] = grade_info['grade']
                    record['subjects'][subject_name]['remarks'] = grade_info['remarks']
                    record['subjects'][subject_name]['grade_points'] = grade_info['points']  # TZ points (1-5)
        
        return records
    
    def _calculate_summaries(self, records: List[Dict]) -> List[Dict]:
        """Calculate student summaries (totals, averages, positions)"""
        for record in records:
            # Get all valid marks
            marks = []
            grades = []
            present_subjects = []
            
            for subject_name, data in record['subjects'].items():
                if data.get('mark') is not None:
                    marks.append(data['mark'])
                    grades.append(data.get('grade', ''))
                    present_subjects.append(subject_name)
            
            # Count passing grades (A, B, C, D are passes in TZ)
            passing_grades = ['A', 'B', 'C', 'D']
            passed_subjects = [grade for grade in grades if grade in passing_grades]
            
            if marks:
                record['summary'] = {
                    'total_marks': sum(marks),
                    'average_mark': round(sum(marks) / len(marks), 2),
                    'subjects_count': len(self.subjects),
                    'subjects_present': len(present_subjects),
                    'subjects_absent': len(self.subjects) - len(present_subjects),
                    'subjects_passed': len(passed_subjects),
                    'subjects_failed': len(present_subjects) - len(passed_subjects),
                    'pass_rate': round((len(passed_subjects) / len(present_subjects)) * 100, 1) if present_subjects else 0,
                    'grades': grades
                }
            else:
                record['summary'] = {
                    'total_marks': 0,
                    'average_mark': 0,
                    'subjects_count': len(self.subjects),
                    'subjects_present': 0,
                    'subjects_absent': len(self.subjects),
                    'subjects_passed': 0,
                    'subjects_failed': 0,
                    'pass_rate': 0,
                    'grades': []
                }
        
        # Calculate class positions based on total marks
        valid_records = [r for r in records if r['summary']['total_marks'] > 0]
        valid_records.sort(key=lambda x: x['summary']['total_marks'], reverse=True)
        
        # Assign positions with tie handling
        current_position = 1
        prev_total = None
        skip = 0
        
        for record in valid_records:
            if prev_total is not None and record['summary']['total_marks'] < prev_total:
                current_position += 1 + skip
                skip = 0
            elif prev_total is not None and record['summary']['total_marks'] == prev_total:
                skip += 1
            
            record['summary']['class_position'] = current_position
            prev_total = record['summary']['total_marks']
        
        # For records with no marks
        for record in records:
            if 'class_position' not in record['summary']:
                record['summary']['class_position'] = None
        
        return records
    
    def _generate_class_summary(self, records: List[Dict]) -> Dict:
        """Generate class-wide statistics with GENDER analysis"""
        # Gender breakdown
        male_students = [r for r in records if r.get('gender') == 'M']
        female_students = [r for r in records if r.get('gender') == 'F']
        unknown_gender = len(records) - len(male_students) - len(female_students)
        
        # Subject-wise statistics
        subject_stats = {}
        for subject_name in self.subjects:
            marks = []
            male_marks = []
            female_marks = []
            
            for record in records:
                if subject_name in record['subjects'] and record['subjects'][subject_name].get('mark') is not None:
                    mark = record['subjects'][subject_name]['mark']
                    marks.append(mark)
                    
                    # Separate by gender
                    if record.get('gender') == 'M':
                        male_marks.append(mark)
                    elif record.get('gender') == 'F':
                        female_marks.append(mark)
            
            if marks:
                # Grade distribution for this subject
                grades = []
                for record in records:
                    if subject_name in record['subjects']:
                        grade = record['subjects'][subject_name].get('grade', 'ABSENT')
                        grades.append(grade)
                
                grade_dist = {}
                for grade in ['A', 'B', 'C', 'D', 'E', 'ABSENT', 'NOT PROVIDED']:
                    count = grades.count(grade)
                    if count > 0:
                        grade_dist[grade] = count
                
                subject_stats[subject_name] = {
                    'average': round(np.mean(marks), 2),
                    'highest': max(marks) if marks else 0,
                    'lowest': min(marks) if marks else 0,
                    'students_with_marks': len(marks),
                    'students_absent': len(records) - len(marks),
                    'grade_distribution': grade_dist,
                    'gender_analysis': {
                        'male_average': round(np.mean(male_marks), 2) if male_marks else 0,
                        'female_average': round(np.mean(female_marks), 2) if female_marks else 0,
                        'male_count': len(male_marks),
                        'female_count': len(female_marks)
                    }
                }
        
        # Overall class statistics
        total_marks = [r['summary']['total_marks'] for r in records if r['summary']['total_marks'] > 0]
        male_totals = [r['summary']['total_marks'] for r in male_students if r['summary']['total_marks'] > 0]
        female_totals = [r['summary']['total_marks'] for r in female_students if r['summary']['total_marks'] > 0]
        
        # Pass rate by gender (students who passed at least one subject)
        male_passed = len([r for r in male_students if r['summary']['subjects_passed'] > 0])
        female_passed = len([r for r in female_students if r['summary']['subjects_passed'] > 0])
        
        return {
            'subject_statistics': subject_stats,
            'class_average': round(np.mean(total_marks), 2) if total_marks else 0,
            'class_highest_total': max(total_marks) if total_marks else 0,
            'class_lowest_total': min(total_marks) if total_marks else 0,
            'gender_breakdown': {
                'male': {
                    'total': len(male_students),
                    'percentage': round((len(male_students) / len(records)) * 100, 1) if records else 0,
                    'average_total': round(np.mean(male_totals), 2) if male_totals else 0,
                    'passed': male_passed,
                    'pass_rate': round((male_passed / len(male_students)) * 100, 1) if male_students else 0
                },
                'female': {
                    'total': len(female_students),
                    'percentage': round((len(female_students) / len(records)) * 100, 1) if records else 0,
                    'average_total': round(np.mean(female_totals), 2) if female_totals else 0,
                    'passed': female_passed,
                    'pass_rate': round((female_passed / len(female_students)) * 100, 1) if female_students else 0
                },
                'unknown': unknown_gender
            },
            'total_students': len(records),
            'students_with_complete_marks': len(total_marks),
            'grading_rules': self.grading_rules,
            'summary_notes': self._generate_summary_notes(records, subject_stats, male_students, female_students)
        }
    
    def _count_subjects_with_data(self, records: List[Dict]) -> Dict:
        """Count how many students provided data for each subject"""
        subject_counts = {}
        for subject_name in self.subjects:
            count = 0
            for record in records:
                if subject_name in record['subjects'] and record['subjects'][subject_name].get('mark') is not None:
                    count += 1
            subject_counts[subject_name] = count
        return subject_counts
    
    def _generate_summary_notes(self, records, subject_stats, male_students, female_students):
        """Generate summary notes in Swahili"""
        notes = [
            f"Jumla ya wanafunzi: {len(records)}",
            f"Wavulana: {len(male_students)}",
            f"Wasichana: {len(female_students)}"
        ]
        
        # Subject performance highlights
        if subject_stats:
            best_subject = max(subject_stats.items(), key=lambda x: x[1]['average'])[0]
            worst_subject = min(subject_stats.items(), key=lambda x: x[1]['average'])[0]
            
            notes.append(f"Somo bora: {best_subject} (wastani: {subject_stats[best_subject]['average']}%)")
            notes.append(f"Somo dhaifu: {worst_subject} (wastani: {subject_stats[worst_subject]['average']}%)")
        
        # Gender performance comparison
        if male_students and female_students:
            male_avg = np.mean([s['summary']['average_mark'] for s in male_students if s['summary']['average_mark'] > 0])
            female_avg = np.mean([s['summary']['average_mark'] for s in female_students if s['summary']['average_mark'] > 0])
            
            notes.append(f"Wastani wa wavulana: {round(male_avg, 1)}%")
            notes.append(f"Wastani wa wasichana: {round(female_avg, 1)}%")
        
        # Overall pass rate
        total_passed = len([r for r in records if r['summary']['subjects_passed'] > 0])
        overall_pass_rate = round((total_passed / len(records)) * 100, 1) if records else 0
        notes.append(f"Asilimia ya kufaulu kwa darasa: {overall_pass_rate}%")
        
        return notes
    
    def get_expected_structure(self) -> Dict:
        """Get expected JSON structure"""
        return {
            'subjects': self.subjects,
            'grading_rules': self.grading_rules,
            'expected_fields': self.base_fields,
            'sample_data': [
                {
                    'admission_no': 'ADM001',
                    'student_id': 'STU001',
                    'full_name': 'JOHN MWAMBA',
                    'gender': 'M',
                    'class': 'FORM 4',
                    'stream': 'EAST',
                    'subjects': {
                        'MATHEMATICS': 95,
                        'ENGLISH': 92,
                        'KISWAHILI': 88,
                        'SCIENCE': 90,
                        'GEOGRAPHY': 85
                    },
                    'remarks': 'Excellent student'
                },
                {
                    'admission_no': 'ADM002',
                    'student_id': 'STU002',
                    'full_name': 'SARAH JUMANNE',
                    'gender': 'F',
                    'class': 'FORM 4',
                    'stream': 'EAST',
                    'subjects': {
                        'MATHEMATICS': 78,
                        'ENGLISH': 85,
                        'KISWAHILI': 82,
                        'SCIENCE': 76,
                        'GEOGRAPHY': 80
                    },
                    'remarks': 'Very good performance'
                }
            ],
            'validation_rules': {
                'marks_range': '0-100 kwa masomo yote',
                'gender_values': 'M/male, F/female',
                'required_fields': self.base_fields,
                'subjects_required': self.subjects
            }
        }