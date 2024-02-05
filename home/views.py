from django.shortcuts import render, redirect
from admin_datta.forms import (
    RegistrationForm,
    LoginForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib import messages
from .models import *
from django.db import IntegrityError
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q

from django.contrib.auth.decorators import login_required, permission_required
import json
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from .forms import *
from .models import *


@login_required(login_url="/accounts/login/")
def index(request):
    # Filter staff members by the business of the logged-in user and their active status
    inactive_users = Staff.objects.filter(
        business=request.user.business, is_active=False
    ).order_by("-id")[:5]
    total_staff = Staff.objects.filter(business=request.user.business).count()
    total_clients = Person.objects.filter(
        business=request.user.business, role="Client"
    ).count()

    # Calculate daily, monthly, and yearly sales
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Filter sales for today
    daily_sales_amount = (
        Sale.objects.filter(
            purchase_date=today,
            business=request.user.business,  # Assuming the user is associated with a business
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    # Filter sales for the current month
    monthly_sales_amount = (
        Sale.objects.filter(
            purchase_date__year=current_year,
            purchase_date__month=current_month,
            business=request.user.business,
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    # Filter sales for the current year
    yearly_sales_amount = (
        Sale.objects.filter(
            purchase_date__year=current_year, business=request.user.business
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    yesterday = today - timedelta(days=1)

    yesterday_sales_amount = (
        Sale.objects.filter(
            purchase_date=yesterday, business=request.user.business
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    # Calculate the percentage change
    if yesterday_sales_amount > 0:
        daily_sales_change_percentage = (
            (daily_sales_amount - yesterday_sales_amount) / yesterday_sales_amount
        ) * 100
    elif yesterday_sales_amount == 0 and daily_sales_amount > 0:
        daily_sales_change_percentage = 100
    elif yesterday_sales_amount == 0 and daily_sales_amount == 0:
        daily_sales_change_percentage = 0
    else:
        daily_sales_change_percentage = -100

    previous_month = current_month - 1 if current_month > 1 else 12
    previous_month_year = current_year if current_month > 1 else current_year - 1

    # Previous month's sales
    previous_month_sales_amount = (
        Sale.objects.filter(
            purchase_date__year=previous_month_year,
            purchase_date__month=previous_month,
            business=request.user.business,
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    # Calculate the percentage change
    if previous_month_sales_amount > 0:
        monthly_sales_change_percentage = (
            (monthly_sales_amount - previous_month_sales_amount)
            / previous_month_sales_amount
        ) * 100
    elif previous_month_sales_amount == 0 and monthly_sales_amount > 0:
        monthly_sales_change_percentage = 100
    elif previous_month_sales_amount == 0 and monthly_sales_amount == 0:
        monthly_sales_change_percentage = 0
    else:
        monthly_sales_change_percentage = -100

    previous_year = current_year - 1
    # Previous year's sales
    previous_year_sales_amount = (
        Sale.objects.filter(
            purchase_date__year=previous_year, business=request.user.business
        ).aggregate(total=Sum("charges"))["total"]
        or 0
    )

    # Calculate the percentage change
    if previous_year_sales_amount > 0:
        yearly_sales_change_percentage = (
            (yearly_sales_amount - previous_year_sales_amount)
            / previous_year_sales_amount
        ) * 100
    elif previous_year_sales_amount == 0 and yearly_sales_amount > 0:
        yearly_sales_change_percentage = 100
    elif previous_year_sales_amount == 0 and yearly_sales_amount == 0:
        yearly_sales_change_percentage = 0
    else:
        yearly_sales_change_percentage = -100

    context = {
        "segment": "dashboard",
        "users": inactive_users,
        "total_staff": total_staff,
        "total_clients": total_clients,
        "daily_sales": daily_sales_amount,
        "monthly_sales": monthly_sales_amount,
        "yearly_sales": yearly_sales_amount,
        "daily_sales_change_percentage": daily_sales_change_percentage,
        "daily_sales_change_percentage_abs": abs(daily_sales_change_percentage),
        "monthly_sales_change_percentage": monthly_sales_change_percentage,
        "monthly_sales_change_percentage_abs": abs(monthly_sales_change_percentage),
        "yearly_sales_change_percentage": yearly_sales_change_percentage,
        "yearly_sales_change_percentage_abs": abs(yearly_sales_change_percentage),
    }
    staff_context = {
        "segment": "dashboard",
    }

    # Get all businesses
    # businesses = Business.objects.all()

    # Get the most recent 5 businesses
    businesses = Business.objects.all().order_by("-id")[:5]

    # Create a list to store business data
    business_data = []

    for business in businesses:
        # Retrieve the owner associated with each business
        try:
            owner = Owner.objects.get(business=business)
            owner_name = owner.username
            owner_email = owner.email
            date_joined = owner.date_joined
            status = owner.is_active

        except Owner.DoesNotExist:
            owner_name = "N/A"
            owner_email = ""
            date_joined = None
            status = False

        # Create a dictionary for each business's data
        business_info = {
            "business_name": business.name,
            "owner_name": owner_name,
            "date_joined": date_joined,
            "status": status,
            "owner_email": owner_email,
        }

        business_data.append(business_info)

    business_count = Business.objects.count()
    user_count = User.objects.count()

    admin_context = {
        "segment": "dashboard",
        "business_data": business_data,
        "business_count": business_count,
        "user_count": user_count,
    }
    if request.user.role == "OWNER":
        return render(request, "pages/dashboard_business.html", context)
    elif request.user.role == "STAFF":
        return render(request, "pages/dashboard_staff.html", staff_context)
    elif request.user.role == "ADMIN":
        return render(request, "pages/dashboard_admin.html", admin_context)
    else:
        return render(request, "pages/dashboard.html", context)


@login_required(login_url="/accounts/login/")
def profile(request):
    context = {
        "segment": "profile",
    }
    return render(request, "pages/profile.html", context)


@login_required
@permission_required("home.change_staff", raise_exception=True)
@require_http_methods(["POST"])
def approve_staff(request, user_id):
    try:
        user = get_object_or_404(Staff, pk=user_id)
        print(user.email)
        # Check if the user's business matches the logged-in user's business
        if user.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to approve this user.",
                },
                status=403,
            )
        user.is_active = True
        user.save()
        return JsonResponse({"success": True})
    except Staff.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
@permission_required("home.view_staff", raise_exception=True)
def search_staff(request):
    search_term = (
        request.POST.get("search_term", "").strip() if request.method == "POST" else ""
    )

    user_business = request.user.business
    # base_queryset = Staff.objects.filter(business=user_business, is_active=True)
    base_queryset = Staff.objects.filter(business=user_business)

    if search_term:
        staff_list = base_queryset.filter(
            Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(username__icontains=search_term)
        )
    else:
        staff_list = base_queryset

    context = {
        "staff_list": staff_list,
        "segment": "search-staff",
        "search_term": search_term,  # Pass the search term back to the template
    }
    return render(request, "pages/search_staff.html", context)


@login_required
@require_http_methods(["DELETE"])
@permission_required("home.delete_staff", raise_exception=True)
def delete_staff(request, staff_id):
    try:
        staff = get_object_or_404(User, pk=staff_id)
        # Check if the staff's business matches the user's business
        if staff.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to delete this staff.",
                },
                status=403,
            )
        staff.delete()
        return JsonResponse({"success": True})
    except User.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        # Log the error
        return JsonResponse({"success": False}, status=500)


@login_required
@permission_required("home.delete_staff", raise_exception=True)
@require_http_methods(["POST"])
def reject_staff(request, user_id):
    try:
        user = get_object_or_404(Staff, pk=user_id)
        # business check as in approve_user
        if user.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to reject this user.",
                },
                status=403,
            )
        user.delete()
        return JsonResponse({"success": True})
    except Staff.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


def staff_dashborad(request):
    context = {
        "segment": "staff-dashborad",
    }
    return render(request, "pages/staff.html", context)


@login_required(login_url="/accounts/login/")
@permission_required("home.add_person", raise_exception=True)
def add_person(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            try:
                person = form.save(commit=False)
                person.business = request.user.business  # Set the business
                person.save()

                messages.success(request, "Person added successfully!")
                return redirect("add_person")
            except IntegrityError as e:
                if "unique_email_per_business" in str(e):
                    form.add_error(
                        "email", "Email already in use. Please use a different email."
                    )
                    messages.error(request, "Please correct the errors below.")

                else:
                    messages.error(
                        request, "A database error occurred. Please try again."
                    )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PersonForm()

    context = {"form": form, "segment": "add-person"}
    return render(request, "pages/add_person.html", context)


@login_required(login_url="/accounts/login/")
@permission_required("home.add_item", raise_exception=True)
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                # Set the business for the item
                item = form.save(commit=False)
                item.business = request.user.business
                item.save()

                messages.success(request, "Item added successfully!")
                return redirect("add_item")
            except IntegrityError as e:
                if "unique_asset_tag_per_business" in str(e):
                    form.add_error(
                        "asset_tag_number",
                        "Asset tag number already in use for this business. Please use a different asset tag number.",
                    )
                if "unique_serial_number_per_business" in str(e):
                    form.add_error(
                        "serial_number",
                        "Serial number already in use for this business. Please use a different serial number.",
                    )
                messages.error(
                    request,
                    "Please correct the errors below.",
                    extra_tags="error",
                )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ItemForm()

    context = {"form": form, "segment": "add-item"}
    return render(request, "pages/add_item.html", context)


from datetime import datetime


@login_required
@permission_required("home.add_sale", raise_exception=True)
def add_sale(request):
    if request.method == "POST":
        try:
            # Extract sale data from form
            purchase_date = request.POST.get("purchase_date")
            if not purchase_date:
                purchase_date = timezone.now().date()
            else:
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            charges = request.POST.get("charges")
            payment_method = request.POST.get("payment_method")
            payment_interval = request.POST.get("payment_interval", None)

            # Fetch client details
            email = request.POST.get("email")
            client = Person.objects.filter(
                email=email, role="Client", business=request.user.business
            ).first()

            if not client:
                messages.error(request, "Client not found.")
                raise ValueError("Client not found.")

            # Fetch salesperson details
            semail = request.POST.get("sale_email")
            salesperson = (
                Person.objects.filter(email=semail)
                .exclude(role="Client", business=request.user.business)
                .first()
            )

            if not salesperson:
                messages.error(request, "Salesperson not found.")
                raise ValueError("Salesperson not found.")

            # Fetch items details
            tag = request.POST.get("asset_tag_number")
            item = Item.objects.filter(
                asset_tag_number=tag, business=request.user.business
            ).first()

            if not item:
                messages.error(request, "Item not found.")
                raise ValueError("Item not found.")

            # Calculate billing_date based on payment_interval
            billing_date = None
            if payment_method == "Recurring" and payment_interval != "Manual":
                # billing_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
                billing_date = purchase_date
                if payment_interval == "Monthly":
                    billing_date += timedelta(days=30)
                elif payment_interval == "Quarterly":
                    billing_date += timedelta(days=90)
                elif payment_interval == "Half-Yearly":
                    billing_date += timedelta(days=180)
                elif payment_interval == "Yearly":
                    billing_date += timedelta(days=365)

            renewal_date = request.POST.get("renewal_date", None)
            if payment_interval == "Manual":
                if renewal_date:
                    billing_date = datetime.strptime(renewal_date, "%Y-%m-%d").date()
                else:
                    messages.error(
                        request, "Renewal date is required for manual payments."
                    )
                    raise ValueError("Renewal date is required for manual payments.")

            # Create and add a new sale
            new_sale = Sale(
                purchase_date=purchase_date,
                charges=charges,
                payment_method=payment_method,
                payment_interval=payment_interval
                if payment_method == "Recurring"
                else None,
                billing_date=billing_date,
                role=salesperson.role,
                person=salesperson,
                business=request.user.business,
            )
            new_sale.save()

            # Create and add a new entry in sale_items table
            new_sale_item = SaleItem(sale=new_sale, item=item, person=client)
            new_sale_item.save()

            messages.success(request, "Sale created successfully!")
            return redirect("add_sale")

        except IntegrityError as e:
            print(e)
            messages.error(
                request,
                "A database error occurred. Please try again.",
                extra_tags="info",
            )

        except ValueError as e:
            messages.error(
                request,
                "Please check the provided information.",
                extra_tags="info",
            )

        except Exception as e:
            print("Exception " + str(e))
            messages.error(
                request, "Record not added. Please try again.", extra_tags="info"
            )

        # Render the form with existing data in case of an error
        context = {"form_data": request.POST or None, "segment": "add_sale"}
        return render(request, "pages/add_sale.html", context)

    # If GET request, render the form with empty context
    return render(request, "pages/add_sale.html", {"segment": "add-sale"})


@login_required
def find_item(request):
    asset_tag_number = request.GET.get("asset_tag_number")
    user_business = request.user.business  # Get the business of the logged-in user
    base_queryset = Item.objects.filter(business=user_business)
    item = base_queryset.filter(asset_tag_number=asset_tag_number).first()
    if item:
        return JsonResponse(
            {
                "success": True,
                "item_name": item.item_name,
                "serial_number": item.serial_number,
                "install_date": item.install_date.strftime("%Y-%m-%d")
                if item.install_date
                else "",
            }
        )
    return JsonResponse({"success": False, "message": "Item not found"})


@login_required
def find_sales(request):
    email = request.GET.get("email")
    user_business = request.user.business  # Get the business of the logged-in user
    base_queryset = Person.objects.filter(business=user_business)
    sales_executive = base_queryset.exclude(role="Client").filter(email=email).first()
    if sales_executive:
        gender = (
            "Male"
            if sales_executive.gender == "M"
            else "Female"
            if sales_executive.gender == "F"
            else "Other or not specified"
        )

        return JsonResponse(
            {
                "success": True,
                "full_name": f"{sales_executive.first_name} {sales_executive.last_name}",
                "zipcode": sales_executive.zipcode if sales_executive.zipcode else "",
                "role": sales_executive.role,
                "address": f"{sales_executive.street}, {sales_executive.city}, {sales_executive.state}, {sales_executive.country}"
                if sales_executive.street
                else "No address on file",
                "home_phone": sales_executive.home_phone_number
                if sales_executive.home_phone_number
                else "No phone number on file",
                "gender": gender,
                "business_phone": sales_executive.business_phone_number
                if sales_executive.business_phone_number
                else "No phone number on file",
            }
        )
    return JsonResponse({"success": False, "message": "Sales executive not found"})


@login_required
def find_user(request):
    email = request.GET.get("email")
    user_business = request.user.business  # Get the business of the logged-in user
    base_queryset = Person.objects.filter(business=user_business)
    user = base_queryset.filter(role="Client", email=email).first()
    if user:
        gender = (
            "Male"
            if user.gender == "M"
            else "Female"
            if user.gender == "F"
            else "Other or not specified"
        )

        return JsonResponse(
            {
                "success": True,
                "full_name": f"{user.first_name} {user.last_name}",
                "zipcode": user.zipcode if user.zipcode else "",
                "role": user.role,
                "address": f"{user.street}, {user.city}, {user.state}, {user.country}"
                if user.street
                else "No address on file",
                "home_phone": user.home_phone_number
                if user.home_phone_number
                else "No phone number on file",
                "gender": gender,
                "business_phone": user.business_phone_number
                if user.business_phone_number
                else "No phone number on file",
            }
        )
    return JsonResponse({"success": False, "message": "Client not found"})


from django.db.models import Count


@login_required
@permission_required("home.view_business", raise_exception=True)
def search_business(request):
    search_term = (
        request.POST.get("search_term", "").strip() if request.method == "POST" else ""
    )

    # Start the query from the Owner model
    base_queryset = User.objects.filter(role=User.Role.OWNER).select_related("business")

    if search_term:
        owners = base_queryset.filter(
            Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(username__icontains=search_term)
            | Q(
                business__name__icontains=search_term
            )  # Searches the related Business model's name field
        ).annotate(
            staff_count=Count(
                "business__user", filter=Q(business__user__role=User.Role.STAFF)
            )
        )
    else:
        owners = base_queryset.annotate(
            staff_count=Count(
                "business__user", filter=Q(business__user__role=User.Role.STAFF)
            )
        )

    context = {
        "owners": owners,
        "segment": "search-business",
        "search_term": search_term,
    }
    return render(request, "pages/search_business.html", context)


@login_required
@permission_required("home.view_person", raise_exception=True)
def search_person(request):
    search_term = (
        request.POST.get("search_term", "").strip() if request.method == "POST" else ""
    )

    user_business = request.user.business  # Get the business of the logged-in user
    base_queryset = Person.objects.filter(business=user_business)

    if search_term:
        users = base_queryset.filter(
            Q(id__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(role__icontains=search_term)
            | Q(gender__icontains=search_term)
            | Q(street__icontains=search_term)
            | Q(city__icontains=search_term)
            | Q(state__icontains=search_term)
            | Q(zipcode__icontains=search_term)
            | Q(country__icontains=search_term)
            | Q(home_phone_number__icontains=search_term)
            | Q(business_phone_number__icontains=search_term)
        )
    else:
        users = base_queryset

    context = {
        "users": users,
        "segment": "search-person",
        "search_term": search_term,  # Pass the search term back to the template
    }
    return render(request, "pages/search_person.html", context)


@login_required
@permission_required("home.view_item", raise_exception=True)
def search_item(request):
    search_term = (
        request.POST.get("search_term", "").strip() if request.method == "POST" else ""
    )

    user_business = request.user.business
    base_queryset = Item.objects.filter(business=user_business)

    if search_term:
        item_list = base_queryset.filter(
            Q(asset_tag_number__icontains=search_term)
            | Q(item_name__icontains=search_term)
            | Q(serial_number__icontains=search_term)
            | Q(install_date__icontains=search_term)
        )
    else:
        item_list = base_queryset

    context = {
        "item_list": item_list,
        "segment": "search-item",
        "search_term": search_term,  # Pass the search term back to the template
    }
    return render(request, "pages/search_item.html", context)


@login_required
@permission_required("home.view_sale", raise_exception=True)
def search_sale(request):
    search_term = (
        request.POST.get("search_term", "").strip() if request.method == "POST" else ""
    )

    user_business = request.user.business
    base_queryset = Sale.objects.filter(business=user_business)

    if search_term:
        sales = base_queryset.filter(
            Q(id__icontains=search_term)
            | Q(purchase_date__icontains=search_term)
            | Q(charges__icontains=search_term)
            | Q(payment_method__icontains=search_term)
            | Q(payment_interval__icontains=search_term)
            | Q(billing_date__icontains=search_term)
            | Q(saleitem__person__first_name__icontains=search_term)
            | Q(saleitem__person__last_name__icontains=search_term)
            | Q(saleitem__person__email__icontains=search_term)
            | Q(saleitem__person__role__icontains=search_term)
            | Q(saleitem__item__asset_tag_number__icontains=search_term)
            | Q(saleitem__item__item_name__icontains=search_term)
            | Q(saleitem__item__serial_number__icontains=search_term)
            | Q(person__first_name__icontains=search_term)
            | Q(person__last_name__icontains=search_term)  # Sales Executive details
            | Q(person__email__icontains=search_term)
            | Q(person__role__icontains=search_term)
        ).distinct()
    else:
        sales = base_queryset

    context = {
        "sales": sales,
        "segment": "search-sale",
        "search_term": search_term,  # Pass the search term back to the template
    }

    return render(request, "pages/search_sale.html", context)


@login_required
@permission_required("home.delete_item", raise_exception=True)
@require_http_methods(["DELETE"])
def delete_item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
        # Check if the item's business matches the user's business
        if item.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to delete this item.",
                },
                status=403,
            )
        item.delete()
        return JsonResponse({"success": True})
    except Item.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        # Log the error
        return JsonResponse({"success": False}, status=500)


@login_required
@permission_required("home.change_item", raise_exception=True)
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Check if the item's business matches the user's business
    if item.business != request.user.business:
        # messages.error(request, "item not found.")
        return redirect("search_item")

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect("search_item")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ItemForm(instance=item)

    context = {"form": form, "item": item, "segment": "edit-item"}
    return render(request, "pages/edit_item.html", context)


@login_required
@permission_required("home.delete_person", raise_exception=True)
@require_http_methods(["DELETE"])
def delete_person(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
        # Check if the person's business matches the user's business
        if person.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to delete this person.",
                },
                status=403,
            )
        person.delete()
        return JsonResponse({"success": True})
    except Person.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        # Log the error
        return JsonResponse({"success": False}, status=500)


@login_required
@permission_required("home.change_person", raise_exception=True)
def edit_person(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    # Check if the person's business matches the user's business
    if person.business != request.user.business:
        # messages.error(request, "person not found.")
        return redirect("search_person")
    if request.method == "POST":
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, "Person updated successfully!")
            return redirect("search_person")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PersonForm(instance=person)

    context = {"form": form, "person": person, "segment": "edit-person"}  # segment key
    return render(request, "pages/edit_person.html", context)


@login_required
@permission_required("home.delete_sale", raise_exception=True)
@require_http_methods(["DELETE"])
def delete_sale(request, sale_id):
    try:
        sale = Sale.objects.get(pk=sale_id)
        # Check if the sales's business matches the user's business
        if sale.business != request.user.business:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to delete this sale.",
                },
                status=403,
            )
        sale.delete()
        return JsonResponse({"success": True})
    except Sale.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    except Exception as e:
        # Log the error
        return JsonResponse({"success": False}, status=500)


@login_required
@permission_required("home.change_item", raise_exception=True)
def export_items(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="items.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["No.", "Name", "Asset Tag Number", "Serial Number", "Install Date"]
    )

    items = Item.objects.filter(business=request.user.business)
    count = 1  # Initialize counter
    for item in items:
        writer.writerow(
            [
                count,
                item.item_name,
                item.asset_tag_number,
                item.serial_number,
                item.install_date,
            ]
        )
        count += 1  # Increment counter

    return response


@login_required
@permission_required("home.change_staff", raise_exception=True)
def export_staff(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="staff.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["No.", "Username", "First Name", "Last Name", "Email", "Last Login"]
    )

    staff_members = User.objects.filter(business=request.user.business)
    count = 1  # Initialize counter
    for staff in staff_members:
        writer.writerow(
            [
                count,
                staff.username,
                staff.first_name,
                staff.last_name,
                staff.email,
                staff.last_login if staff.last_login else "Not logged in yet",
            ]
        )
        count += 1  # Increment counter

    return response


@login_required
@permission_required("home.change_person", raise_exception=True)
def export_person(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="persons.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "First Name",
            "Last Name",
            "Gender",
            "Email",
            "Role",
            "Street",
            "City",
            "State",
            "Zipcode",
            "Country",
            "Home Phone Number",
            "Business Phone Number",
        ]
    )

    persons = Person.objects.filter(business=request.user.business)
    count = 1  # Initialize counter
    for person in persons:
        writer.writerow(
            [
                count,
                person.first_name,
                person.last_name,
                person.get_gender_display(),  # Use get_FOO_display() to get the readable value of ChoiceField
                person.email,
                person.get_role_display(),  # Use get_FOO_display() for readable role
                person.street,
                person.city,
                person.state,
                person.zipcode,
                person.country,
                person.home_phone_number,
                person.business_phone_number,
            ]
        )
        count += 1  # Increment counter

    return response


@login_required
@permission_required("home.change_sale", raise_exception=True)
def export_sale(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sales.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "No.",
            "Purchase Date",
            "Charges",
            "Billing Date",
            "Payment Method",
            "Client",
            "Email",
            "Salesperson",
            "Role",
            "Item",
        ]
    )

    sales = Sale.objects.filter(business=request.user.business)
    count = 1  # Initialize counter
    for sale in sales:
        # Assuming each sale has only one SaleItem, adjust as needed
        sale_item = SaleItem.objects.filter(sale=sale).first()

        writer.writerow(
            [
                count,
                sale.purchase_date,
                sale.charges,
                sale.billing_date,
                sale.payment_method
                if sale.payment_method == "One-time"
                or sale.payment_method == "One-Time"
                else f"{sale.payment_method} - {sale.payment_interval}",
                sale_item.person.get_full_name() if sale_item else "",
                sale_item.person.email,
                sale.person.get_full_name(),
                sale.person.role,
                sale_item.item.item_name if sale_item else "",
            ]
        )
        count += 1  # Increment counter

    return response
