from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("approve_staff/<int:user_id>/", views.approve_staff, name="approve_staff"),
    path("reject_staff/<int:user_id>/", views.reject_staff, name="reject_staff"),
    path("", RedirectView.as_view(url="/accounts/login/", permanent=True)),
    path("search-staff/", views.search_staff, name="search_staff"),
    path("delete-staff/<int:staff_id>/", views.delete_staff, name="delete_staff"),
    path(
        "delete-item/<int:item_id>/",
        views.delete_item,
        name="delete_item",
    ),
    path(
        "edit-item/<int:item_id>/",
        views.edit_item,
        name="edit_item",
    ),
    path(
        "delete-person/<int:person_id>/",
        views.delete_person,
        name="delete_person",
    ),
    path("edit-person/<int:person_id>/", views.edit_person, name="edit_person"),
    path("delete-sale/<int:sale_id>/", views.delete_sale, name="delete_sale"),
    path("add-person/", views.add_person, name="add_person"),
    path("add-item/", views.add_item, name="add_item"),
    path("add-sale/", views.add_sale, name="add_sale"),
    path("find-user", views.find_user, name="find_user"),
    path("find-item", views.find_item, name="find_item"),
    path("find-sales", views.find_sales, name="find_sales"),
    path("search-person/", views.search_person, name="search_person"),
    path("search-item/", views.search_item, name="search_item"),
    path("search-sale/", views.search_sale, name="search_sale"),
    path("export-items/", views.export_items, name="export_items"),
    path("export-staff/", views.export_staff, name="export_staff"),
    path("export-person/", views.export_person, name="export_person"),
    path("export-sale/", views.export_sale, name="export_sale"),
    path("search-business/", views.search_business, name="search_business"),

    path("report/", views.generate_report, name="generate_report"),

]
