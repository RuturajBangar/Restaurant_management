from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone

from .models import Category, MenuItem, Table, Order, OrderItem, Reservation, Customer
from .forms import (
    MenuItemForm, TableForm, ReservationForm, CustomerForm,
    OrderForm, OrderItemForm,
)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """Staff landing page: quick stats + today's activity."""
    today = timezone.localdate()
    context = {
        'total_tables': Table.objects.count(),
        'occupied_tables': Table.objects.filter(status='occupied').count(),
        'active_orders': Order.objects.exclude(status__in=['paid', 'cancelled']).count(),
        'todays_reservations': Reservation.objects.filter(date=today).order_by('time'),
        'recent_orders': Order.objects.select_related('table', 'customer')[:8],
        'todays_revenue': sum(
            o.total for o in Order.objects.filter(status='paid', updated_at__date=today)
        ),
    }
    return render(request, 'restaurant/dashboard.html', context)


# ---------------------------------------------------------------------------
# Public-facing menu (no login required, e.g. for customers to browse)
# ---------------------------------------------------------------------------

def menu_list(request):
    categories = Category.objects.prefetch_related('items').all()
    return render(request, 'restaurant/menu_list.html', {'categories': categories})


@login_required
def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item created.')
            return redirect('menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'restaurant/menu_item_form.html', {'form': form, 'title': 'Add Menu Item'})


@login_required
def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated.')
            return redirect('menu_list')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'restaurant/menu_item_form.html', {'form': form, 'title': 'Edit Menu Item'})


@login_required
def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted.')
        return redirect('menu_list')
    return render(request, 'restaurant/confirm_delete.html', {'object': item})


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

@login_required
def table_list(request):
    tables = Table.objects.all()
    return render(request, 'restaurant/table_list.html', {'tables': tables})


@login_required
def table_create(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table added.')
            return redirect('table_list')
    else:
        form = TableForm()
    return render(request, 'restaurant/table_form.html', {'form': form, 'title': 'Add Table'})


@login_required
def table_update(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table updated.')
            return redirect('table_list')
    else:
        form = TableForm(instance=table)
    return render(request, 'restaurant/table_form.html', {'form': form, 'title': 'Edit Table'})


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@login_required
def order_list(request):
    status = request.GET.get('status')
    orders = Order.objects.select_related('table', 'customer').all()
    if status:
        orders = orders.filter(status=status)
    return render(request, 'restaurant/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        # Adding a new item to this order
        item_form = OrderItemForm(request.POST)
        if item_form.is_valid():
            order_item = item_form.save(commit=False)
            order_item.order = order
            order_item.price = order_item.menu_item.price
            order_item.save()
            messages.success(request, 'Item added to order.')
            return redirect('order_detail', pk=order.pk)
    else:
        item_form = OrderItemForm()

    return render(request, 'restaurant/order_detail.html', {
        'order': order,
        'item_form': item_form,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if not order.server_id:
                order.server = request.user
            order.save()
            # Mark the table as occupied
            if order.table:
                order.table.status = 'occupied'
                order.table.save()
            messages.success(request, f'Order #{order.pk} created.')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(initial={'server': request.user})
    return render(request, 'restaurant/order_form.html', {'form': form, 'title': 'New Order'})


@login_required
def order_item_remove(request, pk, item_pk):
    order = get_object_or_404(Order, pk=pk)
    item = get_object_or_404(OrderItem, pk=item_pk, order=order)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removed from order.')
    return redirect('order_detail', pk=order.pk)


@login_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Order.STATUS_CHOICES)
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            # Free up the table once the order is paid or cancelled
            if new_status in ('paid', 'cancelled') and order.table:
                order.table.status = 'available'
                order.table.save()
            messages.success(request, f'Order marked as {valid_statuses[new_status]}.')
    return redirect('order_detail', pk=order.pk)


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------

@login_required
def reservation_list(request):
    reservations = Reservation.objects.select_related('customer', 'table').all()
    return render(request, 'restaurant/reservation_list.html', {'reservations': reservations})


@login_required
def reservation_create(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation created.')
            return redirect('reservation_list')
    else:
        form = ReservationForm()
    return render(request, 'restaurant/reservation_form.html', {'form': form, 'title': 'New Reservation'})


@login_required
def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation updated.')
            return redirect('reservation_list')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'restaurant/reservation_form.html', {'form': form, 'title': 'Edit Reservation'})


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer added.')
            next_url = request.POST.get('next') or 'dashboard'
            return redirect(next_url)
    else:
        form = CustomerForm()
    return render(request, 'restaurant/customer_form.html', {'form': form, 'title': 'Add Customer'})
