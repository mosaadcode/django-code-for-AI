from datetime import datetime,timedelta
from django import forms
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.signals import post_save,pre_delete
from django.contrib.postgres.fields import ArrayField
from student.models import Student as StudentAcc
from django.dispatch import receiver

SCHOOL_CHOICES = (
    ("Alfarouk",'Alfarouk'),
    ("FIS",'FIS'),
    ('Ig','Ig'),
    ('بنين','بنين'),
    ('بنات','بنات'),
)

class School(models.Model):
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES)
    count = models.PositiveSmallIntegerField()
    def __str__(self):
        return f"{self.school} {self.count}"

class Department(models.Model):
    name = models.CharField(max_length=26)
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name='Department'
        verbose_name_plural ='  الأقسام '     

class Job(models.Model):

    TYPES_CHOICES = (
        ('إدارية','إدارية'),
        ('تعليمية','تعليمية'),
        ('خدمية','خدمية'),
    )
    GRADE_CHOICES = (
        ('10','رياض أطفال'),
        ('20','ابتدائى'),
        ('30','اعدادى'),
        ('40','ثانوى'),
        ('50','اعدادى وثانوى'),
    )
    type = models.CharField(max_length=7, choices=TYPES_CHOICES, verbose_name='نوع الوظيفة')
    title = models.CharField(max_length=20 ,verbose_name='المسمى الوظيفي')
    department = models.ForeignKey(Department, on_delete=SET_NULL, null=True,related_name='jobs',verbose_name='القسم')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, null=True,blank=True,verbose_name='المرحلة الدراسية')
    employees = models.ManyToManyField("Employee", blank=True,related_name='jobs',verbose_name='موظفين')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES,null=True,blank=True,verbose_name='المدرسة ')

    def __str__(self):
        # Determine if we need English format
        is_english = False
        if self.department and self.school == "FIS":
            is_english = True
        elif hasattr(self, 'school') and self.school  == "FIS":
            is_english = True
        
        # Build the string parts
        title_part = self.title
        dept_part = f" {self.department.name}" if self.department else ""
        grade_part = f" ({self.get_grade_display()})" if self.grade else ""
        
        # Arrange parts based on language
        if is_english:
            # English format: "Department Title (Grade)"
            if self.department:
                return f"{self.department.name} {self.title}{grade_part}"
            else:
                return f"{self.title}{grade_part}"
        else:
            # Arabic format: "Title Department ( Grade )"
            return f"{self.title}{dept_part}{grade_part}"

    class Meta:
        verbose_name='job'
        verbose_name_plural ='  الوظائف '        

class Employee(models.Model):
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES,verbose_name='المدرسة ')
    code = models.CharField(max_length=7, unique=True,blank=True,verbose_name='كود')
    name = models.CharField(max_length=60,verbose_name='الإسم')
    na_id = models.CharField(max_length=14, unique=True,verbose_name='رقم قومي ')
    birth_date = models.DateField(null=True,blank=True, verbose_name='تاريخ الميلاد ')
    mobile_number = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف محمول')
    phone_number = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف المنزل ')
    emergency_phone = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف طوارئ')
    email = models.EmailField(max_length=60, blank=True,null=True)
    address = models.CharField( max_length=86,null=True,blank=True,verbose_name='العنوان ')
    basic_certificate = models.CharField(max_length=96, blank=True, null=True,verbose_name='المؤهل الاساسي')
    is_educational = models.BooleanField(default=False,verbose_name='تربوي')
    attendance_date = models.DateField(null=True,blank=True,verbose_name='تاريخ الحضور')
    insurance_date = models.DateField(null=True,blank=True,verbose_name='تاريخ التأمين')
    participation_date = models.DateField(null=True,blank=True,verbose_name='تاريخ الاشتراك')
    contract_date = models.DateField(null=True,blank=True,verbose_name='تاريخ إعتماد العقد')
    insurance_no = models.CharField(max_length=10, unique=True,null=True,blank=True,verbose_name='الرقم التأميني')
    notes = models.TextField( max_length=260,null=True,blank=True,verbose_name='ملاحظات ')
    job = models.ForeignKey(Job, on_delete=SET_NULL,null=True, blank=True,verbose_name='الوظيفة')
    is_active = models.BooleanField(default=True,verbose_name='حالة العمل')
    salary_parameter = models.TextField( max_length=120,blank=True,null=True,verbose_name='عوامل تحديد الراتب ')
    salary = models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True,verbose_name='الراتب')
    message = models.CharField(max_length=260, null=True, blank=True)
    time_code = models.CharField(max_length=6,unique=True,blank=True,null=True,verbose_name='كود البصمة')
    permission_setting = models.ForeignKey("Permission_setting", on_delete=models.SET_NULL,blank=True, null=True,verbose_name='إعدادات الاَذون ')
    vacation_setting = models.ForeignKey("Vacation_setting", on_delete=models.SET_NULL,blank=True, null=True,verbose_name='حضور وإجازات')
    used_vacations = models.PositiveSmallIntegerField(default=0,verbose_name='اجازات ')
    used_vacations_s = models.PositiveSmallIntegerField(default=0,verbose_name='اجازات مرضي ')
    used_absents = models.PositiveSmallIntegerField(default=0,verbose_name='غياب بإذن ')
    manager1 = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,verbose_name='رئيس مباشر ',related_name="employees1")
    manager2 = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,verbose_name='رئيس أعلى ',related_name="employees2")
    rules_agreed = models.BooleanField(default=False, verbose_name='موافقة على اللائحة')
    rules_agreed_date = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الموافقة')
    
    def get_code(self):
        if not self.code:
            code_gen = [self.na_id[1:3]]
            school_code = 'b' if self.school == "بنين" else \
                'g' if self.school in ('Ig', 'بنات') else \
                'a' if self.school == 'Alfarouk' else \
                'f' if self.school == 'FIS' else None
            myschool = School.objects.get(school=self.school)
            myschool.count += 1
            code_gen.extend([school_code, format(myschool.count, '04')])
            myschool.save()
            return ''.join(code_gen)

    def get_birth_date(self):
        if not self.birth_date:
            if self.na_id[0] in ["2", "3"]:
                year_prefix = '19' if self.na_id[0] == "2" else '20'
                birth_date = datetime.strptime(year_prefix + self.na_id[1:3] + '-' + self.na_id[3:5] + '-' + self.na_id[5:7], '%Y-%m-%d').date()
                return birth_date

    def save(self, *args, **kwargs):
        if self.code == "":
            self.code = self.get_code()
        if self.birth_date is None:
            self.birth_date = self.get_birth_date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='employee'
        verbose_name_plural ='    سجلات الموظفين'     

class ModifiedArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
            **kwargs
        }
        return super(ArrayField, self).formfield(**defaults)

LABELS_CHOICES = [(str(i), str(i)) for i in range(16, 32)] + [(str(i), str(i)) for i in range(1, 16)]

class MonthN(models.Model):

   
    STATUS_CHOSIES = (
        ('1','جديد'),
        ('2','قيد النشر'),
        ('3','مغلق'),
    )
    code = models.CharField(blank=True,null=True,max_length=7,verbose_name='شهر  ')
    active=models.BooleanField(default=False,verbose_name='نشط  ')
    published =models.BooleanField(default=False,verbose_name='نشر  ')
    status=models.CharField(max_length=1,choices=STATUS_CHOSIES,default=1,verbose_name='الحالة  ')
    start_date = models.DateField(verbose_name='تاريخ البدء')
    end_date = models.DateField(verbose_name='تاريخ الانتهاء')

    dayoff = ModifiedArrayField(
        models.CharField(
            choices=LABELS_CHOICES,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name='العطلات الرسمية',
    )

    def calculate_dayoff(self):
        # Calculate the default value for dayoff based on start_date and end_date
        Friday_days = []
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() == 4:  # 4 represents Friday (0=Monday, 1=Tuesday, ..., 6=Sunday)
                Friday_days.append(str(current_date.day))
            current_date += timedelta(days=1)
        return Friday_days

    def calculate_code(self):
        # Calculate the code based on the end_date in the format 'yyyy-mm'
        return self.end_date.strftime('%Y-%m')

    def save(self, *args, **kwargs):
        if not self.dayoff:
            self.dayoff = self.calculate_dayoff()
        if not self.code:
            self.code = self.calculate_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'month'
        verbose_name_plural = '  إعدادات الشهور'

class SalaryItem(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,verbose_name='إسم الموظف')
    month = models.ForeignKey(MonthN, on_delete=models.CASCADE, null=True,verbose_name='شهر ')
    item = models.CharField(max_length=66,verbose_name='الوصف')
    value = models.SmallIntegerField(verbose_name='القيمة')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES,null=True,verbose_name='المدرسة ')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.month == "":
            self.month = MonthN.objects.get(active=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.name

    class Meta:
        verbose_name='SalaryItem'
        verbose_name_plural ='  مفردات الرواتب '   

class Vacation(models.Model):
    OFF_CHOICES = (
    ('إذن غياب','إذن غياب'),
    ('مرضي','مرضي'),
    ('من الرصيد','من الرصيد'),
)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='emp_vacations',verbose_name='إسم الموظف')
    month = models.ForeignKey(MonthN, on_delete=models.CASCADE, related_name='month_vacations',null=True,verbose_name='شهر ')
    date_from = models.DateField(verbose_name='من')
    date_to = models.DateField(verbose_name='الى')
    type = models.CharField(max_length=9, choices=OFF_CHOICES,null=True,verbose_name='النوع')
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,verbose_name='المدرسة')
    created = models.DateTimeField(auto_now_add=True)
    ok1 = models.BooleanField(default=False,verbose_name='رئيس مباشر')
    ok2 = models.BooleanField(default=False,verbose_name='رئيس أعلى ')
    count = models.PositiveSmallIntegerField(default=0,verbose_name='عدد ايام')
    total = models.PositiveSmallIntegerField(default=0,verbose_name='متاح ')
    days = ArrayField(models.IntegerField(), default=list,verbose_name='ايام ')
    photo = models.ImageField(upload_to='vacation_photos/', null=True, blank=True, verbose_name='صورة الإجازة')

    def save(self, *args, **kwargs):
        if self.month == "":
            self.month = MonthN.objects.last()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.name

    class Meta:
        verbose_name='vacation'
        verbose_name_plural ='   سجلات الاجازات'   

class Employee_month(models.Model):   
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='emp_months',verbose_name='إسم الموظف')
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,verbose_name='المدرسة')    
    month = models.ForeignKey(MonthN, on_delete=models.CASCADE,related_name='month_emp_months',null=True,verbose_name='شهر')
    is_active = models.BooleanField(default=True,verbose_name='نشط')
    permissions = models.PositiveSmallIntegerField(default=0,verbose_name='اَذون')
    vacations = models.PositiveSmallIntegerField(default=0,verbose_name='إجازات')
    vacations_s = models.PositiveSmallIntegerField(default=0,verbose_name='مرضي ')
    salary_value = models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True,verbose_name='الراتب')
    absent =models.PositiveSmallIntegerField(default=0,verbose_name='غياب')
    absent_ok =models.PositiveSmallIntegerField(default=0,verbose_name='غياب بإذن')

    def __str__(self):
        return self.employee.code
    
    class Meta:
        # Add a unique constraint on employee and month fields
        unique_together = ('employee', 'month')

    class Meta:
        verbose_name='Employee Month'
        verbose_name_plural ='   سجلات شهرية' 

class Permission_setting(models.Model):
    name = models.CharField(max_length=26,verbose_name='الإسم')
    is_perms = models.BooleanField(default=False,verbose_name='السماح بالاَذون')
    is_morning = models.BooleanField(default=False,verbose_name='صباحي')
    is_evening = models.BooleanField(default=False,verbose_name='مسائي')
    is_between = models.BooleanField(default=False,verbose_name='داخلي')
    is_over = models.BooleanField(default=False,verbose_name='السماح بتجاوز عدد الاَذون')
    perms = models.PositiveSmallIntegerField(default=4,verbose_name='عدد الاّذون المتاحة خلال الشهر')
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='permation setting'
        verbose_name_plural ='  إعدادات الاَذون'
        unique_together = [['name', 'school']]

class Vacation_setting(models.Model):
    name = models.CharField(max_length=26,verbose_name='الإسم')
    is_vacation = models.BooleanField(default=False,verbose_name='اجازة من الرصيد ')
    is_vacation_s = models.BooleanField(default=False,verbose_name='اجازة مرضي  ')
    is_absent = models.BooleanField(default=False,verbose_name='إذن غياب')
    vacations = models.PositiveSmallIntegerField(default=21,verbose_name='رصيد اجازات ')
    vacations_s = models.PositiveSmallIntegerField(default=7,verbose_name='رصيد اجازات مرضي ')
    absents = models.PositiveSmallIntegerField(default=3,verbose_name='رصيد غياب')
    time_in = models.CharField(max_length=5,verbose_name='موعد الحضور')
    time_out = models.CharField(max_length=5,verbose_name='موعد الإنصراف')
    time_in_perm = models.CharField(max_length=5,verbose_name='حضور بإذن')
    time_out_perm = models.CharField(max_length=5,verbose_name='إنصراف بإذن')
    saturday = models.BooleanField(default=False,verbose_name='إجازة ايام السبت')
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='vacation setting'
        verbose_name_plural ='  إعدادات الاجازات'
        unique_together = [['name', 'school']]

class Time_setting(models.Model):
    name = models.ForeignKey(Vacation_setting, on_delete=models.CASCADE,null=True,verbose_name='مواعيد ')
    date = models.DateField(verbose_name='يوم')
    time_in = models.CharField(max_length=5,verbose_name='موعد الحضور')
    time_out = models.CharField(max_length=5,verbose_name='موعد الإنصراف')
    time_in_perm = models.CharField(max_length=5,verbose_name='حضور بإذن')
    time_out_perm = models.CharField(max_length=5,verbose_name='إنصراف بإذن')
    month = models.ForeignKey(MonthN, on_delete=SET_NULL, null=True,verbose_name='شهر ')
    dayoff = models.BooleanField(default=False,verbose_name='عطلة')
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES,null=True,blank=True)
    

    def __str__(self):
        return self.name.name

    class Meta:
        verbose_name='Time setting'
        verbose_name_plural ='  مواعيد الحضور والإنصراف والعطلات'

class Permission(models.Model):
    PERM_CHOICES = (
    ('صباحي','صباحي'),
    ('داخلي','داخلي'),
    ('مسائي','مسائي'),
)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='emp_permissions',verbose_name='موظف')
    month = models.ForeignKey(MonthN, on_delete=models.CASCADE,related_name='month_permissions',blank=True,null=True,verbose_name='شهر ')
    date = models.DateField(verbose_name='يوم ')
    type = models.CharField( max_length=5, choices=PERM_CHOICES,null=True,verbose_name='إذن ')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES,null=True,verbose_name='المدرسة ')
    created = models.DateTimeField(auto_now_add=True)
    ok1 = models.BooleanField(default=False,verbose_name='رئيس مباشر')
    ok2 = models.BooleanField(default=False,verbose_name='رئيس أعلى')
    start_time = models.CharField(max_length=5,blank=True,null=True,verbose_name='من ساعة')
    end_time = models.CharField(max_length=5,blank=True,null=True,verbose_name='الى ساعة')
    count = models.PositiveSmallIntegerField(default=0,verbose_name='إذن')
    total = models.PositiveSmallIntegerField(default=0,verbose_name='من ')

    # @property
    # def department_name(self):
    #     return self.employee.job.department.name if self.employee and self.employee.job and self.employee.job.department else ''

    def __str__(self):
        return self.employee.name

    class Meta:
        verbose_name='permission'
        verbose_name_plural ='   سجلات الاَذون'   

def create_employ(sender, instance, created, **kwargs):
    if created:
        StudentAcc.objects.create(
            code=instance.code,
            username=instance.name,
            password=make_password(instance.code),
            school=instance.school,
            year='emp22',
            is_employ=True,
            )
post_save.connect(create_employ, sender=Employee)


@receiver(pre_delete, sender=Vacation)
def delete_vacation_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete()