from django.shortcuts import render,redirect
from .models import Student,Contact,Application
from .forms import ContactData,ContactContact,ApplicationForm

def contact(request):
        if request.method == 'GET':
            msg = request.session.get('msg')
            request.session['msg'] = ''
            error = request.session.get('error')
            request.session['error'] = ''

            student = Student.objects.get(code=request.user.code)
            try:
                contact = Contact.objects.get(student=student)
                context = {
                'msg':msg,
                'error':error,
                'form':ContactContact(instance=contact),
                 }
            except Contact.DoesNotExist:
                context = {
                    'msg':msg,
                    'error':error,
                    'form':ContactData(instance=student),
                }
            return render(request, 'student_affairs/contact.html',context)

        else:
            try:
                student = Student.objects.get(code=request.user.code)
                if student.father_mobile != request.POST['father_mobile'] or student.mother_mobile != request.POST['mother_mobile'] :
                    phone_update = True
                else:
                    phone_update = False
                if student.address_1 != request.POST['address']:
                    address_update = True
                else:
                    address_update = False
                try:
                    contact = Contact.objects.get(student=student)
                    contact.father_mobile = request.POST['father_mobile']
                    contact.mother_mobile = request.POST['mother_mobile']
                    contact.phone_number = request.POST['phone_number']
                    contact.email = request.POST['email']
                    contact.address_1 = request.POST['address']
                    contact.phone_update = phone_update
                    contact.address_update = address_update
                    contact.save()
                except Contact.DoesNotExist:
                    contact = Contact(
                        student=student,
                        father_mobile = request.POST['father_mobile'],
                        mother_mobile = request.POST['mother_mobile'],
                        phone_number = request.POST['phone_number'],
                        email = request.POST['email'],
                        address_1 = request.POST['address'],
                        school = request.user.school,
                        phone_update = phone_update,
                        address_update = address_update,
                    )
                    contact.save()
                student.contact_status = True
                student.save()
                request.session['msg'] = 'تم استلام البيانات وسيتم التعديل بعد المراجعة'
                return redirect('dashboard')
            except ValueError:
                    request.session['error'] = 'برجاء إدخال البيانات بشكل صحيح'
                    return redirect('contact')
            
def application(request):
        if request.method == 'GET':
            msg = request.session.get('msg')
            request.session['msg'] = ''
            error = request.session.get('error')
            request.session['error'] = ''
            context = {
                'msg':msg,
                'error':error,
                'form':ApplicationForm(),
            }
            return render(request, 'student_affairs/application.html',context)

        else:
            try:
                student = Student.objects.get(code=request.user.code)
                application = Application(
                    student=student,
                    school = request.user.school,
                    father_id = request.POST['father_id'],
                    father_job = request.POST['father_job'],
                    father_mobile = request.POST['father_mobile'],
                    email = request.POST['email'],
                    mother_job = request.POST['mother_job'],
                    mother_mobile = request.POST['mother_mobile'],
                    email2 = request.POST['email2'],
                    phone_number = request.POST['phone_number'],
                    phone_number2 = request.POST['phone_number2'],
                    address_1 = request.POST['address_1'],
                    student_order = request.POST['student_order'],
                    parents_status = request.POST['parents_status'],
                    student_with = request.POST['student_with'],
                    sos_name1 = request.POST['sos_name1'],
                    sos_phone1 = request.POST['sos_phone1'],
                    sos_name2 = request.POST['sos_name2'],
                    sos_phone2 = request.POST['sos_phone2'],
                    brother1_name = request.POST['brother1_name'],
                    brother2_name = request.POST['brother2_name'],
                    brother3_name = request.POST['brother3_name'],
                    brother4_name = request.POST['brother4_name'],
                    brother1_grade = request.POST['brother1_grade'],
                    brother2_grade = request.POST['brother2_grade'],
                    brother3_grade = request.POST['brother3_grade'],
                    brother4_grade = request.POST['brother4_grade'],

                )
                application.save()
                student.application_status = True
                student.save()
                request.session['msg'] = 'تم استلام البيانات وسيتم التعديل بعد المراجعة'
                return redirect('dashboard')
            except ValueError:
                    request.session['error'] = 'برجاء إدخال البيانات بشكل صحيح'
                    return redirect('contact')
            
def nile_application(request):
        if request.method == 'GET':
            msg = request.session.get('msg')
            request.session['msg'] = ''
            error = request.session.get('error')
            request.session['error'] = ''
            context = {
                'msg':msg,
                'error':error,
                'form':ApplicationForm(),
            }
            return render(request, 'student_affairs/application.html',context)

        else:
            try:
                student = Student.objects.get(code=request.user.code)
                if student.school == request.user.school == "بنين":
                     new_school = 'Nile-b'
                else:
                     new_school = 'Nile-g'
                
                application = Application(
                    student=student,
                    school = new_school,
                    father_id = request.POST['father_id'],
                    father_job = request.POST['father_job'],
                    father_mobile = request.POST['father_mobile'],
                    email = request.POST['email'],
                    mother_job = request.POST['mother_job'],
                    mother_mobile = request.POST['mother_mobile'],
                    email2 = request.POST['email2'],
                    phone_number = request.POST['phone_number'],
                    phone_number2 = request.POST['phone_number2'],
                    address_1 = request.POST['address_1'],
                    student_order = request.POST['student_order'],
                    parents_status = request.POST['parents_status'],
                    student_with = request.POST['student_with'],
                    sos_name1 = request.POST['sos_name1'],
                    sos_phone1 = request.POST['sos_phone1'],
                    sos_name2 = request.POST['sos_name2'],
                    sos_phone2 = request.POST['sos_phone2'],
                    brother1_name = request.POST['brother1_name'],
                    brother2_name = request.POST['brother2_name'],
                    brother3_name = request.POST['brother3_name'],
                    brother4_name = request.POST['brother4_name'],
                    brother1_grade = request.POST['brother1_grade'],
                    brother2_grade = request.POST['brother2_grade'],
                    brother3_grade = request.POST['brother3_grade'],
                    brother4_grade = request.POST['brother4_grade'],

                )
                application.save()
                student.nile_transfers = True
                student.save()
                request.session['msg'] = 'تم استلام البيانات وسيتم التعديل بعد المراجعة'
                return redirect('dashboard')
            except ValueError:
                    request.session['error'] = 'برجاء إدخال البيانات بشكل صحيح'
                    return redirect('contact')
