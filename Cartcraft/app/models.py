from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinValueValidator
import uuid

PAKISTAN_STATES = (
    ('Punjab', 'Punjab'),
    ('Sindh', 'Sindh'),
    ('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
    ('Balochistan', 'Balochistan'),
    ('Gilgit-Baltistan', 'Gilgit-Baltistan'),
    ('Azad Jammu & Kashmir', 'Azad Jammu & Kashmir'),
    ('Islamabad Capital Territory', 'Islamabad Capital Territory'),
)

class Costumer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    zipcode = models.IntegerField()
    state = models.CharField(max_length=50, choices=PAKISTAN_STATES)

    def __str__(self):
        return self.name


CATEGORY_CHOICE = (
    ('M', 'Mobile'),
    ('L', 'Laptop'),
    ('B', 'Bottom Wear'),
    ('U', 'Upper Wear'),
)

class Product(models.Model):
    title = models.CharField(max_length=50)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.CharField(max_length=10000)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICE)
    product_image = models.ImageField(upload_to='productimg')
    
    # Electronics
    ram = models.CharField(max_length=50, blank=True, null=True)
    battery = models.CharField(max_length=50, blank=True, null=True)
    display = models.CharField(max_length=100, blank=True, null=True)
    storage = models.CharField(max_length=100, blank=True, null=True)
    processor = models.CharField(max_length=100, blank=True, null=True)
    
    #Clothes
    size = models.CharField(max_length=20, blank=True, null=True)
    fabric = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    # Availability field
    in_stock = models.BooleanField(default=True)
    
    @property
    def formatted_selling_price(self):
        return f"{self.selling_price:,.0f}"

    @property
    def formatted_discounted_price(self):
        return f"{self.discounted_price:,.0f}"


def __str__(self):
    return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Cart {self.id}"


STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the Way', 'On the Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
)

def generate_order_id():
    return str(uuid.uuid4()).split('-')[0].upper()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    costumer = models.ForeignKey(Costumer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    order_id = models.CharField(max_length=20, default=generate_order_id, unique=True, blank=True)


    def __str__(self):
        return f"Order {self.id} - {self.order_status}"
