from django.db import models
from mainapp.context_processors import subjects, product_types
from django.contrib.auth.models import User
from django.db.models import Sum
# Create your models here.


string_profit = float()

PRODUCT_TYPE = []

for product_type in product_types:
    PRODUCT_TYPE.append((f'{product_type}', f'{product_type}'))

PRODUCT_TYPE = tuple(PRODUCT_TYPE)


SUBJECTS = []

for subject in subjects:
    SUBJECTS.append((f'{subject}', f'{subject}'))

SUBJECTS = tuple(SUBJECTS)




class Product(models.Model):
    product_seller = models.ForeignKey(User, on_delete=models.CASCADE)
    product_subject = models.CharField(max_length=100, choices=SUBJECTS, null=True, blank=True)
    product_type = models.CharField(max_length=100, choices=PRODUCT_TYPE, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=20, decimal_places=2)
    product_details = models.TextField(blank=True)
    product_poster = models.ImageField(upload_to="product_poster")
    product_created = models.DateTimeField(auto_now_add=True)
    product_availability = models.BooleanField(default=True)

    class Meta:
        ordering = ('product_name',)
        index_together = (('id', 'product_name'),)

    def __str__(self):
        return self.product_name



class Cart(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)



class Cart_Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_seller = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_made = models.CharField(max_length=10, default='no')



class Card_Details(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    card_holder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiration_month = models.CharField(max_length=2)
    expiration_year = models.CharField(max_length=4)
    cvv = models.CharField(max_length=3)



class Item_Bought(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_bought = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_price = models.FloatField()


class Item_Sold(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_sold = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_price = models.FloatField()


class Bank_Account(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    cash = models.FloatField()

