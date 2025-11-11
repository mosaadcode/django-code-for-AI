from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.signals import post_save
from student.models import Student as StudentAcc, SchoolFee
from datetime import date,timedelta
from django.contrib.auth.hashers import make_password

current_year = '26-25'

SCHOOL_CHOICES = (
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

class School(models.Model):
    school = models.CharField(max_length=8, choices=SCHOOL_CHOICES)
    count = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.school+" "+str(self.count)

class Governorate(models.Model):
    name = models.CharField(max_length=36)
    # class Meta:
    #     verbose_name='governorate'
    #     verbose_name_plural ='المحافظات والاقسام والمراكز '
    def __str__(self):
        return self.name

class Nationality(models.Model):
    name = models.CharField(max_length=11)
    # class Meta:
    #     verbose_name='nationality'
    #     verbose_name_plural ='الجنسيات '
    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=11)
    class Meta:
        verbose_name='class'
        verbose_name_plural =' الفصول الدراسية'
    def __str__(self):
        return self.name

class Class_group(models.Model):
    name = models.CharField(max_length=6)
    class Meta:
        verbose_name='group'
        verbose_name_plural =' مجموعات الفصول'
    def __str__(self):
        return self.name


class Student(models.Model):

    STATUS_CHOICES = (
        # (None, ""),
        ('مستجد', 'مستجد'),
        ('منقول', 'منقول'),
        ('باقي', 'باقي للإعادة'),
        ('محول', 'محول'),
        ('محول من', 'محول من'),
        ('عائد','عائد'),
        ('وافد','وافد'),
    )
    GRADE_CHOICES = (
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

    RELIGION_CHOICES = (
        ('مسلم','مسلم'),
        ('مسيحي','مسيحي'),
    )

    RESPONSIBILITY_CHOICES = (
        ('الاب','الاب'),
        ('الام','الام'),
        ('الاب والام','الاب والام'),
    )    

    OVER_CHOICES =(
        ('No',''),
        ('ضابط','ضابط'),
        ('وزير','وزير'),
        ('بعثات','بعثات'),
    )   

    KIND_CHOICES = (
        ('ذكر','ذكر'),
        ('اُنثى','اُنثى'),
    )
    code = models.CharField(max_length=7, unique=True,blank=True,verbose_name='الكود ')
    global_code = models.CharField(max_length=9,blank=True,null=True,verbose_name='كود الوزارة ')
    name = models.CharField(max_length=60,verbose_name='إسم الطالب ')
    en_name = models.CharField(max_length=60, blank=True, null=True,verbose_name='الإسم بالانجلزية ')
    kind = models.CharField(max_length=5,choices=KIND_CHOICES,blank=True,null=True,verbose_name='النوع ')
    student_id = models.CharField(max_length=14, blank=True, null=True,verbose_name='رقم قومي ')
    status = models.CharField( max_length=7, choices=STATUS_CHOICES,blank=True,null=True,default='مستجد',verbose_name='حالة القيد ')
    status_no = models.CharField(max_length=7, blank=True, null=True,verbose_name='رقم القيد ')
    from_to = models.CharField(max_length=32,blank=True,null=True,verbose_name='')
    study_year = models.CharField( max_length=5, default = current_year,verbose_name='العام الدراسي ')
    start_year = models.CharField( max_length=5,blank=True,null=True,verbose_name='سنة الالتحاق ')
    school = models.CharField( max_length=8, choices=SCHOOL_CHOICES,verbose_name='المدرسة ')
    grade = models.CharField( max_length=16, choices=GRADE_CHOICES,verbose_name='الصف ')
    start_grade = models.CharField( max_length=16, null=True,blank=True, choices=GRADE_CHOICES,verbose_name='صف الإلتحاق ')
    Class = models.ForeignKey(Class,on_delete=models.SET_NULL, null=True,blank=True,verbose_name='الفصل ')
    group = models.ForeignKey(Class_group,on_delete=models.SET_NULL, null=True,blank=True,verbose_name='المجموعة ')
    religion = models.CharField(max_length=5,choices=RELIGION_CHOICES,default='مسلم',blank=True,null=True,verbose_name='الديانة ')
    nationality = models.ForeignKey(Nationality,on_delete=SET_NULL, blank=True,null=True,verbose_name='الجنسية ')
    is_over = models.CharField( max_length=5, choices=OVER_CHOICES,null=True,default='',verbose_name='فوق الكثافة ')
    birth_date = models.DateField(null=True,blank=True, verbose_name='تاريخ الميلاد ')
    birth_gov = models.ForeignKey(Governorate,on_delete=SET_NULL, null=True,blank=True,verbose_name='محل الميلاد ')
    age1oct = models.CharField(default="",max_length=8,null=True,blank=True,verbose_name='(يوم- شهر- سنة) العمر اول اكتوبر ')
    father_name = models.CharField(max_length=46,null=True, blank=True,verbose_name='إسم الاب ')
    father_job = models.CharField(max_length=60,null=True, blank=True,verbose_name='الوظيفة ')
    father_id = models.CharField(max_length=14, null=True,blank=True,verbose_name='رقم قومي ')
    mother_name = models.CharField(max_length=46, null=True,blank=True,verbose_name='إسم الام ')
    mother_job = models.CharField(max_length=60,null=True, blank=True,verbose_name='الوظيفة ')
    mother_id = models.CharField(max_length=14, null=True,blank=True,verbose_name='رقم قومي ')
    responsibility = models.CharField(max_length=11,choices=RESPONSIBILITY_CHOICES,default='الاب والام',blank=True,null=True,verbose_name='الولاية التعليمية ')    
    father_mobile = models.CharField(max_length=14, null=True,blank=True,verbose_name='هاتف الاب ')
    mother_mobile = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف الام ')
    phone_number = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف المنزل ')
    phone_number2 = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف بديل ')
    address_1 = models.CharField( max_length=86,null=True,blank=True,verbose_name='العنوان ')
    # address_2 = models.CharField( max_length=64,null=True,blank=True,verbose_name='العنوان البديل ')
    email = models.EmailField(max_length=60, blank=True,null=True)
    notes = models.TextField( max_length=250,null=True,blank=True,verbose_name='ملاحظات ')
    payment_status = models.BooleanField(default=False,verbose_name='حالة السداد ')
    document_status = models.BooleanField(default=False,verbose_name=' تم تقديم الأوراق   ')
    contact_status = models.BooleanField(default=True,verbose_name='   تم تحديث بيانات التواصل ')
    application_status = models.BooleanField(default=False,verbose_name='   تم فتح الملف ')
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    admission_id = models.PositiveIntegerField(blank=True,null=True)
    nile_transfers = models.BooleanField(default=False,verbose_name='   تحويل النيل ')


    def __str__(self):
        return self.name + " " + self.code

    def get_code(self):
        if self.code == "":
            code_gen = []
            if self.school == "بنين":
                code_gen.append('2')
            elif self.school == "Alfarouk":
                code_gen.append('1')
            else:
                code_gen.append('3')
            code_gen.append(self.study_year[3:])
            if self.school == ".بنات.":
                myschool = School.objects.get(school="بنات")
            else:
                myschool = School.objects.get(school=self.school)
            myschool.count +=1
            code_gen.append(format(myschool.count,'04'))
            myschool.save()
            return ''.join(code_gen)


    # def myage(self):
    #     if self.birth_date !=None:
    #         ret = []
    #         age = date(2021,10,1) - self.birth_date
    #         num_years = int(age.days / 365.2425)
    #         if num_years >= 0:
    #             age -= timedelta(days=num_years * 365.2425)
    #             num_years = format(num_years,'02')
    #             ret.append(num_years)
    #         num_months = int(age.days / 30.436875)
    #         if num_months >= 0:
    #             age -= timedelta(days=num_months * 30.436875)
    #             num_months = format(num_months,'02')
    #             ret.append(num_months)
    #         if age.days >= 0:
    #             days = format(age.days,'02')
    #             ret.append(days)
    #         return '-'.join(ret)
    #     return ""
    
    # def brothers(self):
    #     return Student.objects.filter(father_id=self.father_id).count()-1


    def save(self, *args, **kwargs):
        if self.code == "":
            self.code = self.get_code()
        # self.age1oct = self.myage()
        if self.start_year == "":
            self.start_year = self.study_year
        super().save(*args, **kwargs)

    class Meta:
        verbose_name='student'
        verbose_name_plural ='    سجلات الطلاب'

class Archive(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=7,verbose_name='الكود ')
    study_year = models.CharField( max_length=5,verbose_name='العام الدراسي ')
    school = models.CharField( max_length=6,verbose_name='المدرسة ')
    grade = models.CharField( max_length=16,verbose_name='الصف ')
    status = models.CharField( max_length=7,verbose_name='حالة القيد ')

    def __str__(self):
        return self.student.name

    class Meta:
        verbose_name='study_year'
        verbose_name_plural ='ارشيف السنوات السابقة'

class Contact(models.Model):
    SCHOOL1_CHOICES = (
        ('بنين', 'بنين'),
        ('بنات', 'بنات'),
        ('.بنات.', '.بنات.'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    father_mobile = models.CharField(max_length=14, null=True,blank=True,verbose_name='هاتف الاب ')
    mother_mobile = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف الام ')
    phone_number = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف المنزل ')
    email = models.EmailField(max_length=60, blank=True,null=True)
    address_1 = models.CharField( max_length=86,null=True,blank=True,verbose_name='العنوان ')
    school = models.CharField( max_length=6, choices=SCHOOL1_CHOICES, blank=True)
    phone_update = models.BooleanField(default=False,verbose_name='تحديث الهاتف')
    address_update = models.BooleanField(default=False,verbose_name='تحديث العنوان')

    def __str__(self):
        return self.student.name

    class Meta:
        verbose_name='contact'
        verbose_name_plural ='   تحديث بيانات تواصل'

class Application(models.Model):
    PARENTS_CHOICES = (
        ('معاً', 'معاً'),
        ('منفصلان', 'منفصلان'),
        ('بالخارج', 'بالخارج'),
        ('أحدهما متوفى', 'أحدهما متوفى'),
    )

    ORDER_CHOICES = [(i, i) for i in range(1, 9)]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    school = models.CharField( max_length=6,verbose_name='المدرسة ')
    father_id = models.CharField(max_length=14, null=True,blank=True,verbose_name=' رقم الأب القومي ')
    father_job = models.CharField(max_length=46,null=True, blank=True,verbose_name='وظيفة الأب ')
    mother_job = models.CharField(max_length=46,null=True, blank=True,verbose_name='وظيفة الاَم ')
    father_mobile = models.CharField(max_length=14, null=True,blank=True,verbose_name='هاتف الأب ')
    mother_mobile = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف الاَم ')
    phone_number = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف المنزل ')
    phone_number2 = models.CharField(max_length=13, null=True,blank=True,verbose_name='هاتف بديل ')
    address_1 = models.CharField( max_length=86,null=True,blank=True,verbose_name='العنوان بالتفصيل')
    email = models.EmailField(max_length=36, blank=True,null=True,verbose_name='ايميل الأب ')
    email2 = models.EmailField(max_length=36, blank=True,null=True,verbose_name='ايميل الاَم ')
    student_with = models.CharField(max_length=12,null=True,verbose_name='يتواجدالطالب مع ')
    student_order = models.PositiveSmallIntegerField(choices=ORDER_CHOICES,null=True,verbose_name='الترتيب بين الإخوة ')
    parents_status = models.CharField(max_length=12,choices=PARENTS_CHOICES,default='معاً',null=True,verbose_name='الوالدين ')
    sos_name1 = models.CharField(max_length=46,null=True,verbose_name='الإسم ')
    sos_phone1 = models.CharField(max_length=13,null=True,verbose_name='الهاتف ')
    sos_name2 = models.CharField(max_length=46,null=True,verbose_name='الإسم ')
    sos_phone2 = models.CharField(max_length=13,null=True,verbose_name='الهاتف ')
    brother1_name  = models.CharField(max_length=46,verbose_name='الإسم ')
    brother1_grade = models.CharField( max_length=16, choices=Student.GRADE_CHOICES,verbose_name='الصف ')
    brother2_name  = models.CharField(max_length=46,verbose_name='الإسم ')
    brother2_grade = models.CharField( max_length=16, choices=Student.GRADE_CHOICES,verbose_name='الصف ')
    brother3_name  = models.CharField(max_length=46,verbose_name='الإسم ')
    brother3_grade = models.CharField( max_length=16, choices=Student.GRADE_CHOICES,verbose_name='الصف ')
    brother4_name  = models.CharField(max_length=46,verbose_name='الإسم ')
    brother4_grade = models.CharField( max_length=16, choices=Student.GRADE_CHOICES,verbose_name='الصف ')
    created = models.DateTimeField(auto_now_add=True,null=True)
    done = models.BooleanField(default=False,verbose_name='تم التحويل ')

    def __str__(self):
        return self.student.name

    class Meta:
        verbose_name='application'
        verbose_name_plural ='   تحديث ملفات'

def create_student(sender, instance, created, **kwargs):
    if created:
        if instance.code[0] != "C":
            # if instance.school == ".بنات.":
            #     GradeFee = SchoolFee.objects.get(school="بنات",grade=instance.grade,year=instance.study_year)
            # else:
            #     GradeFee = SchoolFee.objects.get(school=instance.school,grade=instance.grade,year=instance.study_year)
            StudentAcc.objects.create(
                code=instance.code,
                username=instance.name,
                password=make_password(instance.code),
                school=instance.school,
                grade=instance.grade,
                year=instance.study_year,
                father_mobile=instance.father_mobile,
                mother_mobile=instance.mother_mobile,
                phone_number=instance.phone_number,
                address=instance.address_1,
                email=instance.email,
                # study_payment1=GradeFee.study_payment1,
                # study_payment2=GradeFee.study_payment2,
                # study_payment3=GradeFee.study_payment3,
                # study_payment4=GradeFee.study_payment4,
                # bus_payment1=GradeFee.bus_payment1,
                # bus_payment2=GradeFee.bus_payment2,
                )
post_save.connect(create_student, sender=Student)

def update_student(sender, instance, created, **kwargs):
    if created ==False:
        # if instance.school == ".بنات.":
        #     GradeFee = SchoolFee.objects.get(school="بنات",grade=instance.grade,year=instance.study_year)
        # elif instance.school[0] != 'O':
        #     GradeFee = SchoolFee.objects.get(school=instance.school,grade=instance.grade,year=instance.study_year)
        if instance.school[0] != 'O' and instance.status != 'محول من':
            studentacc = StudentAcc.objects.get(code=instance.code)
            studentacc.username=instance.name
            studentacc.school=instance.school
            studentacc.grade=instance.grade
            studentacc.year=instance.study_year
            studentacc.father_mobile=instance.father_mobile
            studentacc.mother_mobile=instance.mother_mobile
            studentacc.phone_number=instance.phone_number
            studentacc.email=instance.email
            # studentacc.living_area=None
            studentacc.address=instance.address_1
            # studentacc.study_payment1=GradeFee.study_payment1
            # studentacc.study_payment2=GradeFee.study_payment2
            # studentacc.study_payment3=GradeFee.study_payment3
            # studentacc.study_payment4=GradeFee.study_payment4
            # studentacc.bus_payment1=GradeFee.bus_payment1
            # studentacc.bus_payment2=GradeFee.bus_payment2

            if studentacc.bus_active == False:
                studentacc.save(update_fields=["username", "school", "grade", "year","father_mobile", 
                "mother_mobile", "phone_number", "email", "address"])
            else:
                studentacc.save(update_fields=["username", "school", "grade", "year","father_mobile", 
                "mother_mobile", "phone_number", "email"])

post_save.connect(update_student, Student)