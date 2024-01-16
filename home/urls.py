from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

urlpatterns = [
  path(''       , views.index,  name='index'),
  path('', RedirectView.as_view(url='/accounts/login/', permanent=True)),

  path('tables/', views.tables, name='tables'),
  path('person/', views.person, name='person'),
  path('add-user', views.add_user, name='add_user'),
  path('add-equipment', views.add_equipment, name='add_equipment'),
  path('add-contract', views.add_contract, name='add_contract'),
  path('find-user', views.find_user, name='find_user'),
  path('find-equipment', views.find_equipment, name='find_equipment'),
  path('find-sales', views.find_sales, name='find_sales'),
  path('search-user/', views.search_user, name='search_user'),  # URL pattern for search_user view
  path('search-equipment/', views.search_equipment, name='search_equipment'),
  path('search-contract/', views.search_contract, name='search_contract'),
]
