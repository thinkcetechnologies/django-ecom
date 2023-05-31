from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.
CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sport wear'),
    ('OW','Outwear')
    
    
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D', 'danger'),
)

ADDRESS_CHOICES = (
    ('B','Billing'),
    ('s','Shipping'),
)


class Item(models.Model):
    title=models.CharField(max_length=100)
    price=models.FloatField()
    discount_price=models.FloatField(blank=True,null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label = models.CharField(choices=LABEL_CHOICES,max_length=1)
    slug=models.SlugField(default='',unique=True)
    description=models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

        #making the items clickable
    def get_absolute_url(self):
        return reverse('detail',kwargs={
            'slug':self.slug
        }) 

class OrderItem(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    # checking if the item is ordered or not 
    ordered = models.BooleanField(default=False)
    item= models.ForeignKey(Item, on_delete=models.CASCADE)  
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return f"(self.quantity) quantities of(self.item.title)" 


    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_absolute_url(self):
        return reverse('detail',kwargs={
            'slug':self.item.slug
        }) 

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()    



class Order(models.Model):
     user = models.ForeignKey(User,on_delete=models.CASCADE)   
     ref_code = models.CharField(max_length=20,blank=True,null=True)
     #manytomany because the user can select more than one item
     items = models.ManyToManyField(OrderItem)
     start_date = models.DateTimeField(auto_now_add=True)
     ordered_date = models.DateTimeField()
     #Tracking if the item is been ordered or not
     #default is false because the user hasn't ordered the item
     ordered = models.BooleanField(default=False)
     shipping_address = models.ForeignKey('Address',related_name='shipping_address', on_delete=models.SET_NULL,blank=True,null=True)
     billing_address = models.ForeignKey('Address',related_name='billing_address', on_delete=models.SET_NULL,blank=True,null=True) 
     payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
     coupon = models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)
     being_delivered = models.BooleanField(default=False)
     received = models.BooleanField(default=False)
     refund_requested = models.BooleanField(default=False)
     refund_granted=models.BooleanField(default=False)

     def __str__(self):
        return self.user.username
     def get_total(self):
         total = 0
         for order_item in self.items.all():
             total  += order_item.get_final_price()  
         return total           

class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zipcode = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    #if you have shopped with us before your details will be saved,so the default is going to input your credentials if set to true
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
   
        class Meta:
            verbose_name_plural= 'Addresses'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        #the pk is the ID
        return f"{self.pk}"          





