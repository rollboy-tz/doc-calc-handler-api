# services/upload_handlers/multi_subject_upload.py
"""
MULTI SUBJECT UPLOAD HANDLER - TANZANIA NECTA SYSTEM  
Process uploaded Excel with marks for MULTIPLE subjects
Returns clean data with gender analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Set
from ..calculations.grade_calculator import GradeCalculator

class MultiSubjectUploadHandler:
    """
    Handle upload of Excel file with MULTIPLE subjects marks - Tanzania NECTA
    
    Expected Excel structure:
    - Columns A-F: Student info (including gender)
    - Columns G onward: Subject marks (one column per subject)
    """
    
    def __init__(self, subjects: List[str], grading_rules: str = 'CSEE'):
        self.subjects = subjects
        self.grading_rules = grading_rules  # 'CSEE' or 'PSLE'
        self.calculator = GradeCalculator(grading_rules)
        
        # Base columns that should always be present
        self.base_columns = ['admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream']
    
    def process_upload(self, excel_file_path: str) -> Dict:
        """
        Process uploaded multi-subject Excel file
        
        Args:
            excel_file_path: Path to uploaded Excel file
            
        Returns:
            Dictionary with processed data for Node.js
        """
        try:
            # 1. Read Excel file with header row 1 (skip title)
            df = pd.read_excel(excel_file_path, header=None)

            if len(df) > 0:
                # Row 0 contains headers
                df.columns = df.iloc[0]
                # Remove the header row from data
                df = df.iloc[1:].reset_index(drop=True)
        

            # 2. Detect subjects from file
            detected_subjects = self._detect_subjects(df)
            
            # 3. Validate file structure
            validation = self._validate_structure(df, detected_subjects)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid file structure',
                    'details': validation['errors'],
                    'detected_subjects': detected_subjects
                }
            
            # 4. Extract and clean data for each student
            student_records = self._extract_student_records(df, detected_subjects)
            
            # 5. Calculate grades for each subject (Tanzania NECTA)
            processed_records = self._calculate_all_grades(student_records, detected_subjects)
            
            # 6. Calculate student summaries and positions
            final_results = self._calculate_summaries(processed_records, detected_subjects)
            
            # 7. Generate class-wide statistics with GENDER analysis
            class_summary = self._generate_class_summary(final_results, detected_subjects)
            
            # 8. Return comprehensive data for Node.js
            return {
                'success': True,
                'subjects_processed': detected_subjects,
                'total_students': len(final_results),
                'grading_rules': self.grading_rules,
                'class_summary': class_summary,
                'student_records': final_results,
                'processing_stats': {
                    'valid_students': len([s for s in final_results if s['valid']]),
                    'invalid_students': len([s for s in final_results if not s['valid']]),
                    'subjects_found': len(detected_subjects),
                    'subjects_missing': list(set(self.subjects) - set(detected_subjects)) if self.subjects else []
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'subjects_expected': self.subjects
            }
    
    def _detect_subjects(self, df: pd.DataFrame) -> List[str]:
        """Detect subject columns in the uploaded file"""
        all_columns = [str(col).strip() for col in df.columns.tolist()]
        
        # Subject columns are those not in base columns
        base_set = set(self.base_columns)
        subject_columns = [col for col in all_columns if col not in base_set and col.lower() != 'remarks']
        
        # If subjects were specified, filter to only those
        if self.subjects:
            # Match case-insensitive
            available_subjects = []
            for specified_subject in self.subjects:
                for actual_col in subject_columns:
                    if specified_subject.lower() in actual_col.lower() or actual_col.lower() in specified_subject.lower():
                        available_subjects.append(actual_col)
            subject_columns = available_subjects
        
        return subject_columns
    
    def _validate_structure(self, df: pd.DataFrame, subjects: List[str]) -> Dict:
        """Validate Excel file structure"""
        errors = []
        
        # Check base columns (all are required)
        for col in self.base_columns:
            if col not in df.columns:
                errors.append(f'Missing required column: {col}')
        
        # Check gender values
        if 'gender' in df.columns:
            unique_genders = df['gender'].dropna().unique()
            for gender in unique_genders:
                gender_str = str(gender).strip().lower()
                if gender_str not in ['m', 'f', 'male', 'female']:
                    errors.append(f'Invalid gender value: {gender}')
        
        # Check if we have any subject columns
        if not subjects:
            errors.append('No subject columns found in file')
        
        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2
            
            # Check student info
            if pd.isna(row.get('admission_no')) or pd.isna(row.get('student_id')) or pd.isna(row.get('full_name')):
                errors.append(f'Row {row_num}: Missing admission_no, student_id, or full_name')
                continue
            
            # Validate gender
            if pd.notna(row.get('gender')):
                gender = str(row['gender']).strip().lower()
                if gender not in ['m', 'f', 'male', 'female']:
                    errors.append(f'Row {row_num}: Invalid gender: {row["gender"]}')
            
            # Validate marks for each subject
            for subject in subjects:
                if subject in df.columns and pd.notna(row[subject]):
                    try:
                        mark = float(row[subject])
                        if not (0 <= mark <= 100):  # Assuming 100 max for all subjects
                            errors.append(f'Row {row_num}: {subject} marks {mark} out of range (0-100)')
                    except ValueError:
                        errors.append(f'Row {row_num}: {subject} invalid marks format')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors[:10],  # Limit to first 10 errors
            'total_errors': len(errors)
        }
    
    def _extract_student_records(self, df: pd.DataFrame, subjects: List[str]) -> List[Dict]:
        """Extract student records from DataFrame"""
        records = []
        
        for _, row in df.iterrows():
            # Skip rows with missing essential info
            if pd.isna(row.get('admission_no')) or pd.isna(row.get('student_id')):
                continue
            
            # Normalize gender
            gender = None
            if pd.notna(row.get('gender')):
                gender_str = str(row['gender']).strip().lower()
                if gender_str in ['m', 'male']:
                    gender = 'M'
                elif gender_str in ['f', 'female']:
                    gender = 'F'
            
            record = {
                'admission_no': str(row['admission_no']).strip(),
                'student_id': str(row['student_id']).strip(),
                'full_name': str(row.get('full_name', '')).strip(),
                'gender': gender,
                'class': str(row.get('class', '')).strip(),
                'stream': str(row.get('stream', '')).strip(),
                'subjects': {},
                'valid': True,
                'errors': []
            }
            
            # Extract marks for each subject
            for subject in subjects:
                if subject in df.columns:
                    if pd.notna(row[subject]):
                        try:
                            record['subjects'][subject] = {
                                'mark': float(row[subject]),
                                'grade': None,      # Will be calculated
                                'remarks': None     # Will be calculated
                            }
                        except:
                            record['subjects'][subject] = {'mark': None, 'error': 'Invalid format'}
                            record['valid'] = False
                            record['errors'].append(f'{subject}: Invalid marks format')
                    else:
                        record['subjects'][subject] = {'mark': None, 'status': 'ABSENT'}
            
            records.append(record)
        
        return records
    
    def _calculate_all_grades(self, records: List[Dict], subjects: List[str]) -> List[Dict]:
        """Calculate grades for all subjects using Tanzania NECTA system"""
        for record in records:
            for subject, data in record['subjects'].items():
                if data.get('mark') is not None:
                    grade_info = self.calculator.calculate_grade(data['mark'])
                    record['subjects'][subject]['grade'] = grade_info['grade']
                    record['subjects'][subject]['remarks'] = grade_info['remarks']
                    record['subjects'][subject]['grade_points'] = grade_info['points']  # TZ points (1-5)
        
        return records
    
    def _calculate_summaries(self, records: List[Dict], subjects: List[str]) -> List[Dict]:
        """Calculate student summaries (totals, averages, positions)"""
        for record in records:
            # Get all valid marks
            marks = []
            grades = []
            present_subjects = []
            
            for subject, data in record['subjects'].items():
                if data.get('mark') is not None:
                    marks.append(data['mark'])
                    grades.append(data.get('grade', ''))
                    present_subjects.append(subject)
            
            # Count passing grades (A, B, C, D are passes in TZ)
            passing_grades = ['A', 'B', 'C', 'D']
            passed_subjects = [grade for grade in grades if grade in passing_grades]
            
            if marks:
                record['summary'] = {
                    'total_marks': sum(marks),
                    'average_mark': round(sum(marks) / len(marks), 2),
                    'subjects_count': len(subjects),
                    'subjects_present': len(present_subjects),
                    'subjects_absent': len(subjects) - len(present_subjects),
                    'subjects_passed': len(passed_subjects),
                    'subjects_failed': len(present_subjects) - len(passed_subjects),
                    'pass_rate': round((len(passed_subjects) / len(present_subjects)) * 100, 1) if present_subjects else 0,
                    'grades': grades
                }
            else:
                record['summary'] = {
                    'total_marks': 0,
                    'average_mark': 0,
                    'subjects_count': len(subjects),
                    'subjects_present': 0,
                    'subjects_absent': len(subjects),
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
    
    def _generate_class_summary(self, records: List[Dict], subjects: List[str]) -> Dict:
        """Generate class-wide statistics with GENDER analysis"""
        # Gender breakdown
        male_students = [r for r in records if r.get('gender') == 'M']
        female_students = [r for r in records if r.get('gender') == 'F']
        unknown_gender = len(records) - len(male_students) - len(female_students)
        
        # Subject-wise statistics
        subject_stats = {}
        for subject in subjects:
            marks = []
            male_marks = []
            female_marks = []
            
            for record in records:
                if subject in record['subjects'] and record['subjects'][subject].get('mark') is not None:
                    mark = record['subjects'][subject]['mark']
                    marks.append(mark)
                    
                    # Separate by gender
                    if record.get('gender') == 'M':
                        male_marks.append(mark)
                    elif record.get('gender') == 'F':
                        female_marks.append(mark)
            
            if marks:
                # Grade distribution for this subject
                grades = [r['subjects'][subject].get('grade', 'ABSENT') for r in records if subject in r['subjects']]
                grade_dist = {}
                for grade in ['A', 'B', 'C', 'D', 'E', 'ABSENT']:
                    count = grades.count(grade)
                    if count > 0:
                        grade_dist[grade] = count
                
                subject_stats[subject] = {
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
        
        # Pass rate by gender
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
    
    def _generate_summary_notes(self, records, subject_stats, male_students, female_students):
        """Generate summary notes in Swahili"""
        notes = [
            f"Jumla ya wanafunzi: {len(records)}",
            f"Wavulana: {len(male_students)}",
            f"Wasichana: {len(female_students)}"
        ]
        
        # Subject performance highlights
        for subject, stats in subject_stats.items():
            if stats['students_with_marks'] > 0:
                best_subject = max(subject_stats.items(), key=lambda x: x[1]['average'])[0] if subject_stats else ""
                worst_subject = min(subject_stats.items(), key=lambda x: x[1]['average'])[0] if subject_stats else ""
                
                notes.append(f"Somo bora: {best_subject} (wastani: {subject_stats[best_subject]['average']}%)")
                notes.append(f"Somo dhaifu: {worst_subject} (wastani: {subject_stats[worst_subject]['average']}%)")
                break
        
        # Gender performance comparison
        if male_students and female_students:
            male_avg = np.mean([s['summary']['average_mark'] for s in male_students if s['summary']['average_mark'] > 0])
            female_avg = np.mean([s['summary']['average_mark'] for s in female_students if s['summary']['average_mark'] > 0])
            
            notes.append(f"Wastani wa wavulana: {round(male_avg, 1)}%")
            notes.append(f"Wastani wa wasichana: {round(female_avg, 1)}%")
        
        return notes
    
    def get_expected_template(self) -> Dict:
        """Get expected template structure for multiple subjects"""
        return {
            'required_base_columns': self.base_columns,
            'subject_columns': self.subjects,
            'grading_rules': self.grading_rules,
            'instructions': 'Jaza alama katika safu za masomo pekee. Usihariri taarifa za mwanafunzi.',
            'validation_rules': {
                'marks_range': '0-100 kwa masomo yote',
                'gender_values': 'M/male, F/female',
                'required_fields': self.base_columns,
                'optional_fields': ['Remarks']
            }
        }