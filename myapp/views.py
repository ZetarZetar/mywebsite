from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse
from .models import *
# from songline import Sendline
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

from django.utils import timezone
from decimal import Decimal
from django.db.models import Count

# Create your views here.
def home(request):
    allproduct = Product.objects.all()
    product_per_page = 3
    paginator = Paginator(allproduct, product_per_page)
    page = request.GET.get('page')
    allproduct = paginator.get_page(page)

    context = {'allproduct' : allproduct}

    allrow = []
    row = []
    for i,p in enumerate(allproduct):
        if i%3 == 0:
            if i != 0:
                allrow.append(row)
            row = []
            row.append(p)
        else:
            row.append(p)
    allrow.append(row)
    context['allrow'] = allrow

    return render(request,'myapp/home.html', context)

def aboutUs(request):
    return render(request, 'myapp/aboutus.html')

def contact(request):
    context = {}
    if request.method == 'POST':
        data = request.POST.copy()
        topic = data.get('topic')
        email = data.get('email')
        detail = data.get('detail')

        if (topic =='' or email == '' or detail == ''):
            context['message']= 'Please, fill in all contact information'
            return render(request,'myapp/contact.html', context)

        newRecord = contactList()
        newRecord.topic = topic
        newRecord.email = email
        newRecord.detail = detail
        newRecord.save()

        context['message'] = 'The message has been received'
    return render(request, 'myapp/contact.html', context)
    # token = 'rH7moNvRhof84P5rfQNLDR9RpvTD6L91afitghPY59r'
    # context = {} #message to notify
    # return render(request, 'myapp/contact.html', context)
    # if request.method == 'POST':
    #     data = request.POST.copy()
    #     topic = data.get('topic')
    #     email = data.get('email')
    #     detail = data.get('detail')

    #     if(topic =='' or email =='' or detail ==''):
    #         context['message']= 'Please, fill in all contact information'
    #         return render(request, 'myapp/contact.html', context)

    #     newRecord = contactList() #create object
    #     newRecord.topic = topic
    #     newRecord.email = email
    #     newRecord.detail = detail
    #     newRecord.save()

    #     context['message'] = 'The message has been received'

    #     m = Sendline(token)
    #     m.sendtext('\ntopic:{0}\n email:{1}\n detail:{2}'.format(topic, email, detail))

def userLogin(request):
    context = {}

    if request.method == 'POST':
        data = request.POST.copy()
        username = data.get('username')
        password = data.get('password')

        try:
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home-page')
        except:
            context['message']="username or password is incorrect."   
             
    return render(request, 'myapp/login.html', context)

def userLogout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login')
def showContact(request):
    allcontact = contactList.objects.all()
    context = {'contact': allcontact}
    return render(request, 'myapp/showcontact.html', context)

def userRegist(request):
    context={}

    if request.method =='POST':
        data = request.POST.copy()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        repassword = data.get('repassword')

        try:
            User.objects.get(username=username)
            context['message'] = "Username duplicate"

        except:
            newuser = User()
            newuser.username = username
            newuser.first_name = firstname
            newuser.last_name = lastname
            newuser.email = email

            if(password == repassword):
                newuser.set_password(password)
                newuser.save()
                newprofile = Profile()
                newprofile.user = User.objects.get(username=username)
                newprofile.save()
                context['message'] = "register complete."
            else:
                context['message'] = "password or re-password is incorrect."
    return render(request, 'myapp/register.html', context)

def userProfile(request):
    context={}
    userprofile = Profile.objects.get(user=request.user)
    context['profile']=userprofile
    return render(request,'myapp/profile.html',context)

def editProfile(request):
    context={}
    if request.method == 'POST':
        data = request.POST.copy()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        current_user = User.objects.get(id=request.user.id)
        current_user.first_name = firstname
        current_user.last_name = lastname
        current_user.username = username
        current_user.email = email
        current_user.set_password(password)
        current_user.save()

        try:
            user = authenticate(username=current_user.username,password=current_user.password)
            login(request,user)
            return redirect('home-page')
        
        except:
            context['message'] = "edit profile fail"
    return render(request, 'myapp/editprofile.html')

def actionPage(request, cid):
    #cid = contactList id
    context ={}
    contact = contactList.objects.get(id=cid)
    context['contact'] = contact

    try:
        action = Action.objects.get(contactList=contact)
        context['action'] = action
    except:
        pass

    if request.method == 'POST':
        data = request.POST.copy()
        actiondetail = data.get('actiondetail')

        if 'save' in data:
            try:
                check = Action.objects.get(contactList=contact)
                check.actionDetail = actiondetail
                check.save()
                context['action'] = check
            except:
                new= Action()
                new.contactList = contact
                new.actionDetail = actiondetail
                new.save()
        elif 'delete' in data:
            try:
                contact.delete()
                return redirect('showcontact-page')
            except:
                pass
        elif 'complete' in data:
            contact.complete = True
            contact.save()
            return redirect('showcontact-page')
    return render(request,'myapp/action.html',context)


def addProduct(request):
    if request.method == 'POST':
        data= request.POST.copy()
        title = data.get('title')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        instock = data.get('instock')

        new = Product()
        new.title = title
        new.description = description
        new.price = price
        new.quantity = quantity

        if instock == "instock":
            new.instock = True
        else:
            new.instock = False
        
        if 'picture' in request.FILES:
            file_image = request.FILES['picture']
            file_image_name = file_image.name.replace(' ','')

            fs = FileSystemStorage(location='media/product')
            filename = fs.save(file_image_name, file_image)
            upload_file_url = fs.url(filename)
            print('Picture url:', upload_file_url)
            new.picture = 'product' + upload_file_url[6:]

        if 'specfile' in request.FILES:
            file_specfile = request.FILES['specfile']
            file_specfile_name = file_specfile.name.replace(' ','')

            fs = FileSystemStorage(location='media/specfile')
            upload_file_url = fs.url(filename)
            print('Specfile url: ', upload_file_url)
            new.specfile = 'specfile' + upload_file_url[6:]

        new.save()
    
    return render(request, 'myapp/addproduct.html')


def handler404(request, exception):
    return render(request, 'myapp/404errorPage.html')

def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product}
    return render(request, 'myapp/product_detail.html', context)

def add_to_basket(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Validate quantity
    if quantity > product.quantity:
        messages.error(request, f"Requested quantity exceeds available stock for {product.title}.")
        return redirect('product-detail', product_id=product.id)
    
    basket, created = Basket.objects.get_or_create(
        user=request.user,
        defaults={'created_at': timezone.now()}
    )

    duplicate_baskets = Basket.objects.filter(user=request.user).exclude(id=basket.id)
    duplicate_baskets.delete()

    basket_item, item_created = BasketItem.objects.get_or_create(
        basket=basket,
        product=product,
        defaults={'quantity': quantity, 'added_on': timezone.now()}
    )

    if not item_created:
        if basket_item.quantity + quantity > product.quantity:
            messages.error(request, "Cannot add more than the available stock.")
            return redirect('product-detail', product_id=product.id)
        
        basket_item.quantity += quantity
        basket_item.save()

    return redirect('home-page')


def delete_basket_item(request, item_id):
    # Retrieve the basket item or return a 404 error if it doesn't exist
    item = get_object_or_404(BasketItem, id=item_id, basket__user=request.user)
    item.delete()  # Delete the item from the basket

    return redirect('view-basket')  # Redirect to the basket view

def update_basket_item(request, item_id):
    # Retrieve the basket item or return a 404 error if it doesn't exist
    item = get_object_or_404(BasketItem, id=item_id, basket__user=request.user)
    new_quantity = int(request.POST.get('quantity', 1))  # Get the new quantity from the POST data
    
    if new_quantity > 0:
        item.quantity = new_quantity  # Update the quantity
        item.save()  # Save the changes to the item
    else:
        item.delete()  # If quantity is zero, delete the item

    return redirect('view-basket')  # Redirect to the basket view

def view_basket(request):
    # Same logic as before for viewing the basket
    items = []
    total_price = Decimal('0.00')
    discount_amount = Decimal('0.00')
    discounted_total_price = Decimal('0.00')
    discount_rate = 0
    saved_credit_cards = []

    try:
        basket = Basket.objects.get(user=request.user)
        items = basket.items.all()  # Retrieve all the items in the user's basket
        total_price = sum(item.total_price() for item in items)

        usertype = request.user.profile.usertype
        if usertype == 'VVIP':
            discount_rate = 15
        elif usertype == 'VIP':
            discount_rate = 10
        elif usertype == 'member':
            discount_rate = 5

        discount_amount = total_price * Decimal(discount_rate / 100)
        discounted_total_price = total_price - discount_amount

        saved_credit_cards = CreditCard.objects.filter(user=request.user)

    except Basket.DoesNotExist:
        pass

    context = {
        'items': items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'discount_rate': discount_rate,
        'discounted_total_price': discounted_total_price,
        'credit_cards': saved_credit_cards,
    }

    return render(request, 'myapp/basket.html', context)

def add_credit_card(request):
    if request.method == 'POST':
        cardholder_name = request.POST.get('cardholder_name')
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        CreditCard.objects.create(
            user = request.user,
            cardholder_name=cardholder_name,
            card_number=card_number,
            expiry_date = expiry_date,
            cvv = cvv
        )

        return redirect('select_credit_card')
    
    return render(request, 'myapp/add_credit_card.html')

def select_credit_card(request):
    credit_cards = CreditCard.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_card_id = request.POST.get('selected_card')
        request.session['select_card_id'] = selected_card_id
        return redirect('confirm_payment')

    context = {
        'credit_cards': credit_cards
    }

    return render(request, 'myapp/select_credit_card.html', context)

def update_credit_card(request, card_id):
    card = get_object_or_404(CreditCard, id=card_id, user=request.user)
    if request.method == 'POST':
        card.cardholder_name = request.POST.get('cardholder_name')
        card.card_number = request.POST.get('card_number')
        card.expiry_date = request.POST.get('expiry_date')
        card.cvv = request.POST.get('cvv')
        card.save()

        return redirect('view-basket')

    return render(request, 'myapp/update_credit_card.html', {'card': card})

def delete_credit_card(request, card_id):
    card = get_object_or_404(CreditCard, id=card_id, user=request.user)
    card.delete()

    return redirect('select_credit_card')

def confirm_payment(request):
    if request.method == 'POST':
        try:
            basket = Basket.objects.get(user=request.user)
            items = basket.items.all()
            total_price = sum(item.total_price for item in items)
        except Basket.DoesNotExist:
            total_price = Decimal('0.00')

        discount_rate = 0
        usertype = request.user.profile.usertype

        if usertype == 'VVIP':
            discount_rate = 15
        elif usertype == 'VIP':
            discount_rate = 10
        elif usertype == 'member':
            disoucnt_rate = 5
        
        discount_amount = total_price * Decimal(discount_rate / 100)
        discounted_total_price = total_price - discount_amount

        payment_method = request.POST.get('payment_method')

        bill = Bill.objects.create(
            user = request.user,
            total_price = total_price,
            discount_amount = discount_amount,
            discounted_total_price = discounted_total_price,
            payment_method = payment_method,
            status = 'Waiting'
        )

        if payment_method == 'credit_card':
            selected_card_id = request.POST.get('selected_card_id')
            if selected_card_id:
                credit_card = get_object_or_404(CreditCard, id=select_credit_card, user=request.user)
                bill.credit_card = credit_card
                bill.save()

            for item in items:
                BillItem.objects.create(
                    bill = bill,
                    product = item.product,
                    quantity = item.quantity,
                    total_price = item.total_price
                )

            Basket.objects.filter(user=request.user).delete()

            return redirect('all_bills')

def all_bills(request):
    user_bills = Bill.objects.filter(user=request.user).order_by('-date')

    paginator = Paginator(user_bills, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bills': page_obj,
    }

    return render(request, 'myapp/all_bills.html', context)
