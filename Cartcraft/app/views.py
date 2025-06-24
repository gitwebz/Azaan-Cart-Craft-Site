from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from .models import Costumer, Product, Order, Cart
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from .models import User
from difflib import SequenceMatcher
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin


# home
def home(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'app/home.html', {'cart_count': cart_count})

# Product
class ProductView(View):
    def get(self, request):
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        context = {
            'mobiles': mobiles,
            'laptops': laptops,
        }
        return render(request, 'app/home.html', context)

# Product Detail
class Product_detail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html', {'product': product})

# 🔒 Requires user to be logged in
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    cart_url = reverse('cart')
    messages.success(request, f"Item added to cart.")
    return redirect('home')

# 🔒 Requires user to be logged in
@login_required
def cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    if not cart.exists():
        return render(request, 'app/empty_cart.html')

    total_amount = 0
    for item in cart:
        total_amount += item.quantity * item.product.discounted_price

    shipping_cost = 0 if total_amount > 20000 else 350
    grand_total = total_amount + shipping_cost

    return render(request, 'app/addtocart.html', {
        'cart': cart,
        'total_amount': total_amount,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total
    })

# 🔒 Requires user to be logged in
@login_required
def update_cart_quantity(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')
        action = request.GET.get('action')
        cart = Cart.objects.get(id=cart_id, user=request.user)

        if action == 'plus':
            cart.quantity += 1
        elif action == 'minus' and cart.quantity > 1:
            cart.quantity -= 1
        cart.save()

        total = sum(c.quantity * c.product.discounted_price for c in Cart.objects.filter(user=request.user))
        shipping = 0 if total > 20000 else 350
        grand_total = total + shipping

        return JsonResponse({
            'quantity': cart.quantity,
            'total': total,
            'shipping': shipping,
            'grand_total': grand_total
        })

# 🔒 Requires user to be logged in
@login_required
def remove_cart_item(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')
        cart = Cart.objects.get(id=cart_id, user=request.user)
        cart.delete()

        total = sum(c.quantity * c.product.discounted_price for c in Cart.objects.filter(user=request.user))
        shipping = 0 if total > 20000 else 350
        grand_total = total + shipping

        return JsonResponse({
            'status': 'success',
            'total': total,
            'shipping': shipping,
            'grand_total': grand_total
        })

# 🔒 Requires user to be logged in
@login_required
def checkout(request):
    user = request.user
    add = Costumer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)

    total_amount = 0
    for item in cart_items:
        item.total_price = item.quantity * item.product.discounted_price
        total_amount += item.total_price

    shipping_cost = 0 if total_amount > 20000 else 350
    grand_total = total_amount + shipping_cost

    return render(request, 'app/checkout.html', {
        'add': add,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total
    })

# 🔒 Requires user to be logged in
@login_required
def payment_done(request):
    user = request.user
    cust_id = request.GET.get('custid')
    costumer = Costumer.objects.get(id=cust_id)
    cart_items = Cart.objects.filter(user=user)

    for item in cart_items:
        Order.objects.create(
            user=user,
            costumer=costumer,
            product=item.product,
            quantity=item.quantity
        )
        item.delete()
    return redirect('orders')

# 🔒 Requires user to be logged in
@login_required
def orders(request):
    op = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'app/orders.html', {'orders': op})

@login_required
def buy_now(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        existing_cart_item = Cart.objects.filter(user=request.user, product=product).first()
        
        if not existing_cart_item:
            Cart.objects.create(user=request.user, product=product, quantity=1)
        return redirect('checkout')
    else:
        return redirect('home')



class ProfileView(LoginRequiredMixin,View):
    def get(self, request):
        try:
            profile = Costumer.objects.get(user=request.user)
            form = CustomerProfileForm(instance=profile)
        except Costumer.DoesNotExist:
            form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        try:
            profile = Costumer.objects.get(user=request.user)
            form = CustomerProfileForm(request.POST, instance=profile)
        except Costumer.DoesNotExist:
            form = CustomerProfileForm(request.POST)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your profile has been updated successfully ✅")
            return redirect('profile')

        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

def search_view(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('home')

    results = Product.objects.filter(title__icontains=query)
    exact_match = results.filter(title__iexact=query).first()
    if exact_match and results.count() == 1:
        return redirect('product-detail', pk=exact_match.pk)

    return render(request, 'app/search_results.html', {'query': query, 'results': results})

# 🔒 Requires user to be logged in
@login_required
def address(request):
    add = Costumer.objects.get(user=request.user)
    return render(request, 'app/address.html', {'add': add})

def mobile(request, data=None):
    if data is None:
        mobile = Product.objects.filter(category='M')
    elif data in ['Xiaomi', 'Samsung', 'Apple', 'OPPO', 'Vivo']:
        mobile = Product.objects.filter(category='M', brand=data)
    else:
        mobile = Product.objects.none()
    return render(request, 'app/mobile.html', {'mobiles': mobile})

def laptop(request, data=None):
    if data is None:
        laptops = Product.objects.filter(category='L')
    elif data in ['HP', 'DELL', 'LENOVO']:
        laptops = Product.objects.filter(category='L', brand=data)
    else:
        laptops = Product.objects.none()
    return render(request, 'app/laptop.html', {'laptops': laptops})

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return render(request, 'app/customerregistration.html', {'form': form})
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
        return render(request, 'app/customerregistration.html', {'form': form})

def about(request):
    return render(request, 'app/about.html')

def faqs(request):
    return render(request, 'app/faqs.html')

def careers(request):
    return render(request, 'app/careers.html')

def terms(request):
    return render(request, 'app/terms_and_conditions.html')
