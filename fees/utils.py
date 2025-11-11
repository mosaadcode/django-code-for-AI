from django.contrib import messages
from django.utils.translation import ngettext
from django.db.models import F
from student.models import Student,Archive
from student_affairs.models import Student as StudentAff


SCHOOL_PAYMENT_MAPPING = {
    "بنين": {
        "Books": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f722fd66d9fe090369e"
        },
        "Study Fees": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9d9fe090369e"
        },
        "Tours": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9dfe090369e"
        },
        "Other": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9de90f3735a66d9fe090369e"
        },
        "Bus Fees": {
            "bank_account": "1903530635939300017",
            "api_token": "08a1fb199f0915a484c882baf3b574bbdb0ce"
        },
        # Add more mappings as needed
    },
    "Nile-b": {
        "Books": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4b090369e"
        },
        "Study Fees": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9d90369e"
        },
        "Tours": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9de90e090369e"
        },
        "Other": {
            "bank_account": "1903530354880500015",
            "api_token": "04449625f72d0ac4bab9de90f3e090369e"
        },
        "Bus Fees": {
            "bank_account": "1903530635939300017",
            "api_token": "08a1fb199f09574bbdb0ce"
        },
        # Add more mappings as needed
    },
    "Nile-g": {
        "Books": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d4386a6e15f9f9d9efd"
        },
        "Study Fees": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c095f9f9d9efd"
        },
        "Tours": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c0976e15f9f9d9efd"
        },
        "Other": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c0978e7cf9f9d9efd"
        },
        "Bus Fees": {
            "bank_account": "1903530635939300017",
            "api_token": "08a1fb199f0915a484c882ba1f3b574bbdb0ce"
        },
        # Add more mappings as needed
    },
    "بنات": {
        "Books": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c09e15f9f9d9efd"
        },
        "Study Fees": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c0978ee15f9f9d9efd"
        },
        "Tours": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c0978e7c2e15f9f9d9efd"
        },
        "Other": {
            "bank_account": "1903530635939400011",
            "api_token": "f4b6b33d43872c0978e15f9f9d9efd"
        },
        "Bus Fees": {
            "bank_account": "1903530635939300017",
            "api_token": "08a1fb199f0915a484c3b574bbdb0ce"
        },
        # Add more mappings as needed
    },
    # Add more schools as needed
}

def payment_route(school, kind):
    """
    Retrieve the bank account and API token for a given school and kind of payment.
    """
    school_mapping = SCHOOL_PAYMENT_MAPPING.get(school)
    if school_mapping:
        return school_mapping.get(kind, {})
    return {}


def verify_fees(request, queryset, log_changes=False, admin_instance=None):
    updated = 0
    notupdated = 0
    cannot = 0

    for obj in queryset:
        if not obj.verified:
            mystudent = Student.objects.get(id=obj.student_id)
            SYear = mystudent.year

            if obj.year == SYear:
                # for book and book
                if obj.kind[:3] == 'Boo':
                    mystudent.total_books = F('total_books') + obj.value
                    mystudent.books = obj.value > 0
                elif obj.kind[:3] == 'Bok':
                    mystudent.total_books = F('total_books') + obj.value
                elif obj.kind == 'دراسية':
                    mystudent.total_paid = F('total_paid') + obj.value
                    # update student affairs
                    try:
                        mystudentAff = StudentAff.objects.get(code=mystudent.code)
                        mystudentAff.payment_status = True
                        mystudentAff.save()
                    except StudentAff.DoesNotExist:
                        pass
                elif obj.kind == 'سيارة':
                    mystudent.total_paid = F('total_paid') + obj.value
                    mystudent.bus_active = True

                mystudent.save()
                obj.verified = True
                obj.save()
                if log_changes and admin_instance:
                    admin_instance.log_change(request, obj, 'verified')
                updated += 1
            else:
                if obj.kind in ['سيارة', 'دراسية']:
                    try:
                        archive = Archive.objects.get(code=mystudent.code, study_year=obj.year)
                        archive.total = F('total') + obj.value
                        archive.save()
                    except Archive.DoesNotExist:
                        pass
                obj.verified = True
                obj.save()
                if log_changes and admin_instance:
                    admin_instance.log_change(request, obj, 'verified')
                updated += 1
        else:
            notupdated += 1

    # Only show messages if log_changes is True
    if log_changes and admin_instance:
        if updated != 0:
            admin_instance.message_user(request, ngettext(
                '%d fee was successfully verified.',
                '%d fees were successfully verified.',
                updated,
            ) % updated, messages.SUCCESS)
        if notupdated != 0:
            admin_instance.message_user(request, ngettext(
                '%d fee was already verified before.',
                '%d fees were already verified before.',
                notupdated,
            ) % notupdated, messages.ERROR)
        if cannot != 0:
            admin_instance.message_user(request, ngettext(
                '%d fee needs year check.',
                '%d fees need year check.',
                cannot,
            ) % cannot, messages.ERROR)

