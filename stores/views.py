
from . models import *
from django.contrib import messages
from .forms import CheckoutForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


# Create your views here.

def index(request):
    # sliders
    sliders = Curousel.objects.all()
    # products
    products = Product.objects.all().order_by('-created_at')
    # pagination
    paginator = Paginator(products,4)
    page_number = request.GET.get('page')
    product_list = paginator.get_page(page_number)

    # cart total
    cart_total = CartProduct.objects.all()
    counts = cart_total.count()
   
    context={
        'sliders':sliders,
        'products':products,
        'paginator':product_list,
        'count':counts
    }
    return render(request,'stores/index.html',context)

# search
def search(request):
    thekw = request.GET.get('keyword')
    results = Product.objects.filter(Q(title__icontains=thekw) | Q(description__icontains=thekw))

    context={
        'show':results
    }
    return render(request,'stores/search.html',context)


# single product
def singleproduct(request, slug):
    product = Product.objects.get(slug=slug)

    product.view_count+=1
    product.save()
    context = {
        'product':product
    }
    return render(request,'stores/singleproduct.html',context)

def category(request):
    categorys = Category.objects.all()

    context = {
        'categorys':categorys
    }
    return render(request,'stores/category.html',context)

# add product to cart
def addtocart(request,id):
    # get the product
    cart_product = Product.objects.get(id=id)
    # check if cart exists
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart_item = Cart.objects.get(id=cart_id)
        this_product_in_cart = cart_item.cartproduct_set.filter(product=cart_product)
        # assign cart to user
        if request.user.is_authenticated and request.user.customer:
                cart_item.customer = request.user.customer
                cart_item.save()
        # end
        # checking if item exist in cart
        if this_product_in_cart.exists():
            cartproduct = this_product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.subtotal += cart_product.price
            cartproduct.save()
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request, 'Item increase in cart')
        # new item in cart
        else:
            cartproduct = CartProduct.objects.create(
                cart=cart_item, product=cart_product, rate=cart_product.price, quantity=1, subtotal=cart_product.price)
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request, 'New item added to cart')

    else:
        cart_item = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_item.id
        cartproduct = CartProduct.objects.create(cart=cart_item, product =cart_product, rate = cart_product.price, quantity=1, subtotal=cart_product.price)
        cart_item.total += cart_product.price
        cart_item.save()
        messages.success(request, 'New Item to cart')
    return redirect('index')

# users cart
def myCart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
        # end
    else:
        cart = None
    context = {
        'cart':cart,
    }
    return render(request, 'stores/mycart.html',context)

# manage cart
def manageCart(request,id):
    action = request.GET.get('action')

    cart_obj = CartProduct.objects.get(id=id)
    cart = cart_obj.cart

    if action == 'inc':
        cart_obj.quantity += 1
        cart_obj.subtotal += cart_obj.rate
        cart_obj.save()
        cart.total += cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity increase in cart')

    elif action == 'dcr':
        cart_obj.quantity -= 1
        cart_obj.subtotal -= cart_obj.rate
        cart_obj.save()
        cart.total -= cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity decrease in cart')

        if cart_obj.quantity == 0:
            cart_obj.delete()
    elif action == 'rmv':
        cart.total -= cart_obj.subtotal
        cart.save()
        cart_obj.delete()
        messages.success(request, 'Item remove in cart')

    else:
        pass
    return redirect('myCart')

def emptyCart(request):
    
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
        # end
        cart.cartproduct_set.all().delete()
        cart.total = 0
        cart.save()
        messages.success(request, 'All Item in cart deleted')

    return redirect('myCart')


#  checkout
# @login_required(login_url='/user/login/')
def checkout(request):
    cart_id = request.session.get('cart_id', None)
    cart_obj = Cart.objects.get(id=cart_id)
    form = CheckoutForm()

    # # checkout authentication
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('/user/login?next=/checkout')

    # getting cart
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart_obj.customer = request.user.customer
            cart_obj.save()
        # end
    else:
        cart_obj = None
    
    # form
    if request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.cart = cart_obj
            form.discount = 0
            form.subtotal = cart_obj.total
            form.amount = cart_obj.total
            form.order_status = 'Order Received'
            pay_mth = form.payment_method
            del request.session['cart_id']
            pay_mth = form.payment_method
            form.save()
            order = form.id
            if pay_mth == 'Paystack':
                return redirect('payment', id =order)
            elif pay_mth == 'Payment Transfer':
                return redirect('transfer', id =order)

            messages.success(request, 'Order have been placed successfully')
            return redirect('index')
        else:
            messages.error(request, 'No Order have been placed')
            return redirect('index')

    context = {
        'cart':cart_obj,
        'form':form,
    }
    return render(request, 'stores/checkout.html',context)


# payment on transfer
def transfer(request,id):
    orders = Order.objects.get(id=id)
    context = {
        'order':orders,
    }
    return render(request, 'stores/transfer.html',context)

# paystack
def paymentPage(request,id):
   
    orders = Order.objects.get(id=id)

    context = {
        'order':orders,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY 
    }
    return render(request, 'stores/payment.html',context)


# verify payment
def verify_payment(request: HttpRequest, ref:str ) -> HttpResponse:
    payment = get_object_or_404(Order, ref = ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, 'Verification Successfully')
    else:
        messages.error(request, 'Verification Failed')
    return redirect('/user/profile')