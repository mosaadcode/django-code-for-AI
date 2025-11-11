# academic_records/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import Subject, StudentMark
from .resources import SubjectResource, StudentMarkResource

@admin.register(StudentMark)
class StudentMarkAdmin(ImportExportModelAdmin):
    resource_class = StudentMarkResource
    
    # Clean list display
    list_display = [
        'student_code', 'student_name', 'student_class', 
        'subject_name', 'get_totals_preview', 'final_exam', 
        'overall_total', 'is_calculated'
    ]
    
    list_filter = [
        'student__Class', 'subject__school', 'subject__grade', 
        'subject__subject_name', 'is_calculated'
    ]
    
    search_fields = [
        'student__name', 'student__code', 
        'subject__subject_name', 'subject__code'
    ]
    
    readonly_fields = [
        'oct_total', 'nov_total', 'mar_total', 'apr_total', 
        'overall_total', 'created_at', 'updated_at', 'is_calculated'
    ]
    
    list_per_page = 25
    
    # Organized fieldsets with collapsible monthly sections
    fieldsets = (
        ('Student & Subject Information', {
            'fields': (
                'student', 'subject',
            )
        }),
        ('October Assessments', {
            'fields': (
                ('monthly_oct', 'weekly_oct', 'performance_oct'),
                ('homework_oct', 'activity_oct', 'attendance_oct'),
                'oral_oct',
                'oct_total',
            ),
            'classes': ('collapse',)
        }),
        ('November Assessments', {
            'fields': (
                ('monthly_nov', 'weekly_nov', 'performance_nov'),
                ('homework_nov', 'activity_nov', 'attendance_nov'),
                'oral_nov',
                'nov_total',
            ),
            'classes': ('collapse',)
        }),
        ('March Assessments', {
            'fields': (
                ('monthly_mar', 'weekly_mar', 'performance_mar'),
                ('homework_mar', 'activity_mar', 'attendance_mar'),
                'oral_mar',
                'mar_total',
            ),
            'classes': ('collapse',)
        }),
        ('April Assessments', {
            'fields': (
                ('monthly_apr', 'weekly_apr', 'performance_apr'),
                ('homework_apr', 'activity_apr', 'attendance_apr'),
                'oral_apr',
                'apr_total',
            ),
            'classes': ('collapse',)
        }),
        ('Final Exam & Overall Results', {
            'fields': (
                'final_exam',
                'overall_total',
                'is_calculated',
            )
        }),
        ('System Information', {
            'fields': (
                'created_at', 'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_totals_preview(self, obj):
        """Show monthly totals preview in list view"""
        if not obj.is_calculated:
            return "🔄 Needs Calculation"
            
        months = []
        if obj.oct_total > 0:
            months.append(f"Oct:{obj.oct_total}")
        if obj.nov_total > 0:
            months.append(f"Nov:{obj.nov_total}")
        if obj.mar_total > 0:
            months.append(f"Mar:{obj.mar_total}")
        if obj.apr_total > 0:
            months.append(f"Apr:{obj.apr_total}")
            
        return ' | '.join(months) if months else '-'
    get_totals_preview.short_description = 'Monthly Totals'
    
    # Simple column methods
    def student_code(self, obj):
        return obj.student.code
    student_code.short_description = 'Code'
    
    def student_name(self, obj):
        return obj.student.name
    student_name.short_description = 'Student'
    
    def student_class(self, obj):
        return obj.student.Class.name if obj.student.Class else 'N/A'
    student_class.short_description = 'Class'
    
    def subject_name(self, obj):
        return obj.subject.subject_name
    subject_name.short_description = 'Subject'
    

    def save_model(self, request, obj, form, change):
        """
        Simple approach: Always mark as not calculated when saving from admin
        """
        if change:  # Only for updates, not new creations
            obj.is_calculated = False
        
        # Call the parent save method
        super().save_model(request, obj, form, change)

    # Custom Admin Actions
    def calculate_totals_selected(self, request, queryset):
        """Bulk calculate totals for selected records - FAST"""
        updated_count = StudentMark.bulk_calculate_totals(queryset)
        
        self.message_user(
            request, 
            f"✅ Successfully calculated totals for {updated_count} records using bulk update."
        )
    calculate_totals_selected.short_description = "🧮 Calculate totals (Bulk - Fast)"
    
    def mark_as_uncalculated(self, request, queryset):
        """Mark selected records as needing calculation"""
        updated = queryset.update(is_calculated=False)
        self.message_user(
            request,
            f"🔄 Marked {updated} records as needing calculation."
        )
    mark_as_uncalculated.short_description = "🔄 Mark as needing calculation"
    
    # Add actions to the admin
    actions = [calculate_totals_selected, mark_as_uncalculated]
    
    def get_export_formats(self):
        return [base_formats.XLSX]
    
    def get_import_formats(self):
        return [base_formats.XLSX]

@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_class = SubjectResource
    
    list_display = ['code', 'school', 'grade', 'subject_name', 'get_active_assessments']
    list_filter = ['school', 'grade']
    search_fields = ['code', 'subject_name']
    readonly_fields = ['code']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'grade', 'subject_name', 'code')
        }),
        ('Maximum Scores (Set to 0 if not applicable)', {
            'fields': (
                ('monthly_max', 'weekly_max', 'performance_max'),
                ('homework_max', 'activity_max', 'attendance_max'),
                ('oral_max', 'final_exam_max'),
            )
        }),
    )
    
    def get_active_assessments(self, obj):
        """Show which assessments are active for this subject"""
        active = []
        if obj.monthly_max and obj.monthly_max > 0:
            active.append('Monthly')
        if obj.weekly_max and obj.weekly_max > 0:
            active.append('Weekly')
        if obj.performance_max and obj.performance_max > 0:
            active.append('Performance')
        if obj.homework_max and obj.homework_max > 0:
            active.append('Homework')
        if obj.activity_max and obj.activity_max > 0:
            active.append('Activity')
        if obj.attendance_max and obj.attendance_max > 0:
            active.append('Attendance')
        if obj.oral_max and obj.oral_max > 0:
            active.append('Oral')
            
        return ', '.join(active) if active else 'None'
    get_active_assessments.short_description = 'Active Assessments'
    
    def get_export_formats(self):
        return [base_formats.XLSX]
    
    def get_import_formats(self):
        return [base_formats.XLSX]