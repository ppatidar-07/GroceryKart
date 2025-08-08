from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from.models.product import Product
from.models.category import Category
from.models.customer import Customer
from.models.cart import Cart
from.models.order import OrderDetail
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def home(request):
    products = None
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        category = Category.get_all_categories()
        customer = Customer.objects.filter(phone=phone)
        totalitem = len(Cart.objects.filter(phone=phone))
        for c in customer:
            name = c.name
            categoryID = request.GET.get('category')
            if categoryID:
                products = Product.get_all_product_by_category_id(categoryID)
            else:
                products = Product.get_all_products()

            data = {
            'name': name,
            'product': products,
            'category': category,
            'totalitem': totalitem
            }
            return render(request, 'home.html', data)
    else:
        return redirect('login')

#..................signup...................................
class Signup(View):
    def get(self,request):
        return render(request, 'signup.html')
    def post(self,request):
        postData = request.POST
        name = postData.get('name')
        phone = postData.get('phone')

        error_message = None

        value = {
            'phone': phone,
            'name': name
        }

        customer = Customer(name=name,
                            phone=phone)

        if (not name):
            error_message = "Name is Required"
        elif not phone:
            error_message = "Mobile number is Required"
        elif len(phone) < 10:
            error_message = "Mobile number must be 10 character long"
        elif customer.isExists():
            error_message = "Mobile number already exists"
        if not error_message:
            messages.success(request, "Congratulations !!, Registered Successfully")
            customer.register()
            return redirect('signup')
        else:
            data = {
                'error': error_message,
                'value': value
            }
            return render(request, 'signup.html', data)

#......................login.......................................
class Login(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        phone = request.POST.get('phone')
        error_message = None
        value = {
            'phone': phone
        }
        customer = Customer.objects.filter(phone=request.POST["phone"])
        if customer:
            request.session['phone']=phone
            return redirect('homepage')
        else:
            error_message = "Mobile number is invalid !!"
            data = {
                'error': error_message,
                'value': value
            }

        return render(request, 'login.html', data)
    
#.......................Product Detail....................
def productdetail(request,pk):
    totalitem = {}
    product = Product.objects.get(pk=pk)
    item_already_in_cart = False
    if request.session.has_key('phone'):
        phone = request.session['phone']
        totalitem = len(Cart.objects.filter(phone=phone))
        item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(phone=phone)).exists()
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.name
        data = {
            'product':product,
            'item_already_in_cart':item_already_in_cart,
            'name':name,
            'totalitem':totalitem
        }
        return render(request,'productdetail.html',data)

#........................logout.......................................
def logout(request):
    if request.session.has_key('phone'):
        del request.session['phone']
        return redirect('login')
    else:
        return redirect('login')

#...............Add to cart...............................
def add_to_cart(request):
    phone = request.session['phone']
    product_id = request.GET.get('prod_id')
    product_name = Product.objects.get(id=product_id)
    product = Product.objects.filter(id=product_id)
    for p in product:
        image=p.image
        price=p.price
        Cart(phone=phone,product=product_name,image=image,price=price).save()
        return redirect(f"/product-detail/{product_id}")

#.......................Cart...................................
def show_cart(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        totalitem = len(Cart.objects.filter(phone=phone))

        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            cart = Cart.objects.filter(phone=phone)
            data = {
                'name':name,
                'totalitem':totalitem,
                'cart':cart
            }
            if cart:
                return render(request,'show_cart.html',data)
            else:
                return render(request, 'empty_cart.html')

#............plus cart.....................
def plus_cart(request):
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity += 1
        cart.save()
        data = {
            'quantity': cart.quantity
        }
        return JsonResponse(data)

#........................minus cart.........................
def minus_cart(request):
    if request.session.has_key('phone'):
        phone = request.session['phone']
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity -= 1
        cart.save()
        data = {
            'quantity': cart.quantity
        }
        return JsonResponse(data)

#...........................remove cart.......................
def remove_cart(request):
    if request.session.has_key('phone'):
        phone = request.session['phone']
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.delete()
        return JsonResponse()

#......................checkout........................
def checkout(request):
    totalitem =0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        name = request.POST.get('name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        cart_product = Cart.objects.filter(phone=phone)
        for c in cart_product:
            qty = c.quantity
            price = c.price
            product_name = c.product
            image = c.image

            OrderDetail(user=phone,product_name=product_name,image=image,qty=qty,price=price).save()
        cart_product.delete()
        totalitem = len(Cart.objects.filter(phone=phone))

        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name

        data = {
            'name':name,
            'totalitem':totalitem
        }
        return render(request,'empty_cart.html',data)

    else:
        return redirect('login')

#......................order.........................
def order(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        order = OrderDetail.objects.filter(user=phone)
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            order = OrderDetail.objects.filter(user=phone)
            data = {
                'order': order,
                'name': name,
                'totalitem': totalitem
            }


            if order:
                return render(request, 'order.html', data)
            else:
                return render(request, 'emptyorder.html', data)

    else:
        return redirect('login')

#...................search............................
def search(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        query = request.GET.get('query')
        search = Product.objects.filter(name__contains=query)
        category = Category.get_all_categories()
        order = OrderDetail.objects.filter(user=phone)
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
        data={
                'name':name,
                'totalitem':totalitem,
                'search':search,
                'category':category,
                'query':query
            }
        return render(request, 'search.html',data)
    else:
        return render('login')