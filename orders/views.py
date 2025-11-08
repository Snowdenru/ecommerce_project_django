from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart, CartItem

def order_create(request):
    cart = _get_cart(request)
    
    if not cart.items.exists():
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        # Обработка формы заказа
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        
        # Создание заказа
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city,
            phone=phone
        )
        
        # Перенос товаров из корзины в заказ
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )
        
        # Очистка корзины
        cart.items.all().delete()
        
        messages.success(request, 'Ваш заказ успешно создан!')
        return redirect('orders:order_created', order_id=order.id)
    
    context = {
        'cart': cart,
    }
    return render(request, 'orders/create.html', context)

def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'orders/created.html', context)

def order_list(request):
    # Скорректировать отображение по конркетному пользователю
    # orders = Order.objects.filter(email=request.user.email).order_by('-created')
    orders = Order.objects.all().order_by('-created')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/list.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'orders/detail.html', context)

def _get_cart(request):
    """Вспомогательная функция для получения корзины"""
    if not request.session.session_key:
        request.session.create()
    
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart