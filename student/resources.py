# from asyncio.windows_events import NULL
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from fees.models import Fee
from .models import Student,Bus,Archive
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_str
from import_export.results import RowResult
from django.db.models import F
from student_affairs.models import School, Class, Student as StudentAff

class FeesResource(resources.ModelResource):
    student = fields.Field(column_name='student',
                      attribute='student',
                      widget=ForeignKeyWidget(Student, 'code'))

    # def get_row_result_class(self):
    #     """
    #     Returns the class used to store the result of a row import.
    #     """
    #     return RowResult

    # delete = fields.Field(widget=BooleanWidget())
    # def for_delete(self, row, instance):
    #     row_result = self.get_row_result_class()
    #     row_result.object_id = instance.pk
    #     row_result.object_repr = force_str(instance)
    #     return self.fields['delete'].clean(row)

    def before_import_row(self,row, **kwargs):
        if row['verified']==True:
            mystudent = Student.objects.get(code=row['student'])
            SYear = mystudent.year
            if row['year'] == SYear:
                if row['kind'][:3] == 'Boo':
                    mystudent.total_books = F('total_books')+row['value']
                    if row['value'] > 0:
                        mystudent.books = True
                    else:
                        mystudent.books = False
                elif row['kind'][:3] == 'Bok':
                    mystudent.total_books = F('total_books')+row['value']
                elif row['kind'] == 'دراسية':
                    mystudent.total_paid = F('total_paid')+row['value']
                    try:
                        mystudentAff = StudentAff.objects.get(code=mystudent.code)
                        mystudentAff.payment_status = True
                        mystudentAff.save()
                    except StudentAff.DoesNotExist:
                        pass
                elif row['kind'] == 'سيارة':
                    mystudent.total_paid = F('total_paid')+row['value']
                    mystudent.bus_active = True
                mystudent.save()
            else:
                try:
                    archive = Archive.objects.get(code=row['student'],study_year=row['year'])
                    archive.total = F('total')+row['value']
                    archive.save()
                except Archive.DoesNotExist:
                    pass

    class Meta:
        model = Fee
        import_id_fields = ('id',)
        fields = ('id', 'student', 'student__username', 'school', 'student__grade', 'value', 'kind', 'bank_account','created','payment_date','year', 'verified')
        export_order = ('id', 'student', 'student__username', 'school', 'student__grade', 'value', 'kind', 'bank_account','created','payment_date','year', 'verified')

class StudentResource(resources.ModelResource):
    # if 'password' in self.fields.keys():
    def get_row_result_class(self):
        """
        Returns the class used to store the result of a row import.
        """
        return resources.RowResult
    
    def for_delete(self, row, instance):
        return row.get("delete") == "1"

    # delete = fields.Field(widget=BooleanWidget())
    # def for_delete(self, row, instance):
    #     row_result = self.get_row_result_class()
    #     row_result.object_id = instance.pk
    #     row_result.object_repr = force_str(instance)
    #     return self.fields['delete'].clean(row)

    def before_import_row(self,row, **kwargs):
        value = row['password']
        row['password'] = make_password(value)

    class Meta:
        model = Student
        import_id_fields = ('code',)
        fields = ('year','code','username', 'password','school','grade','study_payment1','study_payment2','study_payment3','bus_payment1', 'bus_payment2','old_fee', 'old_paid', 'discount','total_paid','message','is_active', 'can_pay', 'bus_active', 'father_mobile', 'mother_mobile', 'phone_number', 'email', 'living_area', 'address', 'old_bus','books','total_books','lms_code','pay_tours','pay_books','all_books','is_golden')
        export_order = ('year','code','username', 'password','school','grade','study_payment1','study_payment2','study_payment3','bus_payment1', 'bus_payment2','old_fee', 'old_paid', 'discount','total_paid','message','is_active', 'can_pay', 'bus_active', 'father_mobile', 'mother_mobile', 'phone_number', 'email', 'living_area', 'address', 'old_bus','books','total_books','lms_code','pay_tours','pay_books','all_books','is_golden')

class StudentAffResource(resources.ModelResource):
    Class = fields.Field(column_name='Class',
                      attribute='Class',
                      widget=ForeignKeyWidget(Class, 'name'))

    # if 'password' in self.fields.keys():
    # def get_row_result_class(self):
    #     """
    #     Returns the class used to store the result of a row import.
    #     """
    #     return RowResult

    # delete = fields.Field(widget=BooleanWidget())
    # def for_delete(self, row, instance):
    #     row_result = self.get_row_result_class()
    #     row_result.object_id = instance.pk
    #     row_result.object_repr = force_str(instance)
    #     return self.fields['delete'].clean(row)

    def before_import_row(self, row, **kwargs):
        if not row['code']:
            code_gen = []
            if row['school'] == "بنين" or row['school'] == "Nile-b":
                code_gen.append('2')
                myschool = School.objects.get(school="بنين")
            elif row['school'] == "Alfarouk":
                code_gen.append('1')
                myschool = School.objects.get(school="Alfarouk")
            else:
                myschool = School.objects.get(school="بنات")
                code_gen.append('3')
            code_gen.append(row['study_year'][3:])
            myschool.count += 1
            code_gen.append(format(myschool.count, '04'))
            myschool.save()
            row['code'] = ''.join(code_gen)

        # value = row['password']
        # row['password'] = make_password(value)

    class Meta:
        model = StudentAff
        import_id_fields = ('code',)
        fields = ('code','study_year','school','grade','Class','status','status_no','name','en_name','student_id','birth_date','age1oct','birth_gov','kind','nationality','address_1','phone_number','phone_number2',
        'mother_mobile','father_mobile','email','father_id','father_name','father_job','mother_name','mother_job','mother_id','payment_status','global_code','document_status','contact_status','application_status','is_over','notes','admission_id','nile_transfers')
        export_order = ('code','study_year','school','grade','Class','status','status_no','name','en_name','student_id','birth_date','age1oct','birth_gov','kind','nationality','address_1','phone_number','phone_number2',
        'mother_mobile','father_mobile','email','father_id','father_name','father_job','mother_name','mother_job','mother_id','payment_status','global_code','document_status','contact_status','application_status','is_over','notes','admission_id','nile_transfers')

class BusStudentResource(resources.ModelResource):

    bus_number = fields.Field(column_name='bus_number',
                    attribute='bus_number',
                    widget=ForeignKeyWidget(Bus, 'number'))
    
    class Meta:
        model = Student
        import_id_fields = ('code',)
        fields = ('code','username','school','grade','bus_number','bus_active', 'father_mobile', 'mother_mobile', 'phone_number', 'email', 'living_area', 'address', 'old_bus','bus_order','bus_notes')
        export_order = ('code','username','school','grade','bus_number','bus_active', 'father_mobile', 'mother_mobile', 'phone_number', 'email', 'living_area', 'address', 'old_bus','bus_order','bus_notes')