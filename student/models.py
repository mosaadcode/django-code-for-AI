from django.db import models
from django.contrib.auth.models import (
AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db.models import Sum
from datetime import date
from django.db.models.deletion import SET_NULL

current_year = '26-25'

class Grade(models.Model):
    name = models.CharField(max_length=24, blank=True)
    def __str__(self):
        return self.name

YEAR_CHOICES = (
    ('26-25' , '26-25'),
    ('25-24' , '25-24'),
    ('24-23' , '24-23'),
    ('23-22' , '23-22'),
    ('22-21' , '22-21'),
    ('21-20' , '21-20'),
)
SCHOOL_CHOICES_2 = (
    ("Alfarouk",'Alfarouk'),
    ("FIS",'FIS'),
    ('Ig','Ig'),
    ('بنين','بنين'),
    ('بنات','بنات'),
)

AREA_CHOICES = (
    (None, ""),
    ('النزهة الجديدة','النزهة الجديدة'),
    ('شيراتون','شيراتون'),
    ('مصر الجديدة','مصر الجديدة'),
    ('الزيتون','الزيتون'),
    ('حدائق القبة','حدائق القبة'),
    ('العباسية','العباسية'),
    ('مدينة نصر','مدينة نصر'),
    ('إمتداد رمسيس','إمتداد رمسيس'),
    ('المعادى','المعادى'),
    ('المقطم','المقطم'),
    ('مدينتى','مدينتى'),
    ('الرحاب','الرحاب'),
    ('الرحاب 2','الرحاب 2'),
    ('التجمع الاول','التجمع الاول'),
    ('التجمع الثالث','التجمع الثالث'),
    ('التجمع الخامس','التجمع الخامس'),
    ('روكسي','روكسي'),
    ('السواح','السواح'),
    ('ارض الجولف','ارض الجولف'),
    ('الشروق','الشروق'),
    ('المستقبل','المستقبل'),
    ('مستثمرين شمالية','مستثمرين شمالية'),
    ('مستثمرين جنوبية','مستثمرين جنوبية'),
    ('الحرفيين','الحرفيين'),
)

class BusLocation(models.Model):
    name = models.CharField(max_length=24, blank=True)
    payment1 = models.PositiveIntegerField(default=0,verbose_name='Payment 1')
    payment2 = models.PositiveIntegerField(default=0,verbose_name='Payment 2')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES_2)
    # New field to store the calculated total
    total_bus_fees = models.PositiveIntegerField(default=0, editable=False) # editable=False hides it from the admin form

    def save(self, *args, **kwargs):
        # Automatically calculate the total before saving
        self.total_bus_fees = self.payment1 + self.payment2
        super().save(*args, **kwargs) # Call the original save method

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='Bus Location'
        verbose_name_plural ='المناطق السكنية '

SCHOOL_CHOICES1 = (
    (None, ""),
    ('بنين', 'بنين'),
    ('بنات', 'بنات'),
    ('مشترك','مشترك'),
    ('Ig','Ig'),
    ('Nile-b','Nile-b'),
    ('Nile-g','Nile-g'),
)

class Bus(models.Model):
    number = models.CharField(unique=True,max_length=4,verbose_name='رقم السيارة')
    area = models.ForeignKey(BusLocation, on_delete=models.SET_NULL, null=True, blank=True,verbose_name='المنطقة')
    sub_area = models.CharField(max_length=24,blank=True,null=True,verbose_name='المنطقة الفرعية')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES_2,verbose_name='المدرسة')
    driver_name = models.CharField(max_length=24,blank=True,null=True,verbose_name='اسم السائق')
    driver_mobile = models.CharField(max_length=11,blank=True,null=True,verbose_name='تليفون السائق')
    supervisor_name = models.CharField(max_length=24,blank=True,null=True,verbose_name='اسم المشرف')
    supervisor_mobile = models.CharField(max_length=11,blank=True,null=True,verbose_name='تليفون المشرف')
    supervisor_address = models.CharField( max_length=50,null=True,blank=True,verbose_name='عنوان المشرف ')
    supervisor_time = models.CharField(max_length=5,null=True,blank=True,verbose_name='موعد المشرف صباحا ')

    class Meta:
        verbose_name='Bus'
        verbose_name_plural ='السيارات المدرسية '

    def bus_count(self):
        s_count = Student.objects.filter(bus_number=self.id,year=current_year).count()
        t_count = Teacher.objects.filter(bus_number=self.id).count()
        return '( '+str(s_count+t_count)+' ) , '+str(t_count)+'t , '+str(s_count)+'s'

    def __str__(self):
        return self.number 

class Teacher(models.Model):
    name = models.CharField(unique=True,max_length=60,verbose_name='الاسم ')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES_2,null=True,verbose_name='المدرسة ')
    job = models.CharField(max_length=36, null=True, blank=True,verbose_name='الوظيفة ')
    phone_number = models.CharField(max_length=11, null=True, blank=True,verbose_name='رقم الهاتف ')
    living_area = models.ForeignKey(BusLocation, on_delete=models.SET_NULL, null=True, blank=True,verbose_name='المنطقة السكنية ')
    address = models.CharField( max_length=50,null=True,blank=True,verbose_name='العنوان ')
    bus_number = models.ForeignKey(Bus, on_delete=SET_NULL,null=True, blank=True,verbose_name='رقم السيارة ')
    bus_order = models.CharField(max_length=5,null=True,blank=True,verbose_name='موعد الركوب ')
    bus_notes = models.CharField(max_length=24, null=True, blank=True,verbose_name='نوع الاشتراك ')
    class Meta:
        verbose_name='teacher'
        verbose_name_plural ='اشتركات المعلمين '
    def __str__(self):
        return self.name

class StudentManager(BaseUserManager):
    def create_user(self, code, username, password=None):
        if not code:
            raise ValueError("Users must have a code")
        if not username:
            raise ValueError("Users must have a name")
        user = self.model(
               code = code,
               username = username,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, code, username, password):
        user = self.create_user(
               code = code,
               password = password,
               username = username,
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Student(AbstractBaseUser, PermissionsMixin):
    SCHOOL_CHOICES = (
        (None, ""),
        ("Alfarouk",'Alfarouk'),
        ('FIS','FIS'),
        ('Ig','Ig'),
        ('Nile-b','Nile-b'),
        ('Nile-g','Nile-g'),
        ('بنين', 'بنين'),
        ('بنات', 'بنات'),
        ('.بنات.', '.بنات.'),
        ('Out-b','Out-b'),
        ('Out-g','Out-g'),
    )
    GRADE_CHOICES = (
        (None, ""),
        ('تمهيدى حضانة', 'تمهيدى حضانة'),
        ('اولى حضانة', 'اولى حضانة'),
        ('ثانية حضانة', 'ثانية حضانة'),
        ('الاول الابتدائى','الاول الابتدائى'),
        ('الثانى الابتدائى','الثانى الابتدائى'),
        ('الثالث الابتدائى','الثالث الابتدائى'),
        ('الرابع الابتدائى','الرابع الابتدائى'),
        ('الخامس الابتدائى','الخامس الابتدائى'),
        ('السادس الابتدائى','السادس الابتدائى'),
        ('الاول الاعدادى','الاول الاعدادى'),
        ('الثانى الاعدادى','الثانى الاعدادى'),
        ('الثالث الاعدادى','الثالث الاعدادى'),
        ('الاول الثانوى','الاول الثانوى'),
        ('الثانى الثانوى','الثانى الثانوى'),
        ('الثالث الثانوى','الثالث الثانوى'),
        ('خريج','خريج'),
        ('Pre-School','Pre-School'),
        ('PK (Kg1)','PK (Kg1)'),
        ('K (Kg2)','K (Kg2)'),
        ('Grade 1','Grade 1'),
        ('Grade 2','Grade 2'),
        ('Grade 3','Grade 3'),
        ('Grade 4','Grade 4'),
        ('Grade 5','Grade 5'),
    )

    code = models.CharField(max_length=7, unique=True)
    username = models.CharField(max_length=60,verbose_name='Name')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES, blank=True)
    grade = models.CharField( max_length=16, choices=GRADE_CHOICES, blank=True)
    father_mobile = models.CharField(max_length=14, null=True, blank=True,verbose_name='موبيل الاب ')
    mother_mobile = models.CharField(max_length=13, null=True, blank=True,verbose_name='موبيل الام ')
    phone_number = models.CharField(max_length=13, null=True, blank=True,verbose_name='تليفون المنزل ')
    email = models.EmailField(max_length=60, null=True, blank=True)
    year = models.CharField( max_length=5,choices=YEAR_CHOICES, default=current_year)
    # study_payment1 = models.PositiveIntegerField(default=0,verbose_name='Study 1')
    # study_payment2 = models.PositiveIntegerField(default=0,verbose_name='Study 2')
    # study_payment3 = models.PositiveIntegerField(default=0,verbose_name='Study 3')
    # study_payment4 = models.PositiveSmallIntegerField(default=0,verbose_name='Study 4')
    discount = models.PositiveIntegerField(default=0)
    old_fee = models.IntegerField(default=0)
    bus_active = models.BooleanField( default=False)
    # bus_payment1 = models.PositiveIntegerField( default=10000,verbose_name='Bus 1')
    # bus_payment2 = models.PositiveSmallIntegerField( default=0,verbose_name='Bus 2')
    total_paid = models.IntegerField(default=0)
    old_paid = models.IntegerField( default=0)

    # def payment_status(self):
    #     if date.today() < date(2024,2,1):
    #         if self.bus_active == True:
    #             return self.study_payment1 + self.study_payment2 + self.study_payment3 + self.study_payment4 + self.bus_payment1 + self.bus_payment2 - self.total_paid - self.discount + self.old_fee - self.old_paid
    #         else:
    #             return self.study_payment1 + self.study_payment2 + self.study_payment3 + self.study_payment4 - self.total_paid - self.discount + self.old_fee - self.old_paid
            
    #     elif date.today() >= date(2024,2,1):
    #         if self.bus_active == True:
    #             return self.study_payment1 + self.study_payment2 + self.study_payment3 + self.study_payment4 + self.bus_payment1 + self.bus_payment2 - self.total_paid - self.discount + self.old_fee - self.old_paid
    #         else:
    #             return self.study_payment1 + self.study_payment2 + self.study_payment3 + self.study_payment4 - self.total_paid - self.discount + self.old_fee - self.old_paid

    # payment_status

    living_area = models.ForeignKey(BusLocation, on_delete=models.SET_NULL, null=True, blank=True,verbose_name='المنطقة السكنية ')
    address = models.CharField( max_length=86,null=True,blank=True,verbose_name='العنوان ')
    old_bus = models.CharField( max_length=4,null=True,blank=True,verbose_name='رقم سيارة العام السابق ')
    bus_number = models.ForeignKey(Bus, on_delete=SET_NULL,null=True, blank=True,verbose_name='رقم السيارة ')
    bus_order = models.CharField(max_length=5,null=True,blank=True,verbose_name='موعد الركوب ')
    bus_notes = models.CharField(max_length=24, null=True, blank=True,verbose_name='نوع الاشتراك ')
    message = models.CharField(max_length=260, null=True, blank=True)

    books  = models.BooleanField(default=False)
    total_books = models.SmallIntegerField( default=0,verbose_name='Total Books')
    is_active = models.BooleanField(default=True)
    can_pay = models.BooleanField(default=True)
    is_admin  = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_employ = models.BooleanField(default=False)
    lms_code = models.CharField(max_length=9,null=True,blank=True)
    pay_books = models.BooleanField(default=False)
    bus_discount = models.PositiveIntegerField(default=0)
    is_golden = models.BooleanField(default=False)
    all_books = models.BooleanField(default=False)
    pay_tours = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)
    # is_superuser field provided by PermissionsMixin
    # groups field provided by PermissionsMixin
    # user_permissions field provided by PermissionsMixin

    objects = StudentManager()

    USERNAME_FIELD = 'code'
    REQUIRED_FIELDS = ['username',]

    # class Meta:
    #     verbose_name='student'
    #     verbose_name_plural ='حسابات الطلاب '

    @property
    def payment_status(self):
        """
        Calculates the remaining balance for a student using optimized fee lookups.
        """
        total_study_fees = 0
        total_bus_fees = 0

        # --- Get Study Fees (Optimized) ---
        try:
            fee_details = SchoolFee.objects.get(
                school=self.school,
                grade=self.grade,
                year=self.year
            )
            # Read the pre-calculated total directly from the model
            total_study_fees = fee_details.total_study_fees
        except SchoolFee.DoesNotExist:
            pass # total_study_fees remains 0

        # --- Get Bus Fees from BusLocation ---
        if self.bus_active and self.living_area:
            # Assumes your BusLocation model has a 'bus_fee' field
            total_bus_fees = self.living_area.total_bus_fees - self.bus_discount
        
        # --- Calculate Final Balance ---
        remaining_balance = (
            total_study_fees +
            total_bus_fees -
            self.total_paid -
            self.discount +
            self.old_fee -
            self.old_paid
        )
        
        return remaining_balance
    
    def __str__(self):
        return self.username + " " + self.code
    # # def __str__(self):
    # #     return self.code
    #
    #
    def has_perm(self, perm, obj=None):
        return self.is_admin
        # return True

    def has_module_perms(self, app_label):
        return True

class BusStudent(Student):
    class Meta:
        proxy = True
        verbose_name='student'
        verbose_name_plural ='اشتركات الطلاب '

class SchoolFee(models.Model):
    school = models.CharField( max_length=8)
    grade = models.CharField( max_length=16)
    study_payment1 = models.PositiveIntegerField(default=0,verbose_name='Study 1')
    study_payment2 = models.PositiveIntegerField(default=0,verbose_name='Study 2')
    study_payment3 = models.PositiveIntegerField(default=0,verbose_name='Study 3')
    study_payment4 = models.PositiveIntegerField(default=0,verbose_name='Study 4')
    # New field to store the calculated total
    total_study_fees = models.PositiveIntegerField(default=0, editable=False) # editable=False hides it from the admin form
    bus_payment1 = models.PositiveIntegerField( default=10000,verbose_name='Bus 1')
    bus_payment2 = models.PositiveIntegerField( default=0,verbose_name='Bus 2')
    study_fee = models.PositiveIntegerField(default=0)
    activity_fee = models.PositiveSmallIntegerField(default=0)
    computer_fee = models.PositiveSmallIntegerField(default=0)
    books_all = models.PositiveSmallIntegerField(default=0)
    books_books = models.PositiveSmallIntegerField(default=0)
    books_booklet = models.PositiveSmallIntegerField(default=0)
    books_a_level = models.PositiveSmallIntegerField(default=0)
    books_fee = models.PositiveSmallIntegerField(default=0)
    bus_fee = models.PositiveIntegerField(default=0)
    year = models.CharField( max_length=5,choices=YEAR_CHOICES,default='25-24')
    study_payment1_date = models.DateField(null=True,verbose_name='Study 1 Date')
    study_payment2_date = models.DateField(null=True,verbose_name='Study 2 Date')
    study_payment3_date = models.DateField(null=True,verbose_name='Study 3 Date')
    study_payment4_date = models.DateField(null=True,verbose_name='Study 4 Date')
    bus_payment1_date = models.DateField(null=True,verbose_name='Bus 1 Date')
    bus_payment2_date = models.DateField(null=True,verbose_name='Bus 2 Date')
    books_activate_value = models.PositiveIntegerField(default=0)
    tour_name = models.CharField(max_length=24, null=True, blank=True)
    tour_value = models.PositiveSmallIntegerField(default=0)
    tour_active = models.BooleanField(default=False)
    books_1 = models.PositiveIntegerField(default=0, verbose_name='Book Set 1')
    books_2 = models.PositiveIntegerField(default=0, verbose_name='Book Set 2')
    book_1 = models.PositiveIntegerField(default=0, verbose_name='Books 1')
    book_2 = models.PositiveIntegerField(default=0, verbose_name='books 2')
    boklet_1 = models.PositiveIntegerField(default=0, verbose_name='Booklets 1')
    boklet_2 = models.PositiveIntegerField(default=0, verbose_name='Booklets 2')
    boknot_1 = models.PositiveIntegerField(default=0, verbose_name='Notebook 1')
    boknot_2 = models.PositiveIntegerField(default=0, verbose_name='Notebook 2')
    boklan_1 = models.PositiveIntegerField(default=0, verbose_name='Languages Books 1')
    boklan_2 = models.PositiveIntegerField(default=0, verbose_name='Languages Books 2')
    bokalv_1 = models.PositiveIntegerField(default=0, verbose_name='A-Level Books 1')
    bokalv_2 = models.PositiveIntegerField(default=0, verbose_name='A-Level Books 2')

    def save(self, *args, **kwargs):
        # Automatically calculate the total before saving
        self.total_study_fees = self.study_payment1 + self.study_payment2 + self.study_payment3 + self.study_payment4
        super().save(*args, **kwargs) # Call the original save method
            
    def __str__(self):
        return self.grade + " ( " + self.school + " )" + " " + str(self.year)
        
    class Meta:
        verbose_name='Fee'
        verbose_name_plural ='School Fees  '


class OtherFee(models.Model):
    KIND_CHOICES = (
        ('Tours','Tours'),
        ('Other','Other')
    )
    name = models.CharField(max_length=100)
    value = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=6, choices=KIND_CHOICES, default='Tours')
    is_active = models.BooleanField(default=True)
    # Relate to multiple SchoolFee and Class instances
    school_fee = models.ForeignKey(SchoolFee, on_delete=models.SET_NULL, null=True, blank=True)
    classes = models.ManyToManyField('student_affairs.Class', related_name='other_fees')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES_2)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name='Other Fee'
        verbose_name_plural ='School Other Fees  '

class Program(models.Model):
    name = models.CharField(max_length=16)
    code = models.CharField(max_length=16)
    count = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return self.name

class Manager(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    level = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.username
    
class Archive(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    school = models.CharField( max_length=8)
    study_year = models.CharField( max_length=5)
    code = models.CharField(max_length=7)
    grade = models.CharField( max_length=16)
    study = models.PositiveIntegerField(default=0)
    bus = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    total = models.IntegerField(default=0)
    old_fee = models.IntegerField(default=0)
    old_paid = models.IntegerField(default=0)
    
    def year_status(self):
        return (self.total + self.old_paid + self.discount) - (self.study + self.bus + self.old_fee)
    
    year_status
    
    def __str__(self):
        return self.student.username

    class Meta:
        verbose_name='study_year'
        verbose_name_plural ='Old Years'