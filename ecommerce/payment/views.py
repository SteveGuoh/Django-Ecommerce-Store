from django.shortcuts import render

# Create your views here.

from . models import ShippingAddress, Order, OrderItem

from cart.cart import Cart

from django.http import JsonResponse

from django.core.mail import send_mail

from django.conf import settings

def checkout(request):
    
    # Users with account -- Pre-fill the form
    
    if request.user.is_authenticated:
        
        try:
            
            # Authenticated users with shipping information
            
            shipping_address = ShippingAddress.objects.get(user = request.user.id)
            
            context = {'shipping': shipping_address}
    
            return render(request, 'payment/checkout.html', context=context)
        
        except: 
            
            # Authenticated user with no shipping information (Guest users)
            
            return render(request, 'payment/checkout.html')
    
    else: 
        
        return render(request, 'payment/checkout.html')
        


def complete_order(request):
    
    if request.POST.get('action') == 'post':
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        
        # All-in-one user shipping address
        shipping_address = (address1 + '\n' + address2 + '\n' + city + '\n' + state +'\n' + zipcode)
        
        # Shopping cart information
        cart = Cart(request)
        
        # Get the total price of the item
        total_cost = cart.get_total()
         
        '''
            Order Variation
            
            1. Create Order -> Account users WITH + WITHOUT shipping information
            
            2. Create Order -> Guest users without an account
        
        '''
        
        # User logged i
        
        if request.user.is_authenticated:
            
            order = Order.objects.create(full_name = name, email = email, shipping_address = shipping_address, amount_paid = total_cost, user = request.user)
            
            order_id = order.pk
            
            product_list = []
            
            for item in cart:
                
                OrderItem.objects.create(order_id=order_id, product= item['product'], quantity = item['qty'], price = item['price'], user = request.user)
                product_list.append(item['product'])
            
            all_products = product_list
                        
            send_mail('Order received', 'Hi! ' + '\n\n' + 'Thank you for placing your order.' + '\n\n' + 'Please see your order below:' + '\n\n' + str(all_products)
                      + '\n\n' + 'Total paid: $' + str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False,)
                
        else:
            
        # Use guest account
            
            order = Order.objects.create(full_name = name, email = email, shipping_address = shipping_address, amount_paid = total_cost)
            
            order_id = order.pk
            
            product_list = []
            
            for item in cart:
                
                OrderItem.objects.create(order_id=order_id, product= item['product'], quantity = item['qty'], price = item['price'])
                product_list.append(item['product'])
        
        
            # Email order 
            
            all_products = product_list
                        
            send_mail('Order received', 'Hi! ' + '\n\n' + 'Thank you for placing your order' + '\n\n' + 'Please see your order below:' + '\n\n' + str(all_products)
                      + '\n\n' + 'Total paid: $' + str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False,)
        
            
        order_success = True
        
        response = JsonResponse({'success': order_success})
        
        return response



def payment_success(request):
    
    # Clear the shopping cart
    
    for key in list(request.session.keys()):
        
        if key == 'session_key':
            
            del request.session[key]
    
    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    
    return render(request, 'payment/payment-failed.html')