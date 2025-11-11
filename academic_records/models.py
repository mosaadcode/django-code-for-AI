# academic_records/models.py
from django.db import models
from student_affairs.models import Student

class Subject(models.Model):
    SCHOOL_CHOICES = (
        (None, ""),
        ('Alfarouk','Alfarouk'),
        ('بنين', 'بنين'),
        ('بنات', 'بنات'),
    )
    GRADE_CHOICES = (
        (None, ""),
        ('01','Grade 1'),
        ('02','Grade 2'),
        ('03','Grade 3'),
        ('04','Grade 4'),
        ('05','Grade 5'),
        ('06','Grade 6'),
        ('07','Grade 7'),
        ('08','Grade 8'),
        ('09','Grade 9'),
        ('10','Grade 10'),
        ('11','Grade 11'),
        ('12','Grade 12'),
    )
    
    code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES)
    grade = models.CharField(max_length=15, choices=GRADE_CHOICES)
    subject_name = models.CharField(max_length=100)
    
    # Maximum scores for each assessment type
    monthly_max = models.IntegerField(null=True, blank=True, verbose_name="Monthly Max Score")
    weekly_max = models.IntegerField(null=True, blank=True, verbose_name="Weekly Max Score")
    performance_max = models.IntegerField(null=True, blank=True, verbose_name="Performance Max Score")
    homework_max = models.IntegerField(null=True, blank=True, verbose_name="Homework Max Score")
    activity_max = models.IntegerField(null=True, blank=True, verbose_name="Activity Max Score")
    attendance_max = models.IntegerField(null=True, blank=True, verbose_name="Attendance Max Score")
    oral_max = models.IntegerField(null=True, blank=True, verbose_name="Oral Max Score")
    year_work_max = models.IntegerField(null=True, blank=True, verbose_name="Year Work Max Score")
    final_exam_max = models.IntegerField(null=True, blank=True, verbose_name="Final Exam Max Score")

    def get_code(self):
        if not self.code:
            code_gen = []
            code_gen.append(self.subject_name)
            if self.school == "بنين":
                code_gen.append('2')
            elif self.school == "Alfarouk":
                code_gen.append('1')
            else:
                code_gen.append('3')
            code_gen.append(self.grade[:2])
            return ''.join(code_gen)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.get_code()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['grade', 'subject_name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['grade', 'subject_name']
    
    def __str__(self):
        return f"{self.grade} - {self.subject_name}"

class StudentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # October Assessments
    monthly_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Monthly")
    weekly_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Weekly")
    performance_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Performance")
    homework_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Homework")
    activity_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Activity")
    attendance_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Attendance")
    oral_oct = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Oral")
    
    # November Assessments
    monthly_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Monthly")
    weekly_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Weekly")
    performance_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Performance")
    homework_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Homework")
    activity_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Activity")
    attendance_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Attendance")
    oral_nov = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Oral")
    
    # March Assessments
    monthly_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Monthly")
    weekly_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Weekly")
    performance_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Performance")
    homework_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Homework")
    activity_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Activity")
    attendance_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Attendance")
    oral_mar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Oral")
    
    # April Assessments
    monthly_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Monthly")
    weekly_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Weekly")
    performance_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Performance")
    homework_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Homework")
    activity_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Activity")
    attendance_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Attendance")
    oral_apr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Oral")
    
    # Final Exam
    final_exam = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Monthly totals
    oct_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nov_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mar_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    apr_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Calculation status
    is_calculated = models.BooleanField(default=False, verbose_name="Totals Calculated")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject']
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'
        indexes = [
            models.Index(fields=['is_calculated']),
        ]
    
    def calculate_month_total(self, month_prefix):
        """Calculate total for a specific month"""
        total = 0
        fields = [f'monthly_{month_prefix}', f'weekly_{month_prefix}', f'performance_{month_prefix}',
                 f'homework_{month_prefix}', f'activity_{month_prefix}', f'attendance_{month_prefix}', 
                 f'oral_{month_prefix}']
        
        for field in fields:
            value = getattr(self, field)
            if value is not None:
                total += value
        return total
    
    def calculate_all_totals(self):
        """Calculate all totals and mark as calculated"""
        self.oct_total = self.calculate_month_total('oct')
        self.nov_total = self.calculate_month_total('nov')
        self.mar_total = self.calculate_month_total('mar')
        self.apr_total = self.calculate_month_total('apr')
        
        # Calculate overall total (average of months + final exam)
        month_totals = [self.oct_total, self.nov_total, self.mar_total, self.apr_total]
        valid_totals = [t for t in month_totals if t > 0]
        month_avg = sum(valid_totals) / len(valid_totals) if valid_totals else 0
        self.overall_total = month_avg + (self.final_exam or 0)
        
        # Set calculated status to TRUE
        self.is_calculated = True
        
        # Save only the calculated fields
        self.save(update_fields=[
            'oct_total', 'nov_total', 'mar_total', 'apr_total', 
            'overall_total', 'is_calculated'
        ])
    
    @classmethod
    def bulk_calculate_totals(cls, queryset):
        """Bulk calculate totals for a queryset - MUCH FASTER"""
        marks_to_update = []
        for mark in queryset:
            # Calculate totals but don't save individually
            mark.oct_total = mark.calculate_month_total('oct')
            mark.nov_total = mark.calculate_month_total('nov')
            mark.mar_total = mark.calculate_month_total('mar')
            mark.apr_total = mark.calculate_month_total('apr')
            
            month_totals = [mark.oct_total, mark.nov_total, mark.mar_total, mark.apr_total]
            valid_totals = [t for t in month_totals if t > 0]
            month_avg = sum(valid_totals) / len(valid_totals) if valid_totals else 0
            mark.overall_total = month_avg + (mark.final_exam or 0)
            
            mark.is_calculated = True
            marks_to_update.append(mark)
        
        # Bulk update all at once - MUCH faster
        if marks_to_update:
            cls.objects.bulk_update(
                marks_to_update,
                ['oct_total', 'nov_total', 'mar_total', 'apr_total', 'overall_total', 'is_calculated']
            )
        
        return len(marks_to_update)
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}"