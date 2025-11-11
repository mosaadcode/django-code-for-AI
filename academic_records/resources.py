# # academic_records/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DecimalWidget
from .models import Subject, StudentMark
from student_affairs.models import Student

class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        import_id_fields = ['code']
        fields = ['code', 'school', 'grade', 'subject_name',
                 'monthly_max', 'weekly_max', 'performance_max', 'homework_max',
                 'activity_max', 'attendance_max', 'oral_max', 'year_work_max',
                 'final_exam_max']
        skip_unchanged = True
    
    def before_import_row(self, row, **kwargs):
        if ('code' not in row or not row['code']) and all(k in row for k in ['school', 'grade', 'subject_name']):
            code_gen = []
            code_gen.append(row['subject_name'])
            if row['school'] == "بنين":
                code_gen.append('2')
            elif row['school'] == "Alfarouk":
                code_gen.append('1')
            else:
                code_gen.append('3')
            
            grade_code = str(row['grade']).zfill(2)
            code_gen.append(grade_code[:2])
            row['code'] = ''.join(code_gen)

class StudentMarkResource(resources.ModelResource):
    student_code = fields.Field(
        column_name='student_code',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'code')
    )
    
    subject_code = fields.Field(
        column_name='subject_code', 
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'code')
    )
    
    # Add is_calculated field to the import/export
    is_calculated = fields.Field(
        column_name='is_calculated',
        attribute='is_calculated',
        widget=resources.widgets.BooleanWidget()
    )
    
    class Meta:
        model = StudentMark
        import_id_fields = ['student_code', 'subject_code']
        fields = [
            'student_code', 'subject_code',
            # October
            'monthly_oct', 'weekly_oct', 'performance_oct', 'homework_oct', 
            'activity_oct', 'attendance_oct', 'oral_oct',
            # November
            'monthly_nov', 'weekly_nov', 'performance_nov', 'homework_nov', 
            'activity_nov', 'attendance_nov', 'oral_nov',
            # March
            'monthly_mar', 'weekly_mar', 'performance_mar', 'homework_mar', 
            'activity_mar', 'attendance_mar', 'oral_mar',
            # April
            'monthly_apr', 'weekly_apr', 'performance_apr', 'homework_apr', 
            'activity_apr', 'attendance_apr', 'oral_apr',
            # Final
            'final_exam',
            # Include the calculation status
            'is_calculated'
        ]
        skip_unchanged = True
        use_bulk = True

    
    # def before_import_row(self, row, **kwargs):
    #     """Set is_calculated to False for ALL imported records - SIMPLE"""
    #     # This ensures imported records will need calculation
    #     row['is_calculated'] = False
    
    # def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
    #     """After import, all imported records are marked as not calculated"""
    #     if not dry_run:
    #         self.message_user = kwargs.get('message_user', print)
    #         self.message_user(f"✅ Import completed. {result.total_rows} records marked for calculation.")