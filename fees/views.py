from django.shortcuts import render, redirect
from .forms import FeesForm
from .models import Fee
from student.forms import StudentForm, StudentArea, fis_StudentArea
from student_affairs.models import Student as StudentAff    
from student.models import Archive ,SchoolFee , OtherFee
import json
import requests
import logging
from datetime import datetime
from .utils import payment_route, verify_fees
from django.db.models import Sum
from django.db import transaction

last_year = '25-24'
current_year = '25-24'
next_year = '26-25'

def payment_status(payments, total_paid, discount=0):
    statuses = []
    remaining_paid = total_paid + discount  # Add discount to total_paid
    for payment in payments:
        if remaining_paid >= payment:
            statuses.append({"status": "Complete", "remaining": 0})
            remaining_paid -= payment
        elif remaining_paid > 0:
            statuses.append({"status": "Partial", "remaining": payment - remaining_paid})
            remaining_paid = 0
        else:
            statuses.append({"status": "Not Complete", "remaining": payment})
    return statuses

def dashboard(request):
    try:
        OldVale = Archive.objects.get(code=request.user.code, study_year=last_year).year_status()
        OldVale = int(OldVale)
        oldSign = -1 if OldVale < 0 else 1 if OldVale > 0 else 0
        OldVale = abs(OldVale)
    except Archive.DoesNotExist:
        oldSign = 0
        OldVale = 0
    student = request.user
    school = student.school
    grade = student.grade
    student_year = student.year
    schoolfee = SchoolFee.objects.get(school=student.school, grade=student.grade, year=student.year)
    studentaff = StudentAff.objects.get(code=request.user.code)
    student_class = studentaff.Class
    living_area = student.living_area
    is_golden = student.is_golden
    all_books = student.all_books

    if studentaff.grade not in ('الاول الابتدائى', 'الاول الاعدادى', 'الاول الثانوى') and not studentaff.contact_status:
        request.session['error'] = 'برجاء تحديث بيانات التواصل'
        return redirect('contact')

    # Get student discount
    student_discount = student.discount or 0
    student_bus_discount = student.bus_discount or 0
    # Calculate total paid fees
    study_total_paid = Fee.objects.filter(student=student, year=student_year, kind='دراسية', verified=True).aggregate(Sum('value'))['value__sum'] or 0
    bus_total_paid = Fee.objects.filter(student=student, year=student_year, kind='سيارة', verified=True).aggregate(Sum('value'))['value__sum'] or 0
    tour_total_paid = Fee.objects.filter(student=student, year=student_year, kind='Tours', verified=True).aggregate(Sum('value'))['value__sum'] or 0

    # Get desired payments from schoolfee
    study_payments = [
        schoolfee.study_payment1,
        schoolfee.study_payment2,
        schoolfee.study_payment3,
        schoolfee.study_payment4
    ]
    study_payments = [payment for payment in study_payments if payment != 0]

    if living_area:
        bus_payments = [living_area.payment1, living_area.payment2]
    else:
        bus_payments = [0, 0]  # Or whatever default values you want
    bus_payments = [payment for payment in bus_payments if payment != 0]

    books_total = schoolfee.books_all
    
    tour = schoolfee.tour_active

    study_total_payments = sum(study_payments)
    bus_total_payments = sum(bus_payments)

    # Get payment statuses
    # study_payment_statuses = payment_status(study_payments, study_total_paid, 0 if is_golden else student_discount)
    study_payment_statuses = payment_status(study_payments, study_total_paid, student_discount)
    bus_payment_statuses = payment_status(bus_payments, bus_total_paid, student_bus_discount)

    # Prepare payment data for template
    study_payment_data = []
    for i, (status, payment) in enumerate(zip(study_payment_statuses, study_payments), start=1):
        payment_date = getattr(schoolfee, f'study_payment{i}_date')
        study_payment_data.append({
            'status': status['status'],
            'remaining': status['remaining'],
            'date': payment_date,
            'amount': payment,
            'number': i
        })

    bus_payment_data = []
    for i, (status, payment) in enumerate(zip(bus_payment_statuses, bus_payments), start=1):
        payment_date = getattr(schoolfee, f'bus_payment{i}_date')
        bus_payment_data.append({
            'status': status['status'],
            'remaining': status['remaining'],
            'date': payment_date,
            'amount': payment,
            'number': i
        })

    # Calculate study_total due amount
    # study_total_due = study_total_payments - study_total_paid - (0 if is_golden else student_discount)
    study_total_due = study_total_payments - study_total_paid - student_discount
    study_total_due = max(study_total_due, 0)  # Ensure total_due is not negative

    # Calculate bus_total due amount
    bus_total_due = bus_total_payments - bus_total_paid - student_bus_discount
    bus_total_due = max(bus_total_due, 0)  # Ensure total_due is not negative
    book_paid = student.books
    pay_books = student.pay_books

    # Calculate threshold values
    books_condition_2 = sum(study_payments[:2])
    books_condition_3 = sum(study_payments[:3])

    # Determine required condition based on school and golden status
    if student.school in ('FIS', 'Nile-b', 'Nile-g'):
        required_condition = books_condition_2 if student.is_golden else books_condition_3
    else:
        required_condition = books_condition_2

    # Check if payment meets the requirement
    books = study_total_paid + student_discount >= required_condition


    if student.bus_active == True and bus_total_due > 0 : books = False
    if pay_books == True : books = True

    # Get all book-related fees in a single query
    book_fees = Fee.objects.filter(
        student=student, 
        year=student_year, 
        kind__startswith='Bo',  # Filter for book-related kinds
        verified=True
    ).values('kind').annotate(total_paid=Sum('value'))

    # Convert to a dictionary for easier access
    book_paid_dict = {fee['kind']: fee['total_paid'] for fee in book_fees}

    # Define book types and their corresponding payment fields
    book_types_config = [
        {'key': 'Books', 'name': 'الكتب كاملة', 'payment_fields': ['books_1', 'books_2']},
        {'key': 'Book', 'name': 'كتب الوزارة', 'payment_fields': ['book_1', 'book_2']},
        {'key': 'Boklet', 'name': 'ملازم', 'payment_fields': ['boklet_1', 'boklet_2']},
        {'key': 'BokNot', 'name': 'كراسات', 'payment_fields': ['boknot_1', 'boknot_2']},
        {'key': 'BokLan', 'name': 'كتب لغات', 'payment_fields': ['boklan_1', 'boklan_2']},
        {'key': 'BokAlv', 'name': 'كتاب A-Level', 'payment_fields': ['bokalv_1', 'bokalv_2']}
    ]

    book_types = []

    # Special logic for "Alfarouk" school when all_books is False
    if school == "Alfarouk" and not all_books:
        for config in book_types_config:
            # Get payments for this book type
            payments = []
            for field in config['payment_fields']:
                payment_amount = getattr(schoolfee, field, 0)
                if payment_amount > 0:
                    payments.append(payment_amount)
            
            # Only proceed if there are required payments for this book type
            if payments:
                paid_amount = book_paid_dict.get(config['key'], 0)
                
                # **APPLY NEW FILTERING RULES**
                # 1. Always include 'Book' (كتب الوزارة) if it has a payment amount.
                # 2. For all other types, include only if there is a payment amount AND a paid amount.
                if (
                    config['key'] in ('Book', 'BokNot') or
                    paid_amount > 0 
                    # or (config['key'] == 'BokLan' and grade in ("ثانية حضانة", "الاول الابتدائى", "الثانى الابتدائى", "الثالث الابتدائى", "الرابع الابتدائى", "الخامس الابتدائى", "السادس الابتدائى"))
                ):
                    total_payments = sum(payments)
                    
                    # Get payment statuses
                    payment_statuses = payment_status(payments, paid_amount, 0)
                    
                    # Prepare payment data for template
                    payment_data = []
                    for i, (status, payment) in enumerate(zip(payment_statuses, payments), start=1):
                        payment_data.append({
                            'status': status['status'],
                            'remaining': status['remaining'],
                            'amount': payment,
                            'number': i,
                            'paid_amount': payment - status['remaining'] if status['status'] == 'Partial' else payment
                        })
                    
                    # Calculate total due
                    total_due = max(total_payments - paid_amount, 0)
                    
                    # Add to book types list
                    book_types.append({
                        'name': config['name'],
                        'key': config['key'],
                        'payment_data': payment_data,
                        'total_payments': total_payments,
                        'total_paid': paid_amount,
                        'total_due': total_due,
                    })

    # Original logic for all other students/cases
    else:
        for config in book_types_config:
            # Get payments for this book type
            payments = []
            for field in config['payment_fields']:
                payment_amount = getattr(schoolfee, field, 0)
                if payment_amount > 0:
                    payments.append(payment_amount)
            
            # Only include book types with payments > 0
            if payments:
                total_payments = sum(payments)
                paid_amount = book_paid_dict.get(config['key'], 0)
                
                # Get payment statuses
                payment_statuses = payment_status(payments, paid_amount, 0)
                
                # Prepare payment data for template
                payment_data = []
                for i, (status, payment) in enumerate(zip(payment_statuses, payments), start=1):
                    payment_data.append({
                        'status': status['status'],
                        'remaining': status['remaining'],
                        'amount': payment,
                        'number': i,
                        'paid_amount': payment - status['remaining'] if status['status'] == 'Partial' else payment
                    })
                
                # Calculate total due
                total_due = max(total_payments - paid_amount, 0)
                
                # Add to book types list
                book_types.append({
                    'name': config['name'],
                    'key': config['key'],
                    'payment_data': payment_data,
                    'total_payments': total_payments,
                    'total_paid': paid_amount,
                    'total_due': total_due,
                })   


    # Get active OtherFee instances relevant to the student
    relevant_other_fees = OtherFee.objects.filter(
        is_active=True,
        classes=student_class,  # Adjust based on your student-class relationship
        school_fee=schoolfee
    ).distinct()
    # Process Other Fees
    other_fees_data = []
    tours_fees_data = []

    for other_fee in relevant_other_fees:
        # Check if this OtherFee is already paid
        is_paid = Fee.objects.filter(
            student=student,
            year=next_year,
            # reference=f'fee_{other_fee.id}',  # Unique identifier for each OtherFee
            reference=other_fee.id,
            verified=True
        ).exists()
        
        fee_data = {
            'name': other_fee.name,
            'value': other_fee.value,
            'reference': other_fee.id,
            'is_paid': is_paid,
            'kind': other_fee.kind,
        }
        
        # Separate fees by type for conditional display
        if other_fee.kind == 'Tours':
            tours_fees_data.append(fee_data)
        else:  # 'Other' type
            other_fees_data.append(fee_data)

    context = {
        'bus': len(str(request.user.living_area)) > 4,
        'msg': request.session.pop('msg', ''),
        'error': request.session.pop('error', ''),
        'oldSign': oldSign,
        'OldVale': OldVale,
        'nile_transfers': studentaff.nile_transfers,
        'schoolfee': schoolfee,
        'last_year': last_year,
        'current_year':current_year,
        'student_year': student_year,
        'next_year':next_year,
        'study_payment_data': study_payment_data,
        'bus_payment_data': bus_payment_data,
        'study_total_paid': study_total_paid,
        'bus_total_paid': bus_total_paid,
        'student_discount': student_discount,
        'student_bus_discount': student_bus_discount,
        'study_total_payments':study_total_payments,
        'bus_total_payments':bus_total_payments,
        'study_total_due': study_total_due,
        'bus_total_due': bus_total_due,
        'books_total' : books_total,
        'book_paid' : book_paid,
        'books': books,
        'tour': tour,
        'tour_total_paid':tour_total_paid,
        'is_golden': is_golden,
        'school': school,

        'book_types': book_types,

        'other_fees_data': other_fees_data,
        'tours_fees_data': tours_fees_data,
        'student_pay_tours': student.pay_tours
    }
    if school == 'FIS':
        return render(request, 'fees/fis_dashboard.html', context)
   
    return render(request, 'fees/dashboard2.html', context)

def addfees(request):
    if request.method == 'GET':   
        msg = request.session.get('msg')
        return render(request, 'fees/addfees.html', {'form':FeesForm(),'msg':msg})     
    else:
        try:
            LYFee = Archive.objects.get(code=request.user.code,study_year=last_year).year_status()
            LYFee=int(LYFee)
            if LYFee < 0 :
                LYFee = LYFee *-1
            else:
                LYFee = 0
          
        except Archive.DoesNotExist:
            LYFee = 0

        if request.user.can_pay == True:
            if request.POST['kind'] == "دراسية":
                # add try: except to solve value Error
                try:
                    form = FeesForm(request.POST)
                    newfee = form.save(commit=False)
                    newfee.student = request.user
                    newfee.school = request.user.school

                    SYear=request.user.year
                    if LYFee >0:
                        if int(request.POST['value']) <= LYFee:
                            newfee.year = last_year
                            newfee.save()
                        else:
                            newfee.value = LYFee
                            newfee.year = last_year
                            newfee.save()
                            form2 = FeesForm(request.POST)
                            newfee2 = form2.save(commit=False)
                            newfee2.student = request.user
                            newfee2.school = request.user.school
                            newfee2.value = int(request.POST['value']) - LYFee
                            newfee2.year = SYear
                            newfee2.save()
                    else:        
                        newfee.year = SYear
                        newfee.save()
                    # update student data
                    # request.user.total_paid += int(request.POST['value'])
                    # request.user.save(update_fields=["total_paid"])
                    # redirect user to currenttodos page
                    return redirect('recorded')
                except ValueError:
                        # tell user when error hapen
                        return render(request, 'fees/addfees.html', {'form':FeesForm(),'error':'برجاء مراجعة بيانات الايصال'})
            else:
                if len(str(request.user.living_area)) > 4 :
                    # add try: except to solve value Error
                    try:
                        form = FeesForm(request.POST)
                        newfee = form.save(commit=False)
                        newfee.student = request.user
                        newfee.school = request.user.school
                        LYFee = request.user.old_fee - request.user.old_paid
                        SYear=request.user.year
                        # if LYFee >0:
                        #     if int(request.POST['value']) <= LYFee:
                        #         newfee.year = '22-21'
                        #         newfee.save()
                        #     else:
                        #         newfee.value = LYFee
                        #         newfee.year ='22-21'
                        #         newfee.save()
                        #         form2 = FeesForm(request.POST)
                        #         newfee2 = form2.save(commit=False)
                        #         newfee2.student = request.user
                        #         newfee2.school = request.user.school
                        #         newfee2.value = int(request.POST['value']) - LYFee
                        #         newfee2.year = SYear
                        #         newfee2.save()
                        # else:        
                        newfee.year = SYear
                        newfee.save()
                        request.session['msg'] = ''
                        return redirect('recorded')
                    except ValueError:
                            # tell user when error hapen
                            return render(request, 'fees/addfees.html', {'form':FeesForm(),'error':'برجاء مراجعة البيانات'})
                else:
                    error = ' يجب اولاً الاطلاع على تعليمات اشتراك السيارة في الاعلى ثم تحديد المنطقة السكنية والعنوان '
                    request.session['error'] = error
                    return redirect('agreement')

        else:
            return render(request, 'fees/addfees.html', {'form':FeesForm(),'error':'لا يمكنك التسجيل الان, برجاء مراجعة قسم الحسابات'})
        
def recorded(request):
    fees = Fee.objects.filter(student=request.user.id,year=request.user.year,kind__in = ('دراسية','سيارة','Books')).exclude(school__in=('Out-b', 'Out-g')).order_by('payment_date')
    return render(request, 'fees/recorded.html',{'fees':fees})


def agreement(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    school = request.user.school

    if request.method == 'GET':
        error = request.session.pop('error', None)
        if school == 'FIS':
            form = fis_StudentArea(instance=request.user)  # Pre-fill with user data
            return render(request, 'fees/fis_agreement.html', {'form': form, 'error': error})
        else:
            form = StudentArea(instance=request.user)  # Pre-fill with user data
            return render(request, 'fees/agreement.html', {'form': form, 'error': error})
    
    else:
        if not school == 'FIS':  # POST request
            form = StudentArea(request.POST, instance=request.user)
            
            if not request.user.bus_number:  # Only allow if user doesn't have a bus assigned
                if form.is_valid():
                    try:
                        form.save()  # This will update living_area and address
                        request.session['error'] = ''
                        msg = 'تم استلام الطلب ولن يتم الاشتراك الا بعد الاتصال مباشرة مع قسم الباصات للتأكد من وجود اماكن شاغرة في منطقتك السكنية ' 
                        request.session['msg'] = msg
                        return redirect('dashboard')
                    except Exception as e:
                        # Log the error for debugging
                        print(f"Error saving form: {e}")
                        error = 'حدث خطأ أثناء حفظ البيانات. يرجى المحاولة مرة أخرى'
                        return render(request, 'fees/agreement.html', {'form': form, 'error': error})
                else:
                    # Form is invalid - show errors
                    return render(request, 'fees/agreement.html', {'form': form, 'error': 'برجاء مراجعة البيانات'})
            else:
                error = 'لا يمكن تغيير العنوان المسجل قبل التواصل مباشرة مع إدارة تشغيل السيارات'
                return render(request, 'fees/agreement.html', {'form': form, 'error': error})
        else:
            form = fis_StudentArea(request.POST, instance=request.user)
            if form.is_valid():
                try:
                    form.save()  # This will update living_area and address
                    request.session['error'] = ''
                    msg = 'The application has been registered'
                    request.session['msg'] = msg
                    return redirect('dashboard')
                except Exception as e:
                    # Log the error for debugging
                    print(f"Error saving form: {e}")
                    error = 'An error occurred while saving data. Please try again.'
                    return render(request, 'fees/fis_agreement.html', {'form': form, 'error': error})
            else:
                error ='The registered address cannot be changed without directly contacting the Bus Operations Department.'
                return render(request, 'fees/fis_agreement.html', {'form': form, 'error': error})

def Pay_online(request):
    if request.method == "POST":
        try:
            # Retrieve payment details based on school and kind
            value = int(request.POST.get('value').replace(',', ''))
            year = request.POST.get('year')
            school = request.user.school
            kind = request.POST.get('kind')
            reference = request.POST.get('reference')
            payment_details = payment_route(school, kind)

            # Ensure we have a valid mapping for the bank account and token
            if not payment_details:
                return render(request, 'fees/payment_failed.html', {'error': 'Invalid school or payment type.'})
            
            bank_account = payment_details['bank_account']
            api_token = payment_details['api_token']
            # Store the API token in the session
            request.session['api_token'] = api_token

            # Prepare the payment data

            payment_data = {
                "payment_method_id": 2,
                "cartTotal": value,
                "currency": "EGP",
                "customer": {
                    "first_name": request.user.code,
                    "last_name": request.user.username,
                    "email": '',
                    "phone": '',
                    "address": '',
                },
                "redirectionUrls": {
                    "successUrl": "https://mfis.online/fee/payment-response/",
                    "failUrl": "https://mfis.online/fee/fail/",
                    "pendingUrl": "https://mfis.online/pending/"
                },
                "discountData": {
                    "type": "literal",
                    "value": 0
                },
                "cartItems": [
                    {
                        "name": kind,
                        "price": value,
                        "quantity": 1
                    }
                ],
                "payLoad": {
                    "school": school,
                    "year": year,
                    "kind": kind,
                    "bank_account": bank_account,
                    "reference": reference
                }
            }

            # Make the payment request
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                url="https://app.fawaterk.com/api/v2/invoiceInitPay",
                headers=headers,
                data=json.dumps(payment_data)
            )

            # Handle the payment response
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("status") == "success":
                    invoice_id = response_data['data']['invoice_id']
                    redirect_url = response_data['data']['payment_data']['redirectTo']
                    return redirect(redirect_url)
                else:
                    return render(request, 'fees/payment_failed.html', {'error': 'Payment initiation failed.'})

            else:
                return render(request, 'fees/payment_failed.html', {'error': 'Payment failed. Please try again.'})

        except Exception as e:
            return render(request, 'fees/payment_failed.html', {'error': f'An error occurred: {str(e)}'})

def handle_payment_response(request):
    invoice_id = request.GET.get("invoice_id")
    
    if not invoice_id:
        return redirect('fail_page')

    # Retrieve the api_token from the session
    api_token = request.session.get("api_token")
    

    # Call getInvoiceData to check the payment status
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    invoice_url = f"https://app.fawaterk.com/api/v2/getInvoiceData/{invoice_id}"
    response = requests.get(invoice_url, headers=headers)


    # Log the entire response to check what's returned
    invoice_data = response.json()
    logging.info(f"Invoice Data Response: {invoice_data}")

    # Process the invoice data response
    if response.status_code == 200:
        # Check if the payment status is 'paid' or transaction status is 'Success'
        status_text = invoice_data['data'].get("status_text", "").lower()
        transaction_status = invoice_data['data']['invoice_transactions'][0].get("status", "").lower()

        if status_text == "paid" or transaction_status == "success":
            paid_at_str = invoice_data['data'].get("paid_at", None)
            invoice_key = invoice_data['data'].get("invoice_key")
            
            # Extract pay_load and parse it as JSON
            pay_load_str = invoice_data['data'].get("pay_load", "{}")
            pay_load = json.loads(pay_load_str)  # Convert the JSON string to a dictionary

            # Define kind mappings
            kind_mappings = {
                "Study Fees": "دراسية",
                "Bus Fees": "سيارة",
                "Tours": "Tours",  # Keep as is
                "Other": "Other",
                "Books": "Books",
                "Book": "Book",  # Keep as is
                "Boklet": "Boklet",
                "BokNot": "BokNot",
                "BokLan": "BokLan",
                "BokAlv": "BokAlv"
            }

            # Retrieve 'kind' from pay_load and map it to the desired value
            raw_kind = pay_load.get("kind", "Study Fees")  # Default to 'Study Fees' if not found
            kind = kind_mappings.get(raw_kind, raw_kind)  # Use the mapping if available, else keep the original

            bank_account = pay_load.get("bank_account", "")
            reference= pay_load.get("reference", "")
            year = pay_load.get("year", request.user.year)  # Use user's year if not found
            try:
                # Convert the 'paid_at' string to a Python date object
                if paid_at_str:
                    payment_date = datetime.strptime(paid_at_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                else:
                    payment_date = None

                value = invoice_data['data'].get("total", 1000)  # Use the total value from the invoice

                # Ensure atomicity in fee creation
                with transaction.atomic():
                    # Generate the invoice link
                    invoice_link = f"https://app.fawaterk.com/invoice/{invoice_id}/{invoice_key}"

                    if not Fee.objects.filter(invoice_link=invoice_link).exists():
                        # Create the new fee in the Fee model
                        fee = Fee.objects.create(
                            student=request.user,
                            value=value,
                            year=year,
                            bank_account=bank_account,
                            kind=kind,
                            payment_date=payment_date,
                            school=request.user.school,
                            invoice_link=invoice_link,  # Store the invoice link
                            reference=reference
                        )

                        # Automatically verify the new fee
                        verify_fees(request, Fee.objects.filter(id=fee.id), log_changes=False)
                
                request.session.update({'msg': 'تمت عملية الدفع بنجاح'})

                return redirect('dashboard')  # Redirect to a success page

            except ValueError as e:
                logging.error(f"Date parsing error: {e}")
                return render(request, 'fees/payment_failed.html', {'error': 'Invalid payment date format.'})
            
        else:
            logging.error(f"Payment status is not successful: {status_text} / {transaction_status}")
            # Payment was not successful
            return redirect('fail_page')
    else:
        logging.error(f"Failed to fetch invoice data: {response.status_code}")
        # If there's an error in fetching invoice data
        return render(request, 'fees/payment_failed.html', {'error': 'Unable to verify payment status.'})
    




def success_page(request):
    return redirect('recorded')

def fail_page(request):
    request.session.update({'error': 'لم تتم عملية الدفع, يرجي التأكد من البيانات'})
    return redirect('dashboard')

def pending_page(request):
    return render(request, 'fees/pending.html')
