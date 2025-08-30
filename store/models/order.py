from django.db import models
from .product import Product

STATUS_CHOICE = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On the Way','On the Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel')
)

class OrderDetail(models.Model):
    user = models.IntegerField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    qty = models.PositiveIntegerField(default=1)
    price = models.IntegerField()
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,default='Pending',choices=STATUS_CHOICE)