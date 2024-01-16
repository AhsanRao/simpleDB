from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib import messages
from .models import *
from django.db import IntegrityError
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q

from django.contrib.auth.decorators import login_required, permission_required

from .models import *

def index(request):

  context = {
    'segment'  : 'index',
    #'products' : Product.objects.all()
  }
  return render(request, "pages/dashboard.html", context)

def staff_dashborad(request):

  context = {
    'segment'  : 'staff-dashborad',
  }
  return render(request, "pages/staff.html", context)

def tables(request):
  context = {
    'segment': 'tables'
  }
  return render(request, "pages/dynamic-tables.html", context)

def person(request):
  context = {
    'segment': 'person'
  }
  return render(request, "pages/adduser.html", context)

from django.views.decorators.csrf import csrf_exempt

@login_required
@permission_required('home.add_person', raise_exception=True)
def add_user(request):
    if request.method == 'POST':
        try:
            # Get data from form
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            gender = request.POST['gender']
            email = request.POST['email']
            role = request.POST['role']

            street = request.POST['street']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            country = request.POST['country']

            home_phone = request.POST['home_phone']
            business_phone = request.POST['business_phone']

            # Create and save the new Person object
            person = Person(
                first_name=first_name, last_name=last_name, gender=gender, 
                email=email, role=role, street=street, city=city, 
                state=state, zipcode=zipcode, country=country, 
                home_phone_number=home_phone, business_phone_number=business_phone
            )
            person.save()

            messages.success(request, 'User added successfully!')
            return redirect('add_user')  
        except IntegrityError as e:
            error_message = str(e)
            # Check for unique constraint on the email field
            if "Duplicate entry" in error_message and "for key 'email'" in error_message:
                messages.error(request, "Email already in use. Please use a different email.", extra_tags='info')
            else:
                messages.error(request, "A database error occurred. Please try again.", extra_tags='error')

        except Exception as e:
            messages.error(request, "An unexpected error occurred: " + str(e))

    # If GET request or form is invalid, render the form with any existing data
    context = {
        'form_data': request.POST or None,
        'segment': 'add-user'
    }
    return render(request, 'pages/adduser.html', context)

@login_required
def add_equipment(request):
    if request.method == 'POST':
        try:
            # Extract data from the form
            asset_tag_number = request.POST.get('asset_tag_number')
            equipment_name = request.POST.get('equipment_name')
            serial_number = request.POST.get('serial_number')
            install_date = request.POST.get('install_date') 

            # Convert the install_date string to a datetime object
            install_date_obj = datetime.strptime(install_date, '%Y-%m-%d').date()

            # Create new instance of Equipment
            new_equipment = Equipment(
                asset_tag_number=asset_tag_number, 
                equipment_name=equipment_name, 
                serial_number=serial_number, 
                install_date=install_date_obj
            )
            new_equipment.save()

            messages.success(request, 'Equipment added successfully!')
            return redirect('add_equipment') 

        except IntegrityError as e:
            error_message = str(e)
            # Check for unique constraint on the asset_tag_number field
            if "Duplicate entry" in error_message and "for key 'asset_tag_number'" in error_message:
                messages.error(request, "Asset Tag Number or Serial Number already in use. Please use different values.", extra_tags='info')
            else:
                messages.error(request, "A database error occurred. Please try again.", extra_tags='error')

        except ValueError as e:
            # This block catches errors like incorrect date format
            messages.error(request, f"An error occurred: {e}")

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    # If GET request or form is invalid, render the form with any existing data
    context = {
        'form_data': request.POST or None,
        'segment': 'add-equipment'
    }
    return render(request, 'pages/addequipment.html', context)

@login_required
def add_contract(request):
  if request.method == 'POST':
      try:
          # Extract contract data from form
          installation_date = request.POST.get('installation_date')
          monthly_charges = request.POST.get('monthly_charges')
          billing_date = request.POST.get('billing_date')
          renewal_date = request.POST.get('renewal_date')

          # Fetch client details
          email = request.POST.get('email')
          client = Person.objects.filter(email=email, role="Client").first()

          if not client:
              messages.error(request, 'Client not found.')

          # Fetch salesperson details
          semail = request.POST.get('sale_email')
          print(semail)
          salesperson = Person.objects.filter(email=semail).exclude(role="Client").first()

          if not salesperson:
              messages.error(request, 'Salesperson not found.')

          # Fetch equipment details
          tag = request.POST.get('asset_tag_number')
          equipment = Equipment.objects.filter(asset_tag_number=tag).first()

          if not equipment:
              messages.error(request, 'Equipment not found.')

          # Create and add a new contract
          new_contract = Contract(
              installation_date=datetime.strptime(installation_date, '%Y-%m-%d').date(),
              monthly_charges=monthly_charges,
              billing_date=datetime.strptime(billing_date, '%Y-%m-%d').date(),
              renewal_date=datetime.strptime(renewal_date, '%Y-%m-%d').date(),
              role=salesperson.role,
              person=salesperson,
          )
          new_contract.save()

          # Create and add a new entry in contract_equipments table
          new_contract_equipment = ContractEquipment(
              contract=new_contract,
              equipment=equipment,
              person=client
          )
          new_contract_equipment.save()

          messages.success(request, 'Contract created successfully!')
          return redirect('add_contract')  

      except IntegrityError as e:
          messages.error(request, 'A database error occurred. Please try again.', extra_tags='info')

      except ValueError as e:
          messages.error(request, 'Invalid date format. Please check the provided information.', extra_tags='info')

      except Exception as e:
          messages.error(request, 'Record not added. Please try again.', extra_tags='info')
  
      # Render the form with existing data in case of an error
      context = {
          'form_data': request.POST or None,
          'segment': 'add_contract'
      }
      return render(request, 'pages/addcontract.html', context)

    # If GET request, render the form with empty context
  return render(request, 'pages/addcontract.html', {'segment': 'add-contract'})

@login_required
def search_user(request):
    email = request.GET.get('email')
    user = Person.objects.filter(email=email, role="Client").first()
    if user:
        return JsonResponse({
            'success': True,
            'full_name': f"{user.first_name} {user.last_name}",
            'address': f"{user.street}, {user.city}, {user.state}, {user.country}" if user.street else "No address on file",
            'gender': "Male" if user.gender == 'M' else "Female" if user.gender == 'F' else "Other",
            'home_phone': user.home_phone_number if user.home_phone_number else "No phone number on file",
            'business_phone': user.business_phone_number if user.business_phone_number else "No phone number on file",
            'role': user.role,
            'zipcode': user.zipcode if user.zipcode else "No zipcode on file"
        })
    else:
        return JsonResponse({'success': False, 'message': 'User not found'})

@csrf_exempt 
def find_equipment(request):
    asset_tag_number = request.GET.get('asset_tag_number')
    equipment = Equipment.objects.filter(asset_tag_number=asset_tag_number).first()
    if equipment:
        return JsonResponse({
            'success': True,
            'equipment_name': equipment.equipment_name,
            'serial_number': equipment.serial_number,
            'install_date': equipment.install_date.strftime('%Y-%m-%d') if equipment.install_date else ''
        })
    return JsonResponse({'success': False, 'message': 'Equipment not found'})

@csrf_exempt
def find_sales(request):
    email = request.GET.get('email')
    sales_executive = Person.objects.exclude(role="Client").filter(email=email).first()
    if sales_executive:
        gender = "Male" if sales_executive.gender == 'M' else "Female" if sales_executive.gender == 'F' else "Other or not specified"

        return JsonResponse({
            'success': True,
            'full_name': f"{sales_executive.first_name} {sales_executive.last_name}",
            'zipcode': sales_executive.zipcode if sales_executive.zipcode else "",
            'role': sales_executive.role,
            'address': f"{sales_executive.street}, {sales_executive.city}, {sales_executive.state}, {sales_executive.country}" if sales_executive.street else "No address on file",
            'home_phone': sales_executive.home_phone_number if sales_executive.home_phone_number else "No phone number on file",
            'gender': gender,
            'business_phone': sales_executive.business_phone_number if sales_executive.business_phone_number else "No phone number on file"
        })
    return JsonResponse({'success': False, 'message': 'Sales executive not found'})

@csrf_exempt
def find_user(request):
    email = request.GET.get('email')
    user = Person.objects.filter(role="Client", email=email).first()
    if user:
        gender = "Male" if user.gender == 'M' else "Female" if user.gender == 'F' else "Other or not specified"

        return JsonResponse({
            'success': True,
            'full_name': f"{user.first_name} {user.last_name}",
            'zipcode': user.zipcode if user.zipcode else "",
            'role': user.role,
            'address': f"{user.street}, {user.city}, {user.state}, {user.country}" if user.street else "No address on file",
            'home_phone': user.home_phone_number if user.home_phone_number else "No phone number on file",
            'gender': gender,
            'business_phone': user.business_phone_number if user.business_phone_number else "No phone number on file"
        })
    return JsonResponse({'success': False, 'message': 'User not found'})

@login_required
def search_user(request):
    search_term = request.POST.get('search_term', '').strip() if request.method == 'POST' else ''

    if search_term:
        users = Person.objects.filter(
            Q(id__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(email__icontains=search_term) |
            Q(role__icontains=search_term) |
            Q(gender__icontains=search_term) |
            Q(street__icontains=search_term) |
            Q(city__icontains=search_term) |
            Q(state__icontains=search_term) |
            Q(zipcode__icontains=search_term) |
            Q(country__icontains=search_term) |
            Q(home_phone_number__icontains=search_term) |
            Q(business_phone_number__icontains=search_term)
        )
    else:
        users = Person.objects.all()

    context = {
        'users': users,
        'segment': 'search-user',
        'search_term': search_term  # Pass the search term back to the template
    }
    return render(request, 'pages/searchuser.html', context)

@login_required
def search_equipment(request):
    search_term = request.POST.get('search_term', '').strip() if request.method == 'POST' else ''

    if search_term:
        equipment_list = Equipment.objects.filter(
            Q(asset_tag_number__icontains=search_term) |
            Q(equipment_name__icontains=search_term) |
            Q(serial_number__icontains=search_term) |
            Q(install_date__icontains=search_term)       
          )
    else:
        equipment_list = Equipment.objects.all()

    context = {
        'equipment_list': equipment_list,
        'segment': 'search-equipment',
        'search_term': search_term  # Pass the search term back to the template
    }
    return render(request, 'pages/searchequipment.html', context)


@csrf_exempt
def search_contract(request):
    search_term = request.POST.get('search_term', '').strip() if request.method == 'POST' else ''

    if search_term:
        contracts = Contract.objects.filter(
            Q(id__icontains=search_term) |
            Q(installation_date__icontains=search_term) |
            Q(billing_date__icontains=search_term) |
            Q(renewal_date__icontains=search_term) |
            Q(monthly_charges__icontains=search_term) |
            Q(contractequipment__person__first_name__icontains=search_term) |
            Q(contractequipment__person__last_name__icontains=search_term) |
            Q(contractequipment__person__email__icontains=search_term) |
            Q(contractequipment__person__role__icontains=search_term) |
            Q(contractequipment__equipment__asset_tag_number__icontains=search_term) |
            Q(contractequipment__equipment__equipment_name__icontains=search_term) |
            Q(contractequipment__equipment__serial_number__icontains=search_term) |
            Q(person__first_name__icontains=search_term) |  # Sales Executive details
            Q(person__last_name__icontains=search_term) |
            Q(person__email__icontains=search_term) |
            Q(person__role__icontains=search_term)
            # Add other fields as needed
        ).distinct()
    else:
        contracts = Contract.objects.all()

    context = {
        'contracts': contracts,
        'segment': 'search-contract',
        'search_term': search_term  # Pass the search term back to the template
    }

    return render(request, 'pages/searchcontract.html', context)