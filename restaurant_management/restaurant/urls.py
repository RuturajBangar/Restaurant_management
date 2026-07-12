from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Menu
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.menu_item_create, name='menu_item_create'),
    path('menu/<int:pk>/edit/', views.menu_item_update, name='menu_item_update'),
    path('menu/<int:pk>/delete/', views.menu_item_delete, name='menu_item_delete'),

    # Tables
    path('tables/', views.table_list, name='table_list'),
    path('tables/add/', views.table_create, name='table_create'),
    path('tables/<int:pk>/edit/', views.table_update, name='table_update'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/items/<int:item_pk>/remove/', views.order_item_remove, name='order_item_remove'),

    # Reservations
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/add/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/edit/', views.reservation_update, name='reservation_update'),

    # Customers
    path('customers/add/', views.customer_create, name='customer_create'),
]
