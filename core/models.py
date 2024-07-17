import uuid
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


LABEL_CHOICES = (
    ('P', 'open'),
    ('S', 'sold'),
    ('R', 'rented'),
)

class Category(models.Model):
    title = models.CharField(max_length=200)
    category_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    slug = models.SlugField(default= None)
    featured_book = models.OneToOneField('Book', on_delete=models.CASCADE, blank=True, null=True, related_name='featured_book')
    icon = models.CharField(max_length=100, default=None, blank = True, null=True)

    def __str__(self):
        return self.title


#book/book_pk/reviews

class Review(models.Model):
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name = "reviews")
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default="description")
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.description

    

class Book(models.Model):
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='pics', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_books')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='books')
    status = models.CharField(choices=LABEL_CHOICES, max_length=1)
    pdf = models.FileField(upload_to='pdfs', blank=True, null=True)
    slug = models.SlugField(default=None)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    is_purchase = models.BooleanField(default=False)
    is_rentall = models.BooleanField(default=False)
    if is_rentall:
        access_time = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title
    

class BookImage(models.Model):
    book = models.ForeignKey(Book,  on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pics', default="", null=True, blank=True)

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return str(self.id)
    

class Cartitems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True, related_name='cartitems')
    quantity = models.IntegerField(default=0)
    
 
class Profile(models.Model):
    name = models.CharField(max_length=30)
    bio = models.TextField()
    picture = models.ImageField(upload_to = 'img', blank=True, null=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    
    
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    pending_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='PAYMENT_STATUS_PENDING')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.pending_status

    @property
    def total_price(self):
        items = self.items.all()
        total = sum([item.quantity * item.book.purchase_price for item in items])
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name = "items")
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    

    def __str__(self):
        return self.book.title
