from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from .models import MonthN as Month,SalaryItem,Employee,Permission,School,Job,Employee_month,Time_setting,Permission_setting,Vacation_setting,Department
from import_export.results import RowResult
from operator import attrgetter
try:
    active_month = Month.objects.get(active=True)
except Month.DoesNotExist:
    active_month = None

class SalaryItemResource(resources.ModelResource):
    employee = fields.Field(column_name='employee',
                      attribute='employee',
                      widget=ForeignKeyWidget(Employee, 'code'))

    def before_import_row(self,row, **kwargs):
        if row['month']==None:
            row['month'] = active_month
        return row

    class Meta:
        model = SalaryItem
        import_id_fields = ('id',)
        fields = ('id','school','employee','item','value','month')
        export_order = ('id','school','employee','item','value','month')

class EmployeeResource(resources.ModelResource):

    def get_row_result_class(self):
        """
        Returns the class used to store the result of a row import.
        """
        return RowResult

    def for_delete(self, row, instance):
        return row.get("delete") == "1"
        
    permission_setting = fields.Field(column_name='permission_setting',
                      attribute='permission_setting',
                      widget=ForeignKeyWidget(Permission_setting, 'name'))
    
    vacation_setting = fields.Field(column_name='vacation_setting',
                      attribute='vacation_setting',
                      widget=ForeignKeyWidget(Vacation_setting, 'name'))
    
    def before_import_row(self, row, **kwargs):
        if not row['code']:
            code_gen = []
            row['na_id'] = str(row['na_id'])
            code_gen.append(row['na_id'][1:3])
            if row['school'] == "بنين":
                code_gen.append('b')
                myschool = School.objects.get(school='بنين')
            elif row['school'] in ('Ig', 'بنات'):   
                code_gen.append('g')
                myschool = School.objects.get(school=row['school'])
            elif row['school'] == 'Alfarouk':
                code_gen.append('a')
                myschool = School.objects.get(school='Alfarouk')
            elif row['school'] == 'FIS':
                code_gen.append('f')
                myschool = School.objects.get(school='FIS') 
            myschool.count += 1
            code_gen.append(format(myschool.count, '04'))
            myschool.save()
            row['code'] = ''.join(code_gen)

    class Meta:
        model = Employee
        import_id_fields = ('code',)
        fields = ('code', 'school', 'name', 'na_id', 'birth_date', 'mobile_number', 'phone_number', 'emergency_phone', 'email', 'address', 'basic_certificate', 'is_educational', 'attendance_date', 'insurance_date', 'participation_date', 'contract_date', 'insurance_no', 'notes', 'job', 'is_active', 'salary_parameter', 'salary', 'message', 'time_code', 'permission_setting', 'vacation_setting','manager1','manager2')
        export_order = ('code', 'school', 'name', 'na_id', 'birth_date', 'mobile_number', 'phone_number', 'emergency_phone', 'email', 'address', 'basic_certificate', 'is_educational', 'attendance_date', 'insurance_date', 'participation_date', 'contract_date', 'insurance_no', 'notes', 'job', 'is_active', 'salary_parameter', 'salary', 'message', 'time_code', 'permission_setting', 'vacation_setting','manager1','manager2')



class PermResource(resources.ModelResource):
    employee = fields.Field(column_name='employee',
                      attribute='employee',
                      widget=ForeignKeyWidget(Employee, 'code'))
    
    month = fields.Field(column_name='month',
                    attribute='month',
                    widget=ForeignKeyWidget(Month, 'code'))

    def before_import_row(self,row, **kwargs):
        if row['month']==None:
            row['month'] = active_month
        return row

    class Meta:
        model = Permission
        import_id_fields = ('id',)
        fields = ('id','school','employee','date','type','ok1','ok2','month')
        export_order = ('id','school','employee','date','type','ok1','ok2','month')

class Employee_monthResource(resources.ModelResource):
    employee = fields.Field(column_name='employee',
                      attribute='employee',
                      widget=ForeignKeyWidget(Employee, 'code'))
    
    month = fields.Field(column_name='month',
                      attribute='month',
                      widget=ForeignKeyWidget(Month, 'code'))
    
    # print(employee)
    # print(month)

    def before_import_row(self,row, **kwargs):
        if row['month']==None:
            row['month'] = active_month
        return row

    class Meta:
        model = Employee_month
        import_id_fields = ('id',)
        fields = ('id','school','employee','permissions','vacations','salary_value','is_active','month')
        export_order = ('id','school','employee','permissions','vacations','salary_value','is_active','month')

class Time_settingResource(resources.ModelResource):

    name = fields.Field(column_name='name',
                      attribute='name',
                      widget=ForeignKeyWidget(Vacation_setting, 'name'))
    
    month = fields.Field(column_name='month',
                      attribute='month',
                      widget=ForeignKeyWidget(Month, 'code'))
    
    class Meta:
        model = Time_setting
        import_id_fields = ('id',)      
        fields = ('id','name','month','date','time_in','time_in_perm','time_out', 'time_out_perm')
        export_order = ('id','name','month','date','time_in','time_in_perm','time_out', 'time_out_perm')
    
    def export(self, queryset=None, *args, **kwargs):
        queryset = self.get_queryset() if queryset is None else queryset
        # sorted_queryset = sorted(queryset, key=attrgetter('name','date'))
        sorted_queryset = queryset.order_by('name', 'date')
        return super().export(sorted_queryset, *args, **kwargs)
    
class JobResource(resources.ModelResource):
    department = fields.Field(column_name='department',
                    attribute='department',
                    widget=ForeignKeyWidget(Department, 'name'))
    class Meta:
        model = Job
        import_id_fields = ('id',)
        fields = ('type','title','department','grade','id')
        export_order = ('type','title','department','grade','id')