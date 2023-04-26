from django.shortcuts import render, redirect, HttpResponse, reverse
from mainapp.context_processors import subjects, product_types
from django.contrib.auth.models import User
from mainapp.models import Profile
from .models import Product, Cart_Item, Card_Details, Cart, Bank_Account, Item_Bought, Item_Sold
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
# Create your views here.


shipping_charge = 10


def shop_home(request):
    products = Product.objects.all()
    products_sort = dict()
    for subject in subjects:
        products_sort[subject] = Product.objects.filter(product_subject=subject)

    products_sort = dict(sorted(products_sort.items(), key=lambda x: len(x[1]), reverse=True))
    return render(request, 'shop_home.html', {'products':products, 'products_sort':products_sort})




@login_required(login_url='signin')
def shop_cart(request, u_name):
    cart = Cart.objects.get(user=request.user)
    cart_items = Cart_Item.objects.filter(cart=cart, payment_made='no').order_by('-added_at')
    # total_product_count = cart.aggregate(Sum('product__id'))['product__id__sum']
    # total_price = Cart.get_total_price(cart)
    total_product_count = cart_items.count()
    total_price = sum([item.product.product_price for item in cart_items])
    shipping_charge = 10
    bill_amount = total_price + shipping_charge
    card_details = Card_Details.objects.get(user=request.user) if Card_Details.objects.filter(user=request.user).count() > 0 else None

    if request.method == 'POST' and 'delete_from_cart_button' in request.POST and request.user.is_authenticated:
        id = request.POST['cart_id']
        Cart_Item.objects.get(id=id).delete()

    if request.method == 'POST' and 'proceed_to_checkout_button' in request.POST and request.user.is_authenticated:
        user = request.user
        card_holder_name = request.POST['card_holder_name']
        card_number = request.POST['card_number']
        expiration_month = request.POST['expiration_month']
        expiration_year = request.POST['expiration_year']
        cvv = request.POST['cvv']
        Card_Details.objects.create(user=user, card_holder_name=card_holder_name, card_number=card_number, expiration_month=expiration_month, expiration_year=expiration_year, cvv=cvv).save() if Card_Details.objects.filter(user=user).count() < 1 else None
        if Card_Details.objects.filter(user=user).count() > 0:
            card_details = Card_Details.objects.get(user=user)
            card_details.card_holder_name = card_holder_name
            card_details.expiration_month = expiration_month
            card_details.expiration_year = expiration_year
            card_details.cvv = cvv
            card_details.save()
            messages.success(request, "Card details updated Successfully")
        return redirect(reverse('make_payment', args=[cart.id]))

    return render(request, 'shop_cart.html', {'cart_items':cart_items, 'total_product_count':total_product_count, 'card_details':card_details, 'total_price':total_price, 'shipping_charge':shipping_charge, 'bill_amount':bill_amount})





# @login_required(login_url="signin")
def shop_sell(request):
    if request.user.is_authenticated and request.method == 'POST':
        product_seller = request.user
        product_subject = request.POST['product_subject']
        product_type = request.POST['product_type']
        product_name = request.POST['product_name']
        product_price = request.POST['product_price']
        product_details = request.POST['product_details']
        product_poster = request.FILES['product_poster']
        Product(product_seller=product_seller, product_subject=product_subject, product_type=product_type, product_name=product_name, product_price=product_price, product_details=product_details, product_poster=product_poster).save()
    return render(request, 'shop_sell.html', {'subjects':subjects, 'product_types':product_types})




def product_details(request, p_id):
    product = Product.objects.get(id=p_id)
    if request.user.is_authenticated and request.method == 'POST':
        product_quantity = request.POST['product_quantity']
        for i in range(int(product_quantity)):
            Cart_Item(cart=Cart.objects.get(user=request.user) if Cart.objects.filter(user=request.user).count() > 0 else Cart.objects.create(user=request.user), product_seller=product.product_seller, product=product).save()
    return render(request, 'product_details.html', {'product':product})


def make_payment(request, cart_id):
    if User.objects.filter(username='owner').count() < 1:
        User.objects.create_user(username='owner', email='owner@string.com').save()
        Profile.objects.create(user_id=User.objects.get(username='owner'), phone=9000000000, user_type='creator').save()

    cart = Cart.objects.get(id=cart_id)
    cart_items = Cart_Item.objects.filter(cart=cart, payment_made='no')

    owner = User.objects.get(username='owner')

    cash_buyer = Bank_Account.objects.get(user=request.user) if Bank_Account.objects.filter(user=request.user).count() > 0 else Bank_Account.objects.create(user=request.user, cash=1000)
    cash_owner = Bank_Account.objects.get(user=owner) if Bank_Account.objects.filter(user=owner).count() > 0 else Bank_Account.objects.create(user=owner, cash=1000)

    temp_cash = cash_buyer.cash
    for item in cart_items:
        temp_cash -= float(float(item.product.product_price) + float(shipping_charge/len(cart_items)))

    print("Temp Cash -----------------", temp_cash)
    if temp_cash < 0:
        messages.info(request, "You don't have enough Money to perform this Action")
        return redirect('home')


    for item in cart_items:
        Item_Bought(user=request.user, item_bought=item.product, item_price=item.product.product_price).save()
        Item_Sold(user=item.product.product_seller, item_sold=item.product, item_price=item.product.product_price).save()
        cash_buyer.cash -= float(float(item.product.product_price) + float(shipping_charge / len(cart_items)))
        cash_buyer.save()
        cash_seller = Bank_Account.objects.get(user=item.product.product_seller) if Bank_Account.objects.filter(user=item.product.product_seller).count() > 0 else Bank_Account.objects.create(user=item.product.product_seller, cash=1000)
        cash_seller.cash += float(item.product.product_price)*0.90
        cash_seller.save()
        cash_owner.cash += float(float(item.product.product_price)*0.10 + shipping_charge/len(cart_items))
        cash_owner.save()
        item.payment_made = 'yes'
        item.save()
        print("item.payment_made", item.payment_made)

    return render(request, 'make_payment.html')


def bank_account(request, u_name):
    Bank_Account.objects.create(user=request.user, cash=1000) if Bank_Account.objects.filter(user=request.user).count() < 1 else 0
    bank_account = Bank_Account.objects.get(user=request.user)
    return render(request, 'bank_account.html', {'bank_account':bank_account})