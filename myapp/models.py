from django.db import models
from django.contrib.auth.models import User

from django.utils.timezone import now

from django.conf import settings

# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    instock = models.BooleanField(default=True)
    #file
    picture = models.ImageField(upload_to="product", null=True, blank=True)
    specfile = models.FileField(upload_to="specfile", null=True, blank=True)

class contactList(models.Model):
    topic = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    detail = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return self.topic

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.CharField(max_length=100, default='member')
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Action(models.Model):
    contactList = models.ForeignKey(contactList, on_delete=models.CASCADE)
    actionDetail = models.TextField()

    def __str__(self):
        return self.contactList.topic

class Basket(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="basket",
        verbose_name="User's Basket"
    )
    created_at = models.DateTimeField(default=now, verbose_name="Created At")

    def __str__(self):
        return f"{self.user.username}'s Basket"

    def total_price(self):
        """Calculate the total price of all items in the basket."""
        return sum(item.total_price() for item in self.items.all())

    def total_items(self):
        """Get the total number of items in the basket."""
        return self.items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0


class BasketItem(models.Model):
    basket = models.ForeignKey(
        Basket, 
        on_delete=models.CASCADE, 
        related_name="items",
        verbose_name="Basket"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    added_on = models.DateTimeField(default=now, verbose_name="Added On")

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in {self.basket.user.username}'s basket"

    def total_price(self):
        """Calculate the total price for this basket item."""
        return self.quantity * self.product.price

class CreditCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, blank=False, null=False)
    card_type = models.CharField(max_length=20, choices=[('Visa', 'Visa'), ('MasterCard', 'MasterCard'), ('Amex', 'Amex')], blank=False, null=False)
    expiry_date = models.CharField(max_length=7, blank=False, null=False)  # or use DateField if needed
    cardholder_name = models.CharField(max_length=100, blank=False, null=False)
    cvv = models.CharField(max_length=3, blank=False, null=False, default='000')  # Default value specified

    def __str__(self):
        return f'{self.card_type} ending in {self.card_number[-4:]}'

class Bill(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal')])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Waiting')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Bill {self.id} for {self.user.username}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Bill {self.bill.id}"

    def total_price(self):
        return self.quantity * self.product.price

