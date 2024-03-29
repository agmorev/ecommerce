from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.utils import timezone


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was successfully updated.')
        else:
            order.items.add(order_item)
            messages.info(request, 'This item was successfully added to your cart.')
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add()
    return redirect("core:product", slug=slug)

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, 'This item was successfully removed from your cart.')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)