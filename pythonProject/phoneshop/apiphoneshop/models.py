from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    Date_of_birth = models.DateField(null=True, blank=True)
    Phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    Address = models.TextField()

class Brand(BaseModel):
    Name = models.CharField(max_length=255)

class Product(BaseModel):
    Name = models.CharField(max_length=255)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    Description = RichTextField()
    TechnicalSpecifications = models.JSONField()

class ListImg(BaseModel):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    TitlePhoto = CloudinaryField('image')

class Variant(BaseModel):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    SKU = models.CharField(max_length=100) #mã sản phẩm
    Memory = models.CharField(max_length=50)
    Color = models.CharField(max_length=50)
    Quantity = models.IntegerField()
    Price = models.FloatField()
    CompareAtPrice = models.FloatField(max_length=50, null=True, blank=True)
    Img = CloudinaryField('image')

class Order(BaseModel):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    Discount = models.ForeignKey('Discount', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    Note = models.TextField(blank=True)
    ShipAddress = models.TextField()
    ShipDate = models.DateTimeField()

class OrderDetail(BaseModel):
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    Variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='order_details')
    Quantity = models.IntegerField()
    Price = models.FloatField()
    Status = models.CharField(max_length=50)

class Comment(BaseModel):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    Variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='comments')
    Comment = models.TextField()
    Star = models.IntegerField()

class Discount(BaseModel):
    Code = models.CharField(max_length=100)
    DiscountPercent = models.FloatField(null=True, blank=True)
    DiscountMoney = models.FloatField(null=True, blank=True)
    StartDate = models.DateField()
    EndDate = models.DateField()
