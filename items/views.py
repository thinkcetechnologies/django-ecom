from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order,Address
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from . forms import CheckoutForm,PaymentForm
from django.conf import settings
# Create your views here.
def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid		


class index(ListView):
      model=Item
      template_name='items/index.html'
 


def detail(request,slug):
    product = get_object_or_404(Item, slug=slug)
    context = {
        'product':product
    }
  
    return render(request, 'items/items_details.html',context)

class PaymentView(View):
	def get(self,*args,**kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		 # if the user has supplied a billing address
		if order.billing_address:
		 	context = {
		 		'order':order,
		 		'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
		 	}
		 	return render(self.request, 'items/payment.html',context)
		else:
			# if you are not having a billing address
			messages.warning(self.request, 'You donot have a billing address')
			return redirect("checkout")

	def Post(self,*args,**kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		form = Payment(self.request.POST)	
		 	

class Checkout(LoginRequiredMixin,View):
	def get(self,*args,**kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			form = CheckoutForm()
			context ={
				'form':form,
				'order':order,
			}
			#checking if the user has already provided an address or not
			shipping_address_qs = Address.objects.filter(
				user = self.request.user,
				address_type="S",
				default=True

			)
			if shipping_address_qs.exists():
				context.updated({'default_shipping_address': shipping_address_qs[0]})
			return render(self.request,'items/checkout.html',context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("/")			
					



			if billing_address_qs.exists():
				context.updated({'default_billing_address': billing_address_qs[0]})
			return render(self.request,'items/checkout.html',context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("/")
	def post(self,*args,**kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				use_default_shipping = form.cleaned_data.get('use_default_shipping')
						#if the user select the use_default_shipping
				if use_default_shipping:
					address_qs = Address.objects.filter(
						user = self.request.user,
						address_type ="S",
						default = True

					)	
					if address_qs.exists():
						shipping_address = address_qs[0]
						order.shipping_address = shipping_address
						order.save()
					else:
						messages.info(self.request,"No default shipping address available")	
						return redirect("checkout")
				else:
					# getting the data the user enters
					shipping_address1 = form.cleaned_data.get('shipping_adress')
					shipping_address2= form.cleaned_data.get('shipping_adress2')	
					shipping_country = form.cleaned_data.get('shipping_country')	
					shipping_zip = form.cleaned_data.get('shipping_zip')	

					if is_valid_form([shipping_address1,shipping_country,shipping_zip]):
						shipping_address = Address(
							user = self.request.user,
							street_address = shipping_address1,
							apartment_address = shipping_address2,
							country=shipping_country,
							zipcode = shipping_zip,
							address_type='S'


						)
						shipping_address.save()
						order.shipping_address = shipping_address
						order.save()

					set_default_shipping = form.cleaned_data.get('set_default_shipping')
					if set_default_shipping:
						shipping_address.default = True
						shipping_address.save()	
					else:
						messages.info(self.request,"Please fill in the required shipping address fields")	
				use_default_billing = form.cleaned_data.get('use_default_billing')
				same_billing_address = form.cleaned_data.get('same_billing_address')

				if same_billing_address:
					billing_address = shipping_address
					billing_address.pk = None
					billing_address.save()
					billing_address.address_type='B'
					billing_address.save()	
					order.billing_address = billing_address	
					order.save()

				elif use_default_billing:
					address_qs = Address.objects.filter(
						user = self.request.user,
						address_type ="B",
						default = True

					)	
					if address_qs.exists():
						billing_address = address_qs[0]
						order.billing_address = billing_address
						order.save()
					else:
						messages.info(self.request,"No default billing address available")	
						return redirect("checkout")	
				else:
					billing_address1 = form.cleaned_data.get('billing_adress')
					billing_address2= form.cleaned_data.get('billing_adress2')	
					billing_country = form.cleaned_data.get('billing_country')	
					billing_zip = form.cleaned_data.get('billing_zip')	

					if is_valid_form([billing_address1,billing_country,billing_zip]):
						billing_adress = Address(
							user = self.request.user,
							street_address = billing_address1,
							apartment_address = billing_address2,
							country=billing_country,
							zipcode = billing_zip,
							address_type='B'


						)
						billing_address.save()
						order.billing_address = billing_address
						order.save()

						set_default_billing=form.cleaned_data.get('set_default_billing')
						if set_default_billing:
							billing_address.default = True
							billing_address.save()
					else:
						messages.info(self.request,"Please fill in the required billing address fields")
			payment_option = form.cleaned_data.get('payment_option')

			if payment_option == "S":
				return redirect('stripe')

			elif payment_option == "P":
				pass

				#if the user did not select any payment option
			else:
				messages.info(self.request,"Invalid payment_option")
				return redirect('checkout')

		except ObjectDoesNotExist:
			messages.info(self.request,"You donot have an active order")
			return redirect('order-summary')
 
class OrderSummaryView(LoginRequiredMixin,View):
	def get(self,*args,**kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object':order
			}
			return render(self.request,'items/order_summary.html',context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("/")

		
@login_required
def add_to_cart(request,slug):
	item = get_object_or_404(Item, slug=slug)
	# checking if the user has ordered an item already or now coming to place an order
	order_item, create =OrderItem.objects.get_or_create(
			#getting the item the user has selected or created
			item=item,
			#checking the user who request for the item, if he has already requested or not
			user=request.user,
			ordered=False
		)
	#checking if the user has ordered the item or not
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		#checking if the order item is in the order or not,filter also known as get
		if order.items.filter(item__slug=item.slug).exists():
			#if an item has been added to the cart ,then lets get the qty
			order_item.quantity +=1
			order_item.save()              
			return redirect("order-summary")
		else:
			order.items.add(order_item)
			return redirect("order-summary")	
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user=request.user, ordered_date = ordered_date

		)	
# adding the orders to the items
		order.items.add(order_item)
		return redirect("order-summary")
@login_required
def remove_from_cart(request,slug):
	item = get_object_or_404(Item,slug=slug)
	# if the user has an order in the cart
	#checking if the item has been ordered or not
	order_qs = Order.objects.filter(
		user=request.user,
		ordered = False
		)
	if order_qs.exists(): 
	# get the order
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item = item,
				user = request.user,
				ordered = False

				)[0]
			# if successful removing the item from the cart
			order.items.remove(order_item)
			# deleting it from the order item table
			order_item.delete()
			messages.info(request, "This item was removed from your cart.")
			return redirect("order-summary")
			# if the user hasn't added any item to the cart
		else:
			messages.info(request, "This item was not in your cart.")
			return redirect('detail', slug=slug)		
	else:
		messages.info(request, "You do not have an active order.")
		return redirect('detail',slug=slug)


@login_required
def remove_one_from_cart(request,slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False

	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item = item,
				user = request.user,
				ordered = False



			)[0]
			if order_item.quantity > 1:
				order_item_quantity -=1
				order_item.save()
			else:
				order.items.remove(order_item)

			messages.info(request,"This item was updated in your cart.")
			return redirect("order-summary")

		else:
			messages.info(request,"This item was not in your cart.")
			return redirect('detail',slug=slug)
	else:
		message.info(request,"You do not have an active order")	
		return redirect('detail', slug=slug)	
				



     



