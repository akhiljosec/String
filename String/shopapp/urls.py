from django.urls import path
from . import views


urlpatterns = [
    path('', views.shop_home, name='shop_home'),
    path('shop_cart/<str:u_name>', views.shop_cart, name='shop_cart'),
    path('shop_sell/', views.shop_sell, name='shop_sell'),
    path('product_details/<int:p_id>', views.product_details, name='product_details'),
    path('make_payment/<int:cart_id>', views.make_payment, name='make_payment'),
    path('bank_account/<str:u_name>', views.bank_account, name='bank_account'),
]