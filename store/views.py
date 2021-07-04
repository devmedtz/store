from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import Product, Order, OrderItem, ShippingAddress, Customer
from .utils import cookieCart, cartData


def updateItem(request):
	
	if request.is_ajax():
		productId = request.POST['productId']
		action = request.POST['action']

		customer = request.user.customer
		product = Product.objects.get(id=productId)

		order, created = Order.objects.get_or_create(customer=customer, complete=False)

		orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

		if action == 'add':
			orderItem.quantity = (orderItem.quantity + 1)
		elif action == 'remove':
			orderItem.quantity = (orderItem.quantity - 1)
		orderItem.save()

		if orderItem.quantity <= 0:
			orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def store(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {
		'products':products,
		'cartItems':cartItems
	}
	template_name = 'store/index.html'

	return render(request, template_name, context)


def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items':items,
		'order':order,
		'cartItems':cartItems
	}
	template_name = 'store/cart.html'
	return render(request, template_name , context)


def checkout(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items':items,
		'order':order,
		'cartItems':cartItems
	}
	template_name = 'store/checkout.html'
	return render(request, template_name , context)


def processOrder(request):

	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

	else:
		print('User is not logged in')

		print('COOKIES:', request.COOKIES)

		name = data['form']['name']
		email = data['form']['email']

		cookieData = cookieCart(request)

		items = cookieData['items']

		customer, created = Customer.objects.get_or_create(
			email=email,
		)
		customer.name = name
		customer.save()

		order = Order.objects.create(
			customer=customer, complete=False,
		)

		for item in items:
			product = Product.objects.get(id=item['id'])
			orderItem = OrderItem.objects.create(
				product=product,
				order=order,
				quantity=item['quantity'],
			)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)
